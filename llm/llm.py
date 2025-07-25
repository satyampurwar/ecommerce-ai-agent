"""Helper functions for interacting with LLM providers."""

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    INTENT_CLASSIFIER,
    HF_INTENT_MODEL,
    HUGGINGFACE_API_TOKEN,
)
from openai import OpenAI
from transformers import pipeline
from huggingface_hub import login

def openai_chat_completion(
    messages,
    model: str = OPENAI_MODEL_NAME,
    temperature: float = OPENAI_TEMPERATURE,
    max_tokens: int = OPENAI_MAX_TOKENS,
):
    """Call OpenAI's chat completion API.

    Parameters
    ----------
    messages : list[dict]
        Sequence of ``{"role": str, "content": str}`` chat messages.
    model : str, optional
        Model name to use.
    temperature : float, optional
        Sampling temperature.
    max_tokens : int, optional
        Maximum tokens to generate.

    Returns
    -------
    str
        Content of the first completion choice.
    """
    # Basic wrapper around the OpenAI API
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

# ---- Intent Classifier ----

_hf_classifier = None

def _openai_classify_intent(query: str) -> str:
    """Classify intent using OpenAI."""

    prompt = [
        {"role": "system", "content": "You are a helpful intent classifier."},
        {"role": "user", "content":
            "Classify the user's query into one of these intents: faq, order_status, refund_status, review, order_details. "
            "Respond with only the intent word, nothing else. "
            f"Here is the query: {query}"}
    ]
    resp = openai_chat_completion(prompt)
    return resp.strip().lower()


def _hf_classify_intent(query: str) -> str:
    """Classify intent using a HuggingFace zero-shot model."""

    global _hf_classifier
    if _hf_classifier is None:
        if HUGGINGFACE_API_TOKEN:
            login(HUGGINGFACE_API_TOKEN, add_to_git_credential=True)
        _hf_classifier = pipeline(
            "zero-shot-classification",
            model=HF_INTENT_MODEL,
            device=-1,
        )
    candidate_intents = [
        "faq",
        "order_status",
        "refund_status",
        "review",
        "order_details",
    ]
    result = _hf_classifier(query, candidate_labels=candidate_intents)
    return result["labels"][0].lower()


def classify_intent(query: str) -> str:
    """Public helper that selects the configured intent classifier.

    Parameters
    ----------
    query : str
        User input to classify.

    Returns
    -------
    str
        Intent label such as ``faq`` or ``order_status``.
    """
    provider = INTENT_CLASSIFIER.lower()
    if provider == "huggingface":
        intent = _hf_classify_intent(query)
    else:
        intent = _openai_classify_intent(query)

    allowed = {"faq", "order_status", "refund_status", "review", "order_details"}
    if intent not in allowed:
        if any(word in query.lower() for word in {"detail", "item"}):
            intent = "order_details"
        elif "order" in query.lower():
            intent = "order_status"
        else:
            intent = "faq"
    return intent

# ---- Rephrase Utility ----

def rephrase_text(text: str) -> str:
    """Use OpenAI to make text sound friendly and natural.

    Parameters
    ----------
    text : str
        Text to rephrase.

    Returns
    -------
    str
        Rephrased version of ``text``.
    """
    prompt = [
        {
            "role": "system",
            "content": (
                "You rephrase agent answers to sound natural, easy to read, "
                "and friendly for end users."
            ),
        },
        {
            "role": "user",
            "content": f"Please rephrase the following text:\n{text}",
        },
    ]
    return openai_chat_completion(prompt)

# ---- General-purpose Chat ----

def chat_completion(query, **kwargs):
    """Convenience wrapper around :func:`openai_chat_completion`.

    Parameters
    ----------
    query : str
        Prompt for the model.
    **kwargs : Any
        Additional arguments passed to :func:`openai_chat_completion`.

    Returns
    -------
    str
        Model response.
    """
    messages = [{"role": "user", "content": query}]
    return openai_chat_completion(messages, **kwargs)

# ---- Quick test ----
if __name__ == "__main__":
    sample = "What is the refund policy for delayed orders?"
    print("Intent:", classify_intent(sample))
    print("Chat:", chat_completion("Tell me about your refund policy."))

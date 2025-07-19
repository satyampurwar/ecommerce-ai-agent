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
from observability import (
    get_langfuse,
    current_trace_id,
    register_prompt,
)

def openai_chat_completion(
    messages,
    model: str = OPENAI_MODEL_NAME,
    temperature: float = OPENAI_TEMPERATURE,
    max_tokens: int = OPENAI_MAX_TOKENS,
):
    """
    Calls OpenAI ChatCompletion API and returns the output text.
    messages: List of dicts with 'role' and 'content'.
    """
    # Basic wrapper around the OpenAI API
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set.")

    lf = get_langfuse()
    generation = None
    if lf:
        generation = lf.generation(
            trace_id=current_trace_id(),
            name="openai_chat_completion",
            input={"messages": messages},
            model=model,
            metadata={"temperature": temperature, "max_tokens": max_tokens},
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    output_text = response.choices[0].message.content.strip()
    if generation:
        generation.end(output=output_text)
    return output_text

# ---- Intent Classifier ----

_hf_classifier = None

def _openai_classify_intent(query: str) -> str:
    prompt = [
        {"role": "system", "content": "You are a helpful intent classifier."},
        {
            "role": "user",
            "content": (
                "Classify the user's query into one of these intents: faq, order_status, refund_status, review, order_details. "
                "Respond with only the intent word, nothing else. "
                f"Here is the query: {query}"
            ),
        },
    ]
    register_prompt("intent_classifier_prompt", str(prompt))
    resp = openai_chat_completion(prompt)
    return resp.strip().lower()


def _hf_classify_intent(query: str) -> str:
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
    """Classify the intent of the user's query using the configured provider."""
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
    """Rephrase text to be clear and conversational using OpenAI."""
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
    register_prompt("rephrase_prompt", str(prompt))
    return openai_chat_completion(prompt)

# ---- General-purpose Chat ----

def chat_completion(query, **kwargs):
    """
    Generic chat completion utility.
    """
    messages = [{"role": "user", "content": query}]
    register_prompt("chat_prompt", str(messages))
    return openai_chat_completion(messages, **kwargs)

# ---- Quick test ----
if __name__ == "__main__":
    sample = "What is the refund policy for delayed orders?"
    print("Intent:", classify_intent(sample))
    print("Chat:", chat_completion("Tell me about your refund policy."))

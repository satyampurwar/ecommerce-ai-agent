from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    HUGGINGFACE_API_TOKEN,
    HUGGINGFACE_MODEL_NAME,
    LLM_PROVIDER,
)
from openai import OpenAI
import requests

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
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


def huggingface_chat_completion(
    messages,
    model: str = HUGGINGFACE_MODEL_NAME,
    temperature: float = OPENAI_TEMPERATURE,
    max_tokens: int = OPENAI_MAX_TOKENS,
):
    """Call Hugging Face Inference API and return the generated text."""
    if not HUGGINGFACE_API_TOKEN:
        raise RuntimeError("HUGGINGFACE_API_TOKEN not set.")
    api_url = f"https://api-inference.huggingface.co/models/{model.strip()}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    # Simple prompt concatenation for single-turn chat
    prompt = "\n".join(m["content"] for m in messages)
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": temperature, "max_new_tokens": max_tokens},
    }
    resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        if resp.status_code == 404:
            raise RuntimeError(
                f"Model '{model}' not found or unavailable on Hugging Face. "
                "Check HUGGINGFACE_MODEL_NAME or that you have access to the model."
            ) from e
        raise
    data = resp.json()
    if isinstance(data, dict) and "generated_text" in data:
        text = data["generated_text"]
    elif isinstance(data, list) and data and "generated_text" in data[0]:
        text = data[0]["generated_text"]
    else:
        raise RuntimeError(f"HuggingFace API error: {data}")
    return text.strip()

# ---- Intent Classifier ----

def classify_intent(query, provider: str = LLM_PROVIDER):
    """
    Classify the intent of the user's query.
    Returns one of: 'faq', 'order_status', 'refund_status', 'review',
    'order_details'.
    """
    prompt = [
        {"role": "system", "content": "You are a helpful intent classifier."},
        {"role": "user", "content":
            "Classify the user's query into one of these intents: faq, order_status, refund_status, review, order_details. "
            "Respond with only the intent word, nothing else. "
            f"Here is the query: {query}"}
    ]
    resp = chat_completion(prompt, provider=provider)
    intent = resp.strip().lower()
    allowed = {"faq", "order_status", "refund_status", "review", "order_details"}
    # Fallback logic (in case LLM is uncertain)
    if intent not in allowed:
        if any(word in query.lower() for word in {"detail", "item"}):
            intent = "order_details"
        elif "order" in query.lower():
            intent = "order_status"
        else:
            intent = "faq"
    return intent

# ---- General-purpose Chat ----

def chat_completion(query, provider: str = LLM_PROVIDER, **kwargs):
    """Generic chat completion utility supporting multiple providers."""
    if isinstance(query, str):
        messages = [{"role": "user", "content": query}]
    else:
        messages = query

    provider = provider.lower()
    if provider == "openai":
        return openai_chat_completion(messages, **kwargs)
    elif provider in {"hf", "huggingface"}:
        return huggingface_chat_completion(messages, **kwargs)
    else:
        raise ValueError(f"Unknown provider '{provider}'")

# ---- Quick test ----
if __name__ == "__main__":
    sample = "What is the refund policy for delayed orders?"
    print("Intent:", classify_intent(sample))
    print("Chat:", chat_completion("Tell me about your refund policy."))

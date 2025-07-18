from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
)
from openai import OpenAI

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

# ---- Intent Classifier ----

def classify_intent(query):
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
    resp = openai_chat_completion(prompt)
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

def chat_completion(query, **kwargs):
    """
    Generic chat completion utility.
    """
    messages = [{"role": "user", "content": query}]
    return openai_chat_completion(messages, **kwargs)

# ---- Quick test ----
if __name__ == "__main__":
    sample = "What is the refund policy for delayed orders?"
    print("Intent:", classify_intent(sample))
    print("Chat:", chat_completion("Tell me about your refund policy."))
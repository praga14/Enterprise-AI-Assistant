import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "openai/gpt-oss-20b"


def generate_answer(
    question: str,
    context: str,
    chat_history: str = "",
) -> str:

    prompt = f"""
You are an Enterprise AI Assistant.

Your job is to answer the user's enterprise knowledge question
using ONLY the information provided in the DOCUMENT CONTEXT.

IMPORTANT GROUNDING RULES:

1. Use the DOCUMENT CONTEXT as the primary and authoritative source.
2. Do NOT invent, assume, or guess enterprise facts.
3. Do NOT use general world knowledge to fill missing enterprise information.
4. If the answer is not supported by the DOCUMENT CONTEXT, say exactly:
   "I don't have enough information in the provided documents."
5. Do not treat conversation history as a source of enterprise facts.
6. Conversation history may only be used to understand references such as:
   "that", "it", "the previous policy", or follow-up questions.
7. If the user asks for information about a person, role, permission,
   document, policy, application, or company process, only state it if
   supported by the DOCUMENT CONTEXT.
8. Do not combine unrelated pieces of information to create a conclusion
   that the documents do not explicitly support.
9. When multiple documents support the answer, combine their information
   carefully.
10. If the documents contain conflicting information, clearly mention
    the conflict instead of choosing one without evidence.
11. Do not mention retrieval, embeddings, similarity scores, chunks,
    vector databases, or internal implementation details.
12. Answer naturally and clearly.
13. Do not say "according to the context" or "based on the context".
14. If the user asks a general conversational question rather than an
    enterprise knowledge question, answer naturally.

DOCUMENT CONTEXT:
{context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION:
{question}

ANSWER:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()



def generate_general_answer(
    question: str,
    chat_history: str = "",
) -> str:

    prompt = f"""
You are an Enterprise AI Assistant.

The user is having a normal conversation.

Answer naturally and helpfully.

Rules:
1. Be concise.
2. Be friendly.
3. Do not invent enterprise data.
4. Do not claim to have performed database operations.
5. If the user asks an enterprise-specific question, that question
   should normally be handled by the enterprise intelligence system.
6. Use conversation history when relevant.

Conversation history:
{chat_history}

User:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def generate_chat_history_answer(
    question: str,
    chat_history: str,
) -> str:
    prompt = f"""
You are an Enterprise AI Assistant.

The user is asking about their previous conversations with you.

Use ONLY the provided conversation history to answer.

Rules:
1. Do not invent previous conversations.
2. Do not claim information was discussed if it is not present.
3. If the user asks for their previous question, identify the most recent
   relevant user question from the history.
4. If the user asks what was discussed, summarize the relevant discussion.
5. If the user asks about a specific topic or person, search the history
   for messages related to that topic.
6. If there is no relevant history, clearly say that no relevant previous
   conversation was found.
7. Keep the answer natural and easy to understand.
8. Do not expose internal database details unless they appear naturally
   in the conversation history.

Previous conversation history:
{chat_history}

Current user question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
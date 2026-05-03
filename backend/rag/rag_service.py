import os
import logging
from typing import List, Tuple
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "../data/nutrition_knowledge.txt"
)

def get_embeddings():
    from langchain_community.embeddings import FakeEmbeddings
    return FakeEmbeddings(size=384)

def build_vectorstore():
    from langchain_community.vectorstores import FAISS
    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = build_vectorstore()
    return _vectorstore

SYSTEM_PROMPT = """You are NutriGen AI, an expert nutritionist and diet advisor specializing in Indian and Bengali cuisine as well as global nutrition.

Use the following context from our nutrition knowledge base to answer the question. If the context doesn't contain the answer, use your general nutrition knowledge but make it clear.

Context:
{context}

Guidelines:
- Give specific, actionable advice
- Reference Indian/Bengali foods when relevant
- Include calorie/nutrient information when helpful
- Be encouraging and supportive

Chat History:
{chat_history}

Question: {question}

Answer:"""

def chat_with_rag(message: str, conversation_history: List[dict] = []) -> Tuple[str, List[str]]:
    try:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=600
        )

        prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=SYSTEM_PROMPT
        )

        history_str = ""
        for msg in conversation_history[-6:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_str += f"{role}: {msg.get('content', '')}\n"

        relevant_docs = retriever.invoke(message)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "chat_history": history_str,
            "question": message
        })

        response_text = response.content if hasattr(response, "content") else str(response)
        sources = [doc.page_content[:100] + "..." for doc in relevant_docs[:2]]

        return response_text, sources

    except Exception as e:
        logger.error(f"RAG chat error: {e}")
        return fallback_chat(message), []

def fallback_chat(message: str) -> str:
    try:
        llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=400
        )
        prompt = f"""You are NutriGen AI, a nutrition expert specializing in Indian and Bengali cuisine.
Answer this nutrition question concisely and helpfully:

{message}"""
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Fallback chat error: {e}")
        return "I am having trouble connecting. Please check your GROQ_API_KEY and try again."
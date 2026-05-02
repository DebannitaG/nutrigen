import os
import logging
from typing import List, Tuple
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/nutrition_knowledge.txt"
)
FAISS_INDEX_PATH = os.path.join(
    os.path.dirname(__file__), "../../data/faiss_index"
)

_vectorstore = None
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info("Loading HuggingFace embedding model (downloads once ~90MB)...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        logger.info("Embedding model loaded.")
    return _embeddings

def build_vectorstore() -> FAISS:
    global _vectorstore
    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} document chunks")

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)
    _vectorstore = vectorstore
    logger.info("FAISS index built and saved.")
    return vectorstore

def get_vectorstore() -> FAISS:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = get_embeddings()
    if os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        try:
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Loaded FAISS index from disk.")
            return _vectorstore
        except Exception as e:
            logger.warning(f"Failed to load FAISS index: {e}. Rebuilding...")

    return build_vectorstore()

SYSTEM_PROMPT = """You are HealthGuard AI, an expert nutritionist and diet advisor specializing in Indian and Bengali cuisine as well as global nutrition.

Use the following context from our nutrition knowledge base to answer the question. If the context doesn't contain the answer, use your general nutrition knowledge but make it clear.

Context:
{context}

Guidelines:
- Give specific, actionable advice
- Reference Indian/Bengali foods when relevant
- Include calorie/nutrient information when helpful
- Be encouraging and supportive
- If asking about meal planning, consider the user's goals

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
            model_name="llama3-8b-8192",
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
            model_name="llama3-8b-8192",
            temperature=0.7,
            max_tokens=400
        )
        prompt = f"""You are HealthGuard AI, a nutrition expert specializing in Indian and Bengali cuisine.
Answer this nutrition question concisely and helpfully:

{message}"""
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Fallback chat error: {e}")
        return "I'm having trouble connecting. Please check your GROQ_API_KEY in the .env file and try again."
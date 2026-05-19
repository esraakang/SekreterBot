import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

provider = (os.getenv("LLM_PROVIDER") or "openai").strip().lower()

if provider == "openai":
    _openai_api_key = os.getenv("OPENAI_API_KEY")
    if not _openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin veya ortam değişkeni olarak tanımlayın."
        )
    # Model ismi güncel Groq modeliyle değiştirildi
    llm = ChatOpenAI(
        model="llama-3.1-8b-instant", 
        temperature=0.7, 
        api_key=_openai_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
elif provider == "gemini":
    _google_api_key = os.getenv("GOOGLE_API_KEY")
    if not _google_api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY bulunamadı. Lütfen .env dosyasına ekleyin veya ortam değişkeni olarak tanımlayın."
        )
    llm = ChatGoogleGenerativeAI(
        model=(os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"),
        temperature=0.7,
        google_api_key=_google_api_key,
    )
else:
    raise RuntimeError("LLM_PROVIDER geçersiz. 'openai' veya 'gemini' olmalı.")
from langchain_core.tools import Tool
import os
import requests
from app.ai.chatbot import process_results_with_openai


def google_search(query):
    """Google Custom Search API kullanarak bir sorgu gerçekleştirir."""
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")
    if not api_key or not cx:
        return (
            "Google araması yapılandırılmamış. "
            ".env dosyasına GOOGLE_API_KEY ve GOOGLE_CX ekleyin."
        )

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cx,
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # HTTP Hatasını yakala
        data = response.json()

        # İlk 3 sonucu birleştirerek string formatında döndür
        results = data.get("items", [])
        if not results:
            return "Sonuç bulunamadı."

        output = "\n".join([
            f"{item.get('title')} - {item.get('link')}\n{item.get('snippet')}"
            for item in results[:3]
        ])
        return output
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP Hatası: {http_err}"
    except Exception as e:
        return f"Bir hata oluştu: {e}"


# process_results_with_openai fonksiyonu bu dosyada kaldırıldı. app/ai/chatbot.py içinden import edin.

# LangChain'e entegre etmek için araçlar
tools = [
    Tool(
        name="Google Search",
        func=google_search,
        description="Google'da bir sorgu çalıştırır ve en üst sonuçları döndürür."
    ),
    Tool(
        name="Google Search + AI Analysis",
        func=lambda query: process_results_with_openai(query, google_search(query)),
        description="Google arama sonuçlarını alır ve OpenAI ile analiz ederek anlamlı bir yanıt oluşturur."
    )
]

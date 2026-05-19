from app.ai import llm
from app.ai.memory import save_message, get_chat_history
import time


def process_user_input(user_id, user_input):
    """
    Kullanıcı girdisini işler, yanıt döner ve geçmişi yönetir.
    """
    # Kullanıcı mesajını kaydet
    save_message(user_id, "user", user_input)

    # Normal chatbot yanıt akışı
    try:
        chat_history = get_chat_history(user_id)

        def _is_errorish(text: str) -> bool:
            t = text.strip().lower()
            return (
                t.startswith("hata:")
                or "error code:" in t
                or "insufficient_quota" in t
                or "resource_exhausted" in t
                or "unavailable" in t
                or "contents are required" in t
                or "traceback" in t
            )

        cleaned = []
        for m in chat_history[-20:]:
            content = (m.get("content") or "").strip()
            if not content or _is_errorish(content):
                continue
            role = "Kullanıcı" if m.get("role") == "user" else "Asistan"
            cleaned.append(f"{role}: {content}")

        history_text = "\n".join(cleaned).strip()

        augmented_input = (
            f"Sohbet:\n{history_text}\n\nKullanıcı: {user_input}"
            if history_text
            else user_input
        )

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                response_msg = llm.invoke(augmented_input)
                response = getattr(response_msg, "content", str(response_msg)).strip()
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                # Gemini/OpenAI tarafındaki geçici yoğunluk durumlarında kısa retry
                if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise
        else:
            raise last_err  # type: ignore[misc]

        save_message(user_id, "assistant", response)
        return response
    except Exception as e:
        error_message = f"Hata: {str(e)}"
        save_message(user_id, "assistant", error_message)
        return error_message

def process_results_with_openai(query, google_results):
    """
    Google sonuçlarını OpenAI ile analiz ederek anlamlı bir yanıt oluşturur.
    """
    prompt = f"""
    Kullanıcı şu soruyu sordu: {query}
    Aşağıda Google'dan alınan sonuçlar var:
    {google_results}

    Bu sonuçları analiz et ve kullanıcıya anlamlı, spesifik bir yanıt oluştur. 
    Sadece ilgili bilgileri kullan ve gereksiz detaylardan kaçın.
    """

    try:
        response = llm.invoke(prompt)
        return getattr(response, "content", str(response)).strip()
    except Exception as e:
        return f"Hata: OpenAI yanıt oluştururken bir sorun oluştu: {e}"

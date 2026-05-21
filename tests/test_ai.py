import pytest
from unittest.mock import MagicMock, patch
from app.ai.chatbot import process_user_input, process_results_with_openai
from app.ai.tools import google_search

@patch("app.ai.chatbot.llm")
@patch("app.ai.chatbot.save_message")
@patch("app.ai.chatbot.get_chat_history")
def test_process_user_input_success(mock_get_history, mock_save_message, mock_llm):
    """Kullanıcı girdisi normal bir şekilde işlendiğinde botun başarıyla yanıt dönmesini test eder."""
    mock_get_history.return_value = [{"role": "user", "content": "Merhaba"}]
    
    mock_response = MagicMock()
    mock_response.content = "Sana nasıl yardımcı olabilirim?"
    mock_llm.invoke.return_value = mock_response

    response = process_user_input("user_123", "Nasılsın?")

    assert response == "Sana nasıl yardımcı olabilirim?"
    assert mock_save_message.call_count == 2
    mock_save_message.assert_any_call("user_123", "user", "Nasılsın?")
    mock_save_message.assert_any_call("user_123", "assistant", "Sana nasıl yardımcı olabilirim?")


@patch("app.ai.chatbot.llm")
@patch("app.ai.chatbot.get_chat_history")
def test_process_user_input_filters_errors_from_history(mock_get_history, mock_llm, app):
    """Geçmişteki 'Hata:' ile başlayan mesajların temizlenip temizlenmediğini test eder."""
    # app context (uygulama bağlamı) içinde çalıştırıyoruz
    with app.app_context():
        mock_get_history.return_value = [
            {"role": "user", "content": "Selam"},
            {"role": "assistant", "content": "Hata: Resource_exhausted veya geçici sorun"}
        ]
        
        mock_response = MagicMock()
        mock_response.content = "Cevap"
        mock_llm.invoke.return_value = mock_response

        process_user_input("user_123", "Test sorusu")

        called_argument = mock_llm.invoke.call_args[0][0]
        assert "Selam" in called_argument
        assert "Resource_exhausted" not in called_argument


@patch("app.ai.chatbot.llm")
@patch("time.sleep")
def test_process_user_input_retry_on_503(mock_sleep, mock_llm, app):
    """503 veya UNAVAILABLE hatası alındığında sistemin retry yapıp yapmadığını test eder."""
    with app.app_context():
        mock_llm.invoke.side_effect = [
            Exception("503 Service Unavailable"),
            Exception("UNAVAILABLE"),
            MagicMock(content="Sonunda başardım!")
        ]

        response = process_user_input("user_123", "Orada mısın?")

        assert response == "Sonunda başardım!"
        assert mock_llm.invoke.call_count == 3
        assert mock_sleep.call_count == 2


@patch("os.getenv")
def test_google_search_not_configured(mock_getenv):
    """Google API anahtarları eksik olduğunda fonksiyonun uyarı dönmesini test eder."""
    mock_getenv.return_value = None

    result = google_search("Python nedir?")
    assert "Google araması yapılandırılmamış" in result


@patch("app.ai.tools.requests.get")
@patch("app.ai.tools.os.getenv")
def test_google_search_success(mock_getenv, mock_get):
    """Google Custom Search API'den başarılı sonuç döndüğünde verinin işlenmesini test eder."""
    mock_getenv.side_effect = lambda key, default=None: "mock_value" if key in ["GOOGLE_API_KEY", "GOOGLE_CX"] else default

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "items": [
            {"title": "Başlık 1", "link": "https://link1.com", "snippet": "Açıklama 1"},
            {"title": "Başlık 2", "link": "https://link2.com", "snippet": "Açıklama 2"}
        ]
    }
    mock_get.return_value = mock_response

    result = google_search("test")
    
    assert "Başlık 1" in result
    assert "https://link1.com" in result
    assert "Açıklama 2" in result


@patch("app.ai.chatbot.llm")
def test_process_results_with_openai(mock_llm):
    """Arama sonuçlarının LLM ile anlamlı bir rapora dönüştürülmesini test eder."""
    mock_response = MagicMock()
    mock_response.content = "Özetlenmiş AI Yanıtı"
    mock_llm.invoke.return_value = mock_response

    result = process_results_with_openai("Hava durumu", "İstanbul: 20 derece")
    
    assert result == "Özetlenmiş AI Yanıtı"
    called_argument = mock_llm.invoke.call_args[0][0]
    assert "Hava durumu" in called_argument
    assert "İstanbul: 20 derece" in called_argument

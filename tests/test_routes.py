from unittest.mock import MagicMock, patch


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SekreterBot" in response.data


def test_chat_rejects_invalid_json(client):
    response = client.post(
        "/chat",
        data="not-json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_chat_rejects_empty_message(client):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 400
    assert "boş" in response.get_json()["error"].lower()


@patch("app.ai.chatbot.llm")
def test_chat_returns_assistant_response(mock_llm, client):
    mock_response = MagicMock()
    mock_response.content = "Merhaba, size nasıl yardımcı olabilirim?"
    mock_llm.invoke.return_value = mock_response

    response = client.post("/chat", json={"message": "Merhaba"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["response"] == "Merhaba, size nasıl yardımcı olabilirim?"


def test_clear_history(client):
    response = client.post("/chat/clear", json={"user_id": "test_user"})
    assert response.status_code == 200
    assert "temizlendi" in response.get_json()["message"].lower()


def test_calendar_events_without_credentials(client):
    response = client.get("/calendar/events")
    assert response.status_code == 503
    assert "error" in response.get_json()

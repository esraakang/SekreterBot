from flask import Blueprint, request, jsonify, render_template
from app.ai.chatbot import process_user_input, process_results_with_openai
from app.ai.tools import google_search
from app.ai.memory import clear_chat_history
from app.ai.google_calendar import list_events, add_event

main_routes = Blueprint('main', __name__)


def _parse_json_body():
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Geçersiz JSON formatı. Lütfen doğru bir JSON gönderin."}), 400)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "JSON gövdesi bir nesne olmalıdır."}), 400)
    return data, None


@main_routes.route('/', methods=['GET'])
def home():
    """Ana sayfa."""
    return render_template('index.html')


@main_routes.route('/chat', methods=['POST'])
def chat_with_bot():
    """LangChain tabanlı bot ile sohbet rotası."""
    data, err = _parse_json_body()
    if err:
        return err

    user_id = data.get('user_id', 'default_user')
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({"error": "Mesaj içeriği boş olamaz."}), 400

    if user_message.lower().startswith("google:"):
        query = user_message[len("google:"):].strip()
        if not query:
            return jsonify({"error": "Google araması için sorgu boş olamaz."}), 400
        google_results = google_search(query)
        processed_response = process_results_with_openai(query, google_results)
        return jsonify({"response": processed_response})

    try:
        response = process_user_input(user_id, user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"Sohbet islenirken hata olustu: {e}"}), 500


@main_routes.route('/chat/clear', methods=['POST'])
def clear_history():
    """Kullanıcı sohbet geçmişini temizler."""
    data, err = _parse_json_body()
    if err:
        return err

    user_id = data.get('user_id', 'default_user')
    clear_chat_history(user_id)
    return jsonify({"message": "Sohbet geçmişi temizlendi."})


@main_routes.route('/calendar/events', methods=['GET'])
def get_calendar_events():
    """Takvimdeki etkinlikleri listeler."""
    try:
        events = list_events()
        return jsonify({"events": events})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Takvim etkinlikleri alınamadı: {e}"}), 500


@main_routes.route('/calendar/events', methods=['POST'])
def create_calendar_event():
    """Yeni bir takvim etkinliği oluşturur."""
    data, err = _parse_json_body()
    if err:
        return err

    summary = data.get('summary')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not summary or not start_time or not end_time:
        return jsonify({"error": "Eksik bilgi. Lütfen tüm alanları doldurun."}), 400

    try:
        result = add_event(summary, start_time, end_time)
        return jsonify({"message": result})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Etkinlik oluşturulamadı: {e}"}), 500

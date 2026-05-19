import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5001"))
    print(f"SekreterBot: http://127.0.0.1:{port}")
    app.run(debug=True, host="127.0.0.1", port=port)
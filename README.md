# SekreterBot 🤖

SekreterBot, kullanıcıların günlük işlerini kolaylaştırmak amacıyla geliştirilmiş, yapay zeka destekli kişisel sekreter web uygulamasıdır. Türkçe doğal dil işleme, web arama ve Google Takvim entegrasyonu sunar.

---

## Özellikler

- 💬 **Akıllı Sohbet:** OpenAI GPT-3.5 veya Google Gemini ile bağlam farkında çok turlu konuşma
- 🔍 **Web Arama:** `google:` öneki ile Google arama ve LLM destekli sonuç analizi
- 📅 **Takvim Yönetimi:** Google Calendar API ile etkinlik listeleme ve oluşturma
- 🧠 **Sohbet Hafızası:** Kullanıcı başına kalıcı mesaj geçmişi (SQLite)
- 🔄 **Çoklu LLM Desteği:** Ortam değişkeni ile OpenAI veya Gemini arasında geçiş
- 📋 **Dönen Log Sistemi:** Hata ayıklama için otomatik dönen log dosyaları

---

## Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Python 3.10+, Flask, LangChain |
| **Veritabanı** | SQLite, SQLAlchemy ORM |
| **Kimlik Doğrulama** | Flask-JWT-Extended |
| **Yapay Zeka** | OpenAI GPT-3.5-turbo, Google Gemini 2.0 Flash |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Test** | pytest, unittest.mock |
| **Harici API** | Google Calendar API, Google Custom Search API |

---

## Kurulum Adımları

### Gereksinimler

- Python 3.10 veya üzeri
- pip

### 1. Repoyu klonlayın

```bash
git clone https://github.com/esraakang/SekreterBot.git
cd SekreterBot
```

### 2. Sanal ortam oluşturun ve bağımlılıkları yükleyin

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ortam değişkenlerini ayarlayın

`.env` dosyası oluşturun:

```env
LLM_PROVIDER=gemini          # veya openai
OPENAI_API_KEY=sk-...        # LLM_PROVIDER=openai ise gerekli
GOOGLE_API_KEY=...           # LLM_PROVIDER=gemini ise gerekli
GEMINI_MODEL=gemini-2.0-flash
JWT_SECRET_KEY=gizli-anahtar
FLASK_PORT=5001
```

### 4. Uygulamayı başlatın

```bash
python run.py
```

Uygulama `http://localhost:5001` adresinde çalışır.

---

## Kullanım

Tarayıcıda `http://localhost:5001` adresine gidin.

- **Normal sohbet:** Metin kutusuna sorunuzu yazın ve gönderin
- **Web araması:** Mesajınıza `google:` öneki ekleyin → `google: Python nedir?`
- **Takvim:** Sohbet üzerinden etkinliklerinizi görüntüleyebilir ve oluşturabilirsiniz

### API Uç Noktaları

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/` | Ana sayfa |
| POST | `/chat` | Sohbet mesajı gönder |
| POST | `/chat/clear` | Sohbet geçmişini temizle |
| GET | `/calendar/events` | Takvim etkinliklerini listele |
| POST | `/calendar/events` | Yeni takvim etkinliği oluştur |

---

## Testleri Çalıştırma

```bash
pytest tests/
```

---

## Katkı (Contribution)

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun: `git checkout -b feature/yeni-ozellik`
3. Değişikliklerinizi commit edin: `git commit -m 'Yeni özellik eklendi'`
4. Branch'inizi push edin: `git push origin feature/yeni-ozellik`
5. Pull Request açın

---

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

## Geliştirici Ekip

| İsim | Numara |
|------|--------|
| Esra Kang | 170425823 |
| Meryem Akbaba | 170425824 |
| Ebru Taşcıoğulları | 170425509 |
| Enes Bulut | 170424507 |

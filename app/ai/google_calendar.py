import os
import datetime
import pickle
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CREDENTIALS_PATH = _PROJECT_ROOT / 'app' / 'ai' / 'credentials' / 'client_secret.json'
_TOKEN_PATH = _PROJECT_ROOT / 'instance' / 'token.pickle'


def _credentials_missing_message():
    return (
        "Google Calendar kimlik bilgileri bulunamadı. "
        f"Lütfen OAuth client dosyasını şuraya yerleştirin: {_CREDENTIALS_PATH}"
    )


def get_calendar_service():
    """Google Calendar API istemcisini başlatır ve döner."""
    if not _CREDENTIALS_PATH.is_file():
        raise FileNotFoundError(_credentials_missing_message())

    creds = None
    _TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

    if _TOKEN_PATH.exists():
        with open(_TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(_CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(_TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def list_events():
    """Kullanıcının takvimindeki etkinlikleri listeler."""
    service = get_calendar_service()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_utc.isoformat(),
        maxResults=10,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    events = events_result.get('items', [])
    if not events:
        return []
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"{start}: {event['summary']}")
    return event_list


def add_event(summary, start_time, end_time):
    """Yeni bir etkinlik ekler."""
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Istanbul',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Istanbul',
        },
    }
    created = service.events().insert(calendarId='primary', body=event).execute()
    return f"Etkinlik oluşturuldu: {created.get('htmlLink')}"

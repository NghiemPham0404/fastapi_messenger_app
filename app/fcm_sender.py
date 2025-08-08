from typing import Annotated
from sqlalchemy.orm import Session
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from .entities.fcm_token import FCMToken
from .message.models import MessageOut

# Initialize
PROJECT_ID = 'messenger-app-e9f0b'
SERVICE_ACCOUNT_FILE = 'app/messenger-app-e9f0b-firebase-adminsdk-fbsvc-1b122d5486.json'
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# get access-token from service account
def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    credentials.refresh(Request())  # Tự động lấy access_token mới
    return credentials.token

# Send fcm to token
def send_fcm_to_token(token: str, message_data: dict):
    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; UTF-8'
    }

    payload = {
        "message": {
            "token": token,
            "data": {
                "type": "chat_message",
                **message_data
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Status:", response.status_code)
    print("token :", access_token)
    print("Response:", response.text)
    return response


# Send fcm to token
def send_message_to_user(user_id : int ,message_data: MessageOut, db : Session):
    fcm_token = db.query(FCMToken).where(FCMToken.user_id == user_id).first()

    if fcm_token:
        token = fcm_token.token
    else:
        return

    access_token = get_access_token()
    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; UTF-8'
    }

    import json

    payload = {
        "message": {
            "token": token,
            "data": {
                "type": "chat_message",
                "message": json.dumps(message_data.model_dump(mode="json", exclude_none=True, by_alias=True), default=str)
            }
        }
    }


    response = requests.post(url, headers=headers, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.text)
    return response
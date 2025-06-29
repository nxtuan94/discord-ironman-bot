# replit/drive_utils.py

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
import base64


# Hàm để khôi phục token từ base64
def restore_token_from_base64():
    with open("token_drive_base64.txt", "r") as f:
        b64data = f.read()

    with open("token_drive.pickle", "wb") as f:
        f.write(base64.b64decode(b64data))


# Cấu hình OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token_drive.pickle'


def authenticate_drive():
    restore_token_from_base64()
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def upload_file(service, file_path, folder_id):
    file_name = os.path.basename(file_path)

    # Tìm file trùng tên đã tồn tại
    query = f"name='{file_name}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id)",
                                   pageSize=1).execute()
    items = results.get("files", [])

    media = MediaFileUpload(file_path, resumable=True)
    if items:
        # Nếu đã tồn tại, ghi đè (update)
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Nếu chưa có, tạo mới
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        service.files().create(body=file_metadata,
                               media_body=media,
                               fields='id').execute()


def download_file(service, file_name, folder_id):
    query = f"name='{file_name}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id)",
                                   pageSize=1).execute()
    items = results.get("files", [])
    if not items:
        raise FileNotFoundError(
            f"Không tìm thấy file '{file_name}' trên Google Drive.")

    file_id = items[0]['id']
    request = service.files().get_media(fileId=file_id)

    dest_path = file_name
    folder = os.path.dirname(dest_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

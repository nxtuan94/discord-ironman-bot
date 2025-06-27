import os
import zipfile
import datetime
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Cấu hình OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token_drive.pickle'
DB_FILE = 'checkin.db'


def create_backup_zip():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    zip_name = f'backup_{date_str}.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(DB_FILE)
    return zip_name


def login_google_drive():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Luồng xác thực thủ công hoàn toàn
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            auth_url, _ = flow.authorization_url(prompt='consent')
            print("🔗 Mở link sau để xác thực:\n", auth_url)

            code = input("📥 Nhập mã xác minh (code): ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print(f"✅ Đã lưu token tại: {TOKEN_FILE}")

    return build('drive', 'v3', credentials=creds)


FOLDER_ID = '1G2_uod0vJRCnLDf-4V1YmUELNlHfFHF5'  # Thay bằng ID thật


def upload_to_drive(file_path):
    service = login_google_drive()
    if not service:
        print("⚠ Không thể xác thực với Google Drive.")
        return None

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, mimetype='application/zip')

    uploaded = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()

    print(f'✅ File đã upload lên thư mục. File ID: {uploaded.get("id")}')
    return uploaded.get("id")

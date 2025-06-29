# data_sync.py

from drive_utils import authenticate_drive, upload_file, download_file
import os
from config import FILES, FOLDER_ID


def backup_to_drive():
    service = authenticate_drive()
    for file in FILES:
        if os.path.exists(file):
            try:
                upload_file(service, file, FOLDER_ID)
                print(f"✅ Đã sao lưu {file} lên Google Drive.")
            except Exception as e:
                print(f"⚠ Lỗi khi sao lưu {file}: {e}")
        else:
            print(f"⛔ File không tồn tại: {file}")


def restore_from_drive():
    service = authenticate_drive()
    for file in FILES:
        try:
            download_file(service, file, FOLDER_ID)
            print(f"📥 Đã khôi phục {file} từ Google Drive.")
        except Exception as e:
            print(f"⚠ Lỗi khi khôi phục {file}: {e}")

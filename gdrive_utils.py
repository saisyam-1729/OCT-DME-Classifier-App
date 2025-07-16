import os
import io
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# Environment variable secrets
SERVICE_ACCOUNT_PATH = "temp_secret.json"
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Authenticate Google Sheet
def init_google_clients():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheet_client = gspread.authorize(creds)
    return sheet_client

# Save image locally to a feedback folder
def save_feedback_image(img: Image.Image, filename: str):
    folder = "feedback_images"
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, filename))

# Log user feedback to the Google Sheet
def log_feedback_to_sheet(sheet_client, username, input_label, right_label, left_label, right_feedback, left_feedback, right_correction, left_correction):
    sheet = sheet_client.open_by_key(SHEET_ID).sheet1

    row = [
        username,
        input_label,
        f"Right: {right_label}, Left: {left_label}",
        right_feedback,
        left_feedback,
        right_correction or "-",
        left_correction or "-"
    ]

    sheet.append_row(row)

import streamlit as st
import os
from PIL import Image
from ultralytics import YOLO
from gdrive_utils import (
    init_google_clients,
    save_feedback_image,
    log_feedback_to_sheet
)

# Step 1: Recreate temp_secret.json
service_account_json = os.getenv("Google_Service_Account")
if service_account_json:
    with open("temp_secret.json", "w") as f:
        f.write(service_account_json)
else:
    st.error("❌ GOOGLE_SERVICE_ACCOUNT secret not found. Please set it in your Space settings.")
    st.stop()

# Step 2: Load YOLOv8 model
MODEL_PATH = "./best.pt"
@st.cache_resource
def load_model():
    return YOLO(MODEL_PATH)
model = load_model()

# Step 3: Initialize Google Sheets client
sheet_client = init_google_clients()

# Step 4: UI - User Input
st.title("👁️ OCT DME Classifier")
username = st.text_input("Enter your name:")
image_file = st.file_uploader("Upload OCT image", type=["jpg", "png", "jpeg"])

if image_file and username:
    image = Image.open(image_file).convert("RGB")
    input_label = image_file.name
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Coordinates
    right_coords = (100, 675, 420, 910)
    left_coords = (450, 675, 770, 910)
    right_eye = image.crop(right_coords)
    left_eye = image.crop(left_coords)

    st.subheader("🔍 Model Predictions")
    preds_right = model.predict(right_eye, imgsz=640)[0]
    preds_left = model.predict(left_eye, imgsz=640)[0]

    right_label = preds_right.names[int(preds_right.probs.top1)]
    left_label = preds_left.names[int(preds_left.probs.top1)]

    st.write(f"**Right Eye:** {right_label}")
    st.write(f"**Left Eye:** {left_label}")

    # Step 5: Feedback
    st.subheader("📝 Feedback")
    agree_right = st.radio("Do you agree with the prediction for Right Eye?", ["Yes", "No"], key="right")
    agree_left = st.radio("Do you agree with the prediction for Left Eye?", ["Yes", "No"], key="left")

    right_correct = None
    left_correct = None

    options = ["CME", "DRT", "NORMAL", "SRD"]
    count = 1

    if agree_right == "No":
        right_correct = st.selectbox("What should be the correct class for Right Eye?", options, key="correct_r")
        filename = f"{username}-{right_correct}_{str(count).zfill(5)}.png"
        save_feedback_image(right_eye, filename)
        count += 1

    if agree_left == "No":
        left_correct = st.selectbox("What should be the correct class for Left Eye?", options, key="correct_l")
        filename = f"{username}-{left_correct}_{str(count).zfill(5)}.png"
        save_feedback_image(left_eye, filename)
        count += 1

    # Submit feedback
    if st.button("Submit Feedback"):
        log_feedback_to_sheet(
            sheet_client,
            username,
            input_label,
            right_label,
            left_label,
            agree_right,
            agree_left,
            right_correct,
            left_correct
        )
        st.success("✅ Feedback submitted successfully!")
import streamlit as st
from PIL import Image
from ultralytics import YOLO

# -------------------------------
# Constants
# -------------------------------
MODEL_PATH = "OCT_DME_CLASSIFICATION_APP\best.pt"
CLASS_NAMES = ["Normal", "CME", "DRT", "SRD"]
right_OCT_coords = (100, 675, 420, 910)
left_OCT_coords = (450, 675, 770, 910)

# -------------------------------
# Load Model with Caching
# -------------------------------
@st.cache_resource
def load_model():
    model = YOLO(MODEL_PATH)
    return model

# -------------------------------
# Inference Function
# -------------------------------
def predict(model, pil_img):
    results = model(pil_img, verbose=False)
    probs = results[0].probs
    class_id = int(probs.top1)
    confidence = float(probs.top1conf)
    return CLASS_NAMES[class_id], confidence

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="OCT Eye Disease Classifier", layout="centered")
st.title("🧠 OCT Eye Disease Classifier")
st.write("Upload an OCT image, and this app will classify the **right and left eyes** using a YOLOv8 model.")

# File uploader
uploaded_file = st.file_uploader("📤 Upload OCT Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded OCT Image", use_column_width=True)

    # Crop right and left eyes
    right_eye = image.crop(right_OCT_coords)
    left_eye = image.crop(left_OCT_coords)

    # Display cropped images
    st.subheader("👁️ Extracted Eye Regions")
    col1, col2 = st.columns(2)
    with col1:
        st.image(right_eye, caption="Right Eye", use_column_width=True)
    with col2:
        st.image(left_eye, caption="Left Eye", use_column_width=True)

    # Load model and predict
    model = load_model()

    st.subheader("🔍 Model Predictions")

    with st.spinner("Running model on Right Eye..."):
        right_label, right_conf = predict(model, right_eye)
        st.success(f"🟦 Right Eye: **{right_label}** (Confidence: {right_conf:.2f})")

    with st.spinner("Running model on Left Eye..."):
        left_label, left_conf = predict(model, left_eye)
        st.success(f"🟥 Left Eye: **{left_label}** (Confidence: {left_conf:.2f})")


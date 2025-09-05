import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io, zipfile
from datetime import datetime

# -------------------------------
# Image Enhancement Function
# -------------------------------
def enhance_image(img, max_size=2048):
    img = img.convert("RGB")
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Color(img).enhance(1.2)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Sharpness(img).enhance(1.1)
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    return img

# -------------------------------
# Device Detection Helper
# -------------------------------
def is_mobile():
    try:
        user_agent = st.session_state.get("_user_agent", "")
        if not user_agent:
            user_agent = st.experimental_get_query_params().get("ua", [""])[0]
            st.session_state["_user_agent"] = user_agent.lower()
        ua = st.session_state["_user_agent"]
        return any(mobile_kw in ua for mobile_kw in ["iphone", "android", "ipad", "mobile"])
    except:
        return False

# -------------------------------
# Subscription Plans
# -------------------------------
tiers = {
    "Free": {"credits": 10},          # Free plan: 10 edits/month
    "Level 1": {"credits": 100},      # Level 1: 100 edits/month
    "Level 2": {"credits": float("inf")},  # Level 2: Unlimited edits
}

# -------------------------------
# Initialize Session State
# -------------------------------
if "plan" not in st.session_state:
    st.session_state.plan = "Free"
if "credits_used" not in st.session_state:
    st.session_state.credits_used = 0
if "last_reset" not in st.session_state:
    st.session_state.last_reset = datetime.now().strftime("%Y-%m")

# Reset credits monthly
current_month = datetime.now().strftime("%Y-%m")
if current_month != st.session_state.last_reset:
    st.session_state.credits_used = 0
    st.session_state.last_reset = current_month

# -------------------------------
# App UI
# -------------------------------
st.title("📸 MLS Photo Enhancer")

# Show plan + credits
plan = st.session_state.plan
max_credits = tiers[plan]["credits"]
used = st.session_state.credits_used
remaining = max_credits - used if max_credits != float("inf") else "∞"

st.info(f"Plan: **{plan}** | Used: {used} | Remaining: {remaining} | Resets monthly")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

# -------------------------------
# Process Uploaded Files
# -------------------------------
if uploaded_files:
    if max_credits != float("inf") and used + len(uploaded_files) > max_credits:
        st.error("❌ Not enough credits! Please upgrade your plan.")
    else:
        output_images = []
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for i, file in enumerate(uploaded_files, start=1):
                img = Image.open(file)
                enhanced = enhance_image(img)

                buf = io.BytesIO()
                enhanced.save(buf, format="JPEG", quality=90)
                img_bytes = buf.getvalue()

                # Add to ZIP
                zipf.writestr(f"{i:02}.jpg", img_bytes)

                # Store for individual downloads
                output_images.append((i, img_bytes))

        st.success("✅ Photos enhanced successfully!")

        # Auto-detect + manual override
        default_mode = "Individual Photos" if is_mobile() else "ZIP"
        download_mode = st.radio(
            "Choose download option:",
            ["ZIP", "Individual Photos"],
            index=0 if default_mode == "ZIP" else 1
        )

        if download_mode == "Individual Photos":
            st.subheader("📱 Download Individual Photos")
            for i, img_bytes in output_images:
                st.download

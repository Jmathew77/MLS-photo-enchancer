import streamlit as st
from enhance import enhance_image
import io, zipfile
from PIL import Image

# Simulated "user database" for demo
tiers = {
    "Free": {"credits": 5},
    "Level 1": {"credits": 50},
    "Level 2": {"credits": 100},
    "Level 3": {"credits": float("inf")},
}

# Simulated login
if "plan" not in st.session_state:
    st.session_state.plan = "Free"
if "credits_used" not in st.session_state:
    st.session_state.credits_used = 0

st.title("📸 MLS Photo Enhancer")

# Show plan + credits
plan = st.session_state.plan
max_credits = tiers[plan]["credits"]
used = st.session_state.credits_used
remaining = max_credits - used if max_credits != float("inf") else "∞"

st.info(f"Plan: **{plan}** | Used: {used} | Remaining: {remaining}")

# File uploader
uploaded_files = st.file_uploader(
    "Upload your photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

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
                zipf.writestr(f"{i:02}.jpg", buf.getvalue())
                output_images.append(enhanced)

        st.success("✅ Photos enhanced successfully!")
        st.download_button(
            label="Download MLS_Photos.zip",
            data=zip_buffer.getvalue(),
            file_name="MLS_Photos.zip",
            mime="application/zip",
        )

        # Deduct credits
        st.session_state.credits_used += len(uploaded_files)

# Upgrade section
st.subheader("Upgrade Plan")
if st.button("Upgrade to Level 1 (50 edits/month)"):
    st.session_state.plan = "Level 1"
    st.session_state.credits_used = 0
if st.button("Upgrade to Level 2 (100 edits/month)"):
    st.session_state.plan = "Level 2"
    st.session_state.credits_used = 0
if st.button("Upgrade to Level 3 (Unlimited)"):
    st.session_state.plan = "Level 3"
    st.session_state.credits_used = 0

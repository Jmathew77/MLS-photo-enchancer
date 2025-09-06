import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io, zipfile
from datetime import datetime

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="MLS Photo Enhancer", page_icon="📸", layout="wide")

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
            user_agent = st.query_params.get("ua", [""])[0]
            st.session_state["_user_agent"] = user_agent.lower()
        ua = st.session_state["_user_agent"]
        return any(mobile_kw in ua for mobile_kw in ["iphone", "android", "ipad", "mobile"])
    except:
        return False

# -------------------------------
# Subscription Plans
# -------------------------------
tiers = {
    "Free": {"credits": 10},
    "Level 1": {"credits": 100},
    "Level 2": {"credits": float("inf")},
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
# Header
# -------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #2563eb;'>📸 MLS Photo Enhancer</h1>
    <p style='text-align: center; font-size:18px; color: gray;'>
    Turn your phone photos into MLS-ready listings in seconds
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Layout
# -------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload your photos (max 15 per session)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    # Enforce 15 image limit
    if uploaded_files and len(uploaded_files) > 15:
        st.error("❌ You can only upload up to 15 images per session. Please remove some and try again.")
        uploaded_files = []

    # Process Uploaded Files
    if uploaded_files:
        plan = st.session_state.plan
        max_credits = tiers[plan]["credits"]
        used = st.session_state.credits_used

        if max_credits != float("inf") and used + len(uploaded_files) > max_credits:
            st.error("❌ Not enough credits! Please upgrade your plan.")
        else:
            output_images = []
            zip_buffer = io.BytesIO()

            # Progress bar
            progress = st.progress(0)
            status_text = st.empty()

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

                    # Update progress bar
                    progress.progress(i / len(uploaded_files))
                    status_text.text(f"Processing image {i} of {len(uploaded_files)}...")

            # Clear progress after done
            progress.empty()
            status_text.empty()

            st.success("✅ Photos enhanced successfully!")

            # Auto-detect device and show appropriate download option
            if is_mobile():
                st.subheader("📱 Download Individual Photos")
                for i, img_bytes in output_images:
                    st.download_button(
                        label=f"Download Photo {i}",
                        data=img_bytes,
                        file_name=f"{i:02}.jpg",
                        mime="image/jpeg",
                    )
                # Mobile hint
                st.markdown(
                    "<p style='color:gray; font-size:14px;'>💡 Tip: Tap a photo button above and then select <b>Save to Camera Roll</b> on your phone.</p>",
                    unsafe_allow_html=True
                )
            else:
                st.download_button(
                    label="📦 Download All (MLS_Photos.zip)",
                    data=zip_buffer.getvalue(),
                    file_name="MLS_Photos.zip",
                    mime="application/zip",
                )
                # Desktop hint
                st.markdown(
                    "<p style='color:gray; font-size:14px;'>💡 Tip: Works best on desktop for downloading large batches of photos as a single ZIP file.</p>",
                    unsafe_allow_html=True
                )

            # Deduct credits
            st.session_state.credits_used += len(uploaded_files)

with col2:
    # Show plan + credits in styled card
    plan = st.session_state.plan
    max_credits = tiers[plan]["credits"]
    used = st.session_state.credits_used
    remaining = max_credits - used if max_credits != float("inf") else "∞"

    st.markdown(
        f"""
        <div style='padding:20px; border-radius:12px; background:#f0f4ff; margin-bottom:20px;'>
            <h3 style='margin:0; color:#2563eb;'>Your Plan: {plan}</h3>
            <p style='margin:0; font-size:16px;'>Used: {used} | Remaining: {remaining}</p>
            <p style='margin:0; font-size:14px; color:gray;'>Credits reset monthly</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Upgrade section
    st.markdown("### 🔑 Upgrade Plan")
    if st.button("🚀 Level 1 – 100 edits/month ($19)"):
        st.session_state.plan = "Level 1"
        st.session_state.credits_used = 0
        st.success("✅ Upgraded to Level 1")

    if st.button("🏆 Level 2 – Unlimited edits ($49)"):
        st.session_state.plan = "Level 2"
        st.session_state.credits_used = 0
        st.success("✅ Upgraded to Level 2")

# -------------------------------
# Footer
# -------------------------------
st.markdown(
    """
    <hr>
    <p style='text-align: center; color: gray; font-size:14px;'>
    © 2025 MLS Photo Enhancer • <a href='#'>Support</a> • <a href='#'>Terms</a>
    </p>
    """,
    unsafe_allow_html=True
)

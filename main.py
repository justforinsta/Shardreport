import streamlit as st
import requests
import base64

st.set_page_config(page_title="Instagram Report Viewer", layout="centered")

st.title("📄 Instagram Report Viewer")
st.caption("Enter your Instagram CSRF and Session ID to fetch your report history.")

# --- Input Fields ---
csrf = st.text_input("CSRF Token", type="default", placeholder="e.g. abc123...")
session_id = st.text_input("Session ID", type="default", placeholder="e.g. 12345%3Aabcde...", help="Get from your Instagram cookies.")

if st.button("🔍 Fetch Reports"):
    if not csrf or not session_id:
        st.error("❌ Please enter both CSRF and Session ID.")
    else:
        try:
            # --- Make Request to Instagram Report Page ---
            headers = {
                "User-Agent": "Mozilla/5.0",
                "X-CSRFToken": csrf,
                "Cookie": f"sessionid={session_id}; csrftoken={csrf};"
            }

            response = requests.get("https://www.instagram.com/support/reports/", headers=headers)

            if response.status_code == 200:
                html = response.text

                # Save for debugging
                with open("debug_instagram_support.html", "w", encoding="utf-8") as f:
                    f.write(html)

                st.success("✅ Page fetched and saved as debug_instagram_support.html")
                
                # --- Download Button ---
                b64 = base64.b64encode(html.encode()).decode()
                download_link = f'<a href="data:text/html;base64,{b64}" download="debug_instagram_support.html">📥 Download debug_instagram_support.html</a>'
                st.markdown(download_link, unsafe_allow_html=True)

                st.info("⚠️ Please download and share this file here so I can analyze your report layout.")
            else:
                st.error(f"❌ Failed to fetch reports. Status code: {response.status_code}")

        except Exception as e:
            st.error(f"🚫 Error: {e}")

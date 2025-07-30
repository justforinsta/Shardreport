import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os

st.set_page_config(page_title="Instagram Report Viewer", layout="centered")

# ---------- CSS Styling ----------
st.markdown("""
    <style>
    .report-box {
        background-color: #111;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
        border: 1px solid #333;
        color: white;
    }
    .status-banner {
        background-color: #2ecc71;
        padding: 6px;
        text-align: center;
        border-radius: 8px;
        font-weight: bold;
        color: white;
        margin-bottom: 15px;
    }
    .more-button {
        background-color: #3897f0;
        padding: 10px;
        text-align: center;
        border-radius: 10px;
        color: white;
        margin-top: 15px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Instagram Report Viewer")
st.caption("Use your `sessionid` and `csrftoken` to load report history.")

sessionid = st.text_input("🍪 Session ID", type="password")
csrftoken = st.text_input("🔐 CSRF Token", type="password")

def get_reports_html(sessionid, csrftoken):
    session = requests.Session()
    session.cookies.set("sessionid", sessionid, domain=".instagram.com")
    session.cookies.set("csrftoken", csrftoken, domain=".instagram.com")
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        "Referer": "https://www.instagram.com/support/requests/",
        "X-CSRFToken": csrftoken,
    })
    r = session.get("https://www.instagram.com/support/requests/")
    
    if "Log in" in r.text or "login" in r.url:
        return None
    
    # Save HTML for debugging
    with open("debug_instagram_support.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    return r.text

def parse_reports(html):
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div")

    reports = []
    for div in divs:
        text = div.get_text(" ", strip=True)
        if any(keyword in text.lower() for keyword in [
            "you anonymously reported",
            "we've removed",
            "thank you for reporting",
            "goes against our"
        ]):
            reports.append({
                "username": "unknown",
                "date": "unknown",
                "reason": "report",
                "status": "closed" if "removed" in text.lower() else "open",
                "description": text,
                "avatar": "https://i.imgur.com/xZzVMpD.png"
            })
    return reports

if st.button("Fetch Reports"):
    if not sessionid or not csrftoken:
        st.error("Please enter both values.")
    else:
        with st.spinner("🔍 Fetching reports..."):
            html = get_reports_html(sessionid, csrftoken)

            if html is None:
                st.error("❌ Session invalid or login expired. Try with a new sessionid.")
            else:
                st.success("✅ HTML saved as `debug_instagram_support.html`. Open it to inspect.")

                report_data = parse_reports(html)

                if not report_data:
                    st.warning("No reports matched in HTML. Please upload `debug_instagram_support.html`.")
                else:
                    for report in report_data:
                        st.markdown('<div class="report-box">', unsafe_allow_html=True)
                        st.markdown(f'<div class="status-banner">{report["status"].capitalize()}</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 6])
                        with col1:
                            response = requests.get(report["avatar"])
                            img = Image.open(BytesIO(response.content))
                            st.image(img, width=50)
                        with col2:
                            st.markdown(f"<b>Reason:</b> {report['reason'].capitalize()}<br><span style='color:gray;'>{report['date']}</span>", unsafe_allow_html=True)
                        
                        st.markdown(f"<br>{report['description']}", unsafe_allow_html=True)
                        st.markdown(f'<div class="more-button">More Options</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

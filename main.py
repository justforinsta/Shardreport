import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Instagram Report Viewer", layout="centered")

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
st.caption("Enter your Instagram session details to view your report history.")

# User input
sessionid = st.text_input("Session ID", type="password")
csrftoken = st.text_input("CSRF Token", type="password")

def get_reports_html(sessionid, csrftoken):
    session = requests.Session()
    session.cookies.set("sessionid", sessionid, domain=".instagram.com")
    session.cookies.set("csrftoken", csrftoken, domain=".instagram.com")
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        "Referer": "https://www.instagram.com/support/requests/",
        "X-CSRFToken": csrftoken,
    })
    response = session.get("https://www.instagram.com/support/requests/")
    if "support" not in response.url or "Log in" in response.text:
        return None
    return response.text

def parse_reports(html):
    soup = BeautifulSoup(html, "html.parser")
    report_blocks = soup.find_all("div", class_="_abn6")  # container divs (may change)
    reports = []
    for block in report_blocks:
        text = block.get_text(" ", strip=True)
        if not text:
            continue
        reports.append({
            "username": "unknown",  # Instagram doesn't include direct username in plain HTML
            "date": "unknown",      # Same for date — can be estimated from ordering
            "reason": "reported content",
            "status": "closed" if "removed" in text.lower() else "open",
            "description": text,
            "avatar": "https://i.imgur.com/xZzVMpD.png"  # Placeholder avatar
        })
    return reports

if st.button("Fetch Reports"):
    if not sessionid or not csrftoken:
        st.error("Please enter both sessionid and csrftoken.")
    else:
        with st.spinner("Fetching reports..."):
            html = get_reports_html(sessionid, csrftoken)
            if html is None:
                st.error("Failed to fetch reports. Invalid session or login expired.")
            else:
                report_data = parse_reports(html)
                if not report_data:
                    st.info("No reports found.")
                for report in report_data:
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(f'<div class="status-banner">Closed</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 6])
                    with col1:
                        avatar_url = report["avatar"]
                        response = requests.get(avatar_url)
                        img = Image.open(BytesIO(response.content))
                        st.image(img, width=50)
                    with col2:
                        st.markdown(f"<b>{report['reason'].capitalize()}</b><br><span style='color:gray;'>{report['date']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<br>{report['description']}<br>", unsafe_allow_html=True)
                    st.markdown(f'<div class="more-button">More Options</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

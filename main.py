import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Instagram Report Viewer", layout="centered")

# ---------- CSS ----------
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

# ---------- Inputs ----------
st.title("📱 Instagram Report Viewer")
st.caption("Enter your sessionid + csrftoken to see your report history.")

sessionid = st.text_input("🍪 Session ID", type="password")
csrftoken = st.text_input("🔐 CSRF Token", type="password")

# ---------- Scraper ----------
def fetch_and_parse_reports(sessionid, csrftoken):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-CSRFToken": csrftoken,
        "Cookie": f"sessionid={sessionid}; csrftoken={csrftoken};"
    }
    url = "https://www.instagram.com/support/reports/"

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script_tag:
        return []

    try:
        data = json.loads(script_tag.string)
        raw_reports = data["props"]["pageProps"]["reportHistory"]
    except Exception as e:
        print("Parsing error:", e)
        return []

    reports = []
    for rep in raw_reports:
        reported_user = rep.get("reportedAccount", "unknown_user")
        reason = rep.get("reportReason", "Unknown")
        status = rep.get("status", "open")
        date_raw = rep.get("date", "")
        try:
            date_fmt = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%SZ")
            date_str = date_fmt.strftime("%B %d, %Y")
        except:
            date_str = "Unknown Date"

        msg = rep.get("body", "Your report was received.")
        reports.append({
            "username": reported_user,
            "reason": reason,
            "status": status,
            "description": msg,
            "date": date_str,
            "avatar": "https://i.imgur.com/xZzVMpD.png"
        })

    return reports

# ---------- Display ----------
if st.button("Fetch Reports"):
    if not sessionid or not csrftoken:
        st.error("Both fields are required.")
    else:
        with st.spinner("Fetching your reports from Instagram..."):
            reports = fetch_and_parse_reports(sessionid, csrftoken)

            if not reports:
                st.warning("No reports found or session expired.")
            else:
                st.success(f"✅ Found {len(reports)} reports.")

                for report in reports:
                    st.markdown('<div class="report-box">', unsafe_allow_html=True)
                    st.markdown(f'<div class="status-banner">{report["status"].capitalize()}</div>', unsafe_allow_html=True)

                    col1, col2 = st.columns([1, 6])
                    with col1:
                        img = Image.open(BytesIO(requests.get(report["avatar"]).content))
                        st.image(img, width=50)
                    with col2:
                        st.markdown(f"<b>Reported:</b> {report['username']}<br><span style='color:gray;'>{report['date']}</span>", unsafe_allow_html=True)

                    st.markdown(f"<br>{report['description']}", unsafe_allow_html=True)
                    st.markdown('<div class="more-button">More Options</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

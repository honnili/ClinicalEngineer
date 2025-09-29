import streamlit as st
import requests
import os

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SCOPE = "openid email profile"

def login_google():
    if "user_id" not in st.session_state:
        auth_link = (
            f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
            f"&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
        )
        st.markdown(f"[Googleでログイン]({auth_link})")

        code = st.experimental_get_query_params().get("code", None)
        if code:
            token_data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code[0],
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code"
            }
            token_res = requests.post(TOKEN_URL, data=token_data).json()
            access_token = token_res.get("access_token")

            user_info = requests.get(
                USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            st.session_state["user_id"] = user_info["id"]
            st.success(f"{user_info['email']} としてログインしました！")
    else:
        st.info(f"現在ログイン中: {st.session_state['user_id']}")
        if st.button("ログアウト"):
            del st.session_state["user_id"]
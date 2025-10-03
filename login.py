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
    query_params = st.query_params

    if "user_id" not in st.session_state:
        if "code" not in query_params:
            # ログインリンクを表示
            auth_link = (
                f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code"
                f"&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
            )
            st.markdown(f"[Googleでログイン]({auth_link})")
            return

        # code がある場合 → トークン取得
        code = query_params.get("code")
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        token_res = requests.post(TOKEN_URL, data=token_data).json()
        st.write("DEBUG token_res =", token_res)

        access_token = token_res.get("access_token")
        if not access_token:
            st.error("アクセストークンが取得できませんでした")
            return

        user_info = requests.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        st.write("DEBUG user_info =", user_info)

        # セッションに保存
        st.session_state["user_id"] = user_info.get("sub", "unknown")
        st.session_state["email"] = user_info.get("email", "no-email")
        st.success(f"{st.session_state['email']} としてログインしました！")

        # ✅ code を消してリロード
        st.query_params.clear()
        st.experimental_rerun()

    else:
        st.info(f"現在ログイン中: {st.session_state['email']}")
        if st.button("ログアウト"):
            st.session_state.clear()
            st.query_params.clear()
            st.experimental_rerun()
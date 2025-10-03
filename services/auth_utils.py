import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from services.db_utils import load_nickname, save_nickname

def login_google():
    if "user_id" not in st.session_state:
        client_id = st.secrets["auth"]["client_id"]
        client_secret = st.secrets["auth"]["client_secret"]
        redirect_uri = st.secrets["auth"]["redirect_uri"]

        oauth = OAuth2Session(
            client_id,
            client_secret,
            scope="openid email profile",
            redirect_uri=redirect_uri
        )

        query_params = st.query_params

        if "code" not in query_params:
            authorization_url, _ = oauth.create_authorization_url(
                st.secrets["auth"]["server_metadata_url"].replace(
                    ".well-known/openid-configuration", "o/oauth2/v2/auth"
                )
            )
            st.markdown(f"[Googleでログイン]({authorization_url})")
            return

        token = oauth.fetch_token(
            st.secrets["auth"]["server_metadata_url"].replace(
                ".well-known/openid-configuration", "o/oauth2/token"
            ),
            code=query_params["code"],
            redirect_uri=redirect_uri
        )

        userinfo = oauth.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token['access_token']}"}
        ).json()

        st.session_state["user_id"] = userinfo.get("sub")
        st.session_state["email"] = userinfo.get("email")
        st.session_state["nickname"] = load_nickname(st.session_state["user_id"]) or userinfo.get("name", st.session_state["email"])

        st.query_params.clear()
        st.experimental_rerun()
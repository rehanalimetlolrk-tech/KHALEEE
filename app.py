import streamlit as st
from supabase import create_client
from datetime import datetime

st.set_page_config(page_title="KHALEEE", page_icon="💬", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #0b0d12; color: #eef0f6; }
[data-testid="stSidebar"] { background: #10131b; border-right: 1px solid #252a36; }
.block-container { padding-top: 2rem; max-width: 1250px; }
h1, h2, h3 { letter-spacing: -0.03em; }
.khalee-card { background: #141923; border: 1px solid #272e3b; border-radius: 16px; padding: 18px; }
.khalee-muted { color: #929bad; font-size: 0.9rem; }
div[data-testid="stChatMessage"] { background: #151b27; border: 1px solid #262e3d; border-radius: 14px; }
.stButton > button { border-radius: 10px; border: 1px solid #343b4b; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
  <div style="width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#8b5cf6,#4f46e5);display:grid;place-items:center;font-size:22px">✦</div>
  <div>
    <div style="font-size:27px;font-weight:800;letter-spacing:3px">KHALEEE</div>
    <div style="font-size:11px;color:#929bad;letter-spacing:2px">YOUR SPACE. YOUR CONVERSATIONS.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- CONNECTION ----------
def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["anon_key"]
    return create_client(url, key)

try:
    supabase = get_supabase()
except Exception:
    st.error("KHALEEE isn't connected to Supabase yet.")
    st.markdown("""
    Add your Supabase credentials in Streamlit **App settings → Secrets**.
    Use this format:
    ```toml
    [supabase]
    url = "https://YOUR-PROJECT.supabase.co"
    anon_key = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"
    ```
    Never put a service-role key in this app or upload it to GitHub.
    """)
    st.stop()

# Restore the authenticated session on Streamlit reruns.
if "access_token" in st.session_state and "refresh_token" in st.session_state:
    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )
    except Exception:
        st.session_state.clear()

def set_login_session(auth_response):
    session = getattr(auth_response, "session", None)
    user = getattr(auth_response, "user", None)
    if session and user:
        st.session_state["access_token"] = session.access_token
        st.session_state["refresh_token"] = session.refresh_token
        st.session_state["user_id"] = user.id
        st.session_state["email"] = user.email
        metadata = getattr(user, "user_metadata", {}) or {}
        st.session_state["username"] = metadata.get("username", "member")
        st.session_state["display_name"] = metadata.get("display_name", "KHALEEE member")
        return True
    return False

def current_user_id():
    return st.session_state.get("user_id")

# ---------- AUTH SCREEN ----------
if not current_user_id():
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown("## A quieter place to connect.")
        st.markdown('<p class="khalee-muted">Private conversations, thoughtful design, and your own little corner online.</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="khalee-card">
          <div style="font-size:42px;margin-bottom:12px">✦</div>
          <div style="font-size:22px;font-weight:700">Welcome to KHALEEE</div>
          <p class="khalee-muted">A messaging space built around people, not noise.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:18px">
            <span style="background:#242039;color:#c4b5fd;padding:7px 10px;border-radius:20px;font-size:12px">One-to-one chats</span>
            <span style="background:#192a2a;color:#99f6e4;padding:7px 10px;border-radius:20px;font-size:12px">Live-ready database</span>
            <span style="background:#202638;color:#bfdbfe;padding:7px 10px;border-radius:20px;font-size:12px">Dark by design</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("### Get started")
        tab_login, tab_signup = st.tabs(["Log in", "Create account"])
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", use_container_width=True)
            if submitted:
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if set_login_session(response):
                        st.rerun()
                    st.info("If email confirmation is enabled, verify your email first, then log in.")
                except Exception as e:
                    st.error(f"Login failed: {e}")
        with tab_signup:
            with st.form("signup_form"):
                display_name = st.text_input("Display name", placeholder="Your name")
                username = st.text_input("Username", placeholder="e.g. rehan_09").strip().lower()
                email_new = st.text_input("Email address", placeholder="you@example.com")
                password_new = st.text_input("Password", type="password", help="Use a strong, unique password.")
                signup = st.form_submit_button("Create account", use_container_width=True)
            if signup:
                if not display_name or not username or not email_new or not password_new:
                    st.warning("Please complete all fields.")
                elif len(username) < 3 or not username.replace("_", "").isalnum():
                    st.warning("Username must be at least 3 characters and use only letters, numbers, or underscores.")
                elif len(password_new) < 8:
                    st.warning("Use a password with at least 8 characters.")
                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": email_new,
                            "password": password_new,
                            "options": {"data": {"username": username, "display_name": display_name}}
                        })
                        if set_login_session(response):
                            st.success("Account created.")
                            st.rerun()
                        else:
                            st.success("Account created. Check your email to confirm it, then log in.")
                    except Exception as e:
                        st.error(f"Could not create account: {e}")
    st.stop()

# ---------- APP SHELL ----------
user_id = current_user_id()
display_name = st.session_state.get("display_name", "KHALEEE member")
username = st.session_state.get("username", "member")

with st.sidebar:
    st.markdown("### ✦ KHALEEE")
    st.caption("YOUR SPACE. YOUR CONVERSATIONS.")
    st.divider()
    st.markdown(f"**{display_name}**")
    st.caption(f"@{username}")
    st.divider()
    st.markdown("**Start a conversation**")
    search_name = st.text_input("Find a username", placeholder="Type a username")
    if search_name.strip():
        try:
            found = supabase.table("profiles").select("id, username, display_name").ilike(
                "username", f"%{search_name.strip()}%"
            ).neq("id", user_id).limit(8).execute().data
            if found:
                for person in found:
                    st.write(f"**{person['display_name']}**")
                    st.caption(f"@{person['username']}")
                    if st.button("Message", key=f"msg_{person['id']}", use_container_width=True):
                        try:
                            created = supabase.table("conversations").insert({
                                "created_by": user_id, "is_group": False
                            }).execute().data[0]
                            conv_id = created["id"]
                            supabase.table("conversation_members").insert([
                                {"conversation_id": conv_id, "user_id": user_id},
                                {"conversation_id": conv_id, "user_id": person["id"]}
                            ]).execute()
                            st.session_state["active_conversation"] = conv_id
                            st.rerun()
                        except Exception as e:
                            st.error(f"Couldn't start chat: {e}")
            else:
                st.caption("No matching users found.")
        except Exception as e:
            st.error(f"Search failed: {e}")
    st.divider()
    if st.button("Log out", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        for key in ["access_token", "refresh_token", "user_id", "email", "username", "display_name", "active_conversation"]:
            st.session_state.pop(key, None)
        st.rerun()

st.markdown("## Messages")
st.caption("Your conversations, all in one place.")

# Fetch the conversations this user belongs to.
try:
    memberships = supabase.table("conversation_members").select("conversation_id").eq("user_id", user_id).execute().data
    conv_ids = [m["conversation_id"] for m in memberships]
    conversations = []
    if conv_ids:
        conversations = supabase.table("conversations").select("id, is_group, name, created_at").in_("id", conv_ids).order("created_at", desc=True).execute().data
except Exception as e:
    st.error(f"Couldn't load conversations: {e}")
    st.stop()

if not conversations:
    st.markdown("""
    <div class="khalee-card" style="text-align:center;padding:42px 20px">
      <div style="font-size:38px">✉</div>
      <h3>Your inbox is waiting</h3>
      <p class="khalee-muted">Search for a username in the left sidebar to start your first conversation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Build readable conversation labels.
labels = {}
for conv in conversations:
    try:
        members = supabase.table("conversation_members").select("user_id").eq("conversation_id", conv["id"]).execute().data
        other_ids = [m["user_id"] for m in members if m["user_id"] != user_id]
        if conv.get("is_group"):
            label = conv.get("name") or "Group chat"
        elif other_ids:
            other = supabase.table("profiles").select("display_name, username").eq("id", other_ids[0]).limit(1).execute().data
            label = f"{other[0]['display_name']} · @{other[0]['username']}" if other else "Conversation"
        else:
            label = "Conversation"
        labels[conv["id"]] = label
    except Exception:
        labels[conv["id"]] = "Conversation"

default_id = st.session_state.get("active_conversation")
if default_id not in labels:
    default_id = conversations[0]["id"]
    st.session_state["active_conversation"] = default_id

col_list, col_chat = st.columns([0.34, 0.66], gap="large")
with col_list:
    st.markdown("### Inbox")
    options = list(labels.keys())
    selected = st.radio(
        "Conversations",
        options,
        index=options.index(default_id),
        format_func=lambda x: labels.get(x, "Conversation"),
        label_visibility="collapsed"
    )
    st.session_state["active_conversation"] = selected

with col_chat:
    st.markdown(f"### {labels.get(selected, 'Conversation')}")
    st.caption("Messages are visible to members of this conversation.")

    @st.fragment(run_every="4s")
    def chat_panel(conversation_id):
        try:
            messages = supabase.table("messages").select(
                "id, sender_id, body, created_at"
            ).eq("conversation_id", conversation_id).order("created_at").limit(200).execute().data
            if not messages:
                st.info("No messages yet. Start the conversation.")
            else:
                for msg in messages:
                    is_mine = msg["sender_id"] == user_id
                    sender_label = "You" if is_mine else labels.get(conversation_id, "Member")
                    with st.chat_message("user" if is_mine else "assistant"):
                        st.markdown(msg["body"])
                        st.caption(f"{sender_label} · {msg['created_at'][:16].replace('T', ' ')}")
            prompt = st.chat_input("Write a message…", key=f"chat_input_{conversation_id}")
            if prompt and prompt.strip():
                supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "sender_id": user_id,
                    "body": prompt.strip()
                }).execute()
                st.rerun()
        except Exception as e:
            st.error(f"Couldn't load this conversation: {e}")

    chat_panel(selected)

st.caption("KHALEEE is an early build. Voice/video calls, group management, media uploads and read receipts are planned for later phases.")

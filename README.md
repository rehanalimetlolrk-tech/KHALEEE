# KHALEEE — Phase 1 starter

A dark-themed Streamlit messaging app starter with Supabase authentication and one-to-one text conversations.

## Included
- Email/password sign-up and login
- Username discovery
- One-to-one conversation creation
- Text messages stored in Supabase
- Database Row Level Security policies
- Streamlit dark styling and periodic chat refresh

## Setup

1. Create a Supabase project.
2. Open **SQL Editor** in Supabase.
3. Paste and run `database/schema.sql`.
4. In Supabase, copy the Project URL and the publishable key (or legacy anon key).
5. In Streamlit Community Cloud, add these secrets:

```toml
[supabase]
url = "https://YOUR-PROJECT.supabase.co"
anon_key = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```

For local testing, put the same TOML in `.streamlit/secrets.toml`. This file is ignored by Git.

6. Push this repository to GitHub.
7. Deploy `app.py` from Streamlit Community Cloud.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Important notes
- This is an early Phase 1 build, not a production-ready replacement for WhatsApp.
- Email confirmation may be enabled in Supabase Auth. If enabled, users must confirm their email before logging in.
- The starter does not yet include group management, attachments, read receipts, push notifications, end-to-end encryption, or voice/video calling.
- Never commit `.streamlit/secrets.toml`, passwords, or a Supabase service-role key.
- Before inviting real users, review and test database policies, abuse reporting, account recovery, privacy, and data-retention behavior.

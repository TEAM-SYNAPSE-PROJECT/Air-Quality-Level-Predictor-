"""Real Google OIDC user identity + persistent SQLite user database."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import streamlit as st

DB_PATH = Path("data/users.db")

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_subject TEXT UNIQUE,
        email TEXT UNIQUE,
        name TEXT NOT NULL,
        picture TEXT,
        first_login_utc TEXT NOT NULL,
        last_login_utc TEXT NOT NULL
    )""")
    con.commit()
    return con

def oidc_configured() -> bool:
    try:
        return bool(st.secrets.get("auth", {}).get("client_id"))
    except Exception:
        return False

def is_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False

def current_identity() -> Optional[Dict[str, Any]]:
    if not is_logged_in():
        return None
    try:
        raw = st.user.to_dict()
    except Exception:
        raw = dict(st.user)
    return {
        "provider_subject": raw.get("sub", ""),
        "email": raw.get("email", ""),
        "name": raw.get("name") or raw.get("given_name") or "Google User",
        "picture": raw.get("picture", ""),
        "email_verified": bool(raw.get("email_verified", False)),
    }

def sync_current_user() -> Optional[Dict[str, Any]]:
    identity = current_identity()
    if not identity or not identity["email"]:
        return identity
    now = datetime.now(timezone.utc).isoformat()
    con = _connect()
    row = con.execute("SELECT * FROM users WHERE email=?", (identity["email"],)).fetchone()
    if row:
        con.execute("""UPDATE users SET provider_subject=?, name=?, picture=?, last_login_utc=? WHERE email=?""",
                     (identity["provider_subject"], identity["name"], identity["picture"], now, identity["email"]))
    else:
        con.execute("""INSERT INTO users(provider_subject,email,name,picture,first_login_utc,last_login_utc)
                       VALUES(?,?,?,?,?,?)""",
                     (identity["provider_subject"], identity["email"], identity["name"], identity["picture"], now, now))
    con.commit()
    con.close()
    identity["first_login_utc"] = row["first_login_utc"] if row else now
    identity["last_login_utc"] = now
    return identity

def login_button(label="Continue with Google"):
    if oidc_configured():
        st.button("🔐 " + label, on_click=st.login, width="stretch", key="google_login_button")
    else:
        st.warning("Google sign-in is not configured yet. Add your real Google OIDC credentials to .streamlit/secrets.toml.")

def logout_button():
    if is_logged_in():
        st.button("Log out", on_click=st.logout, width="stretch", key="logout_button")

def require_login_for_download() -> bool:
    if is_logged_in():
        sync_current_user()
        return True
    st.warning("🔒 Sign in with Google to unlock downloads. This restriction is enforced by the app, not just the button label.")
    if oidc_configured():
        st.button("Sign in with Google to download", on_click=st.login, width="stretch", key="google_download_login_button")
    else:
        st.caption("Configure Google OIDC first. See .streamlit/secrets.toml.example.")
    return False

def list_users(limit=100):
    con=_connect(); rows=con.execute("SELECT email,name,picture,first_login_utc,last_login_utc FROM users ORDER BY last_login_utc DESC LIMIT ?",(limit,)).fetchall(); con.close()
    return [dict(r) for r in rows]

def save_feedback(user: Dict[str, Any], rating: int, category: str, comments: str):
    con=_connect()
    con.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        name TEXT,
        rating INTEGER NOT NULL,
        category TEXT NOT NULL,
        comments TEXT NOT NULL,
        created_utc TEXT NOT NULL
    )""")
    con.execute("INSERT INTO feedback(email,name,rating,category,comments,created_utc) VALUES(?,?,?,?,?,?)",
                (user.get("email",""),user.get("name","Google User"),rating,category,comments,datetime.now(timezone.utc).isoformat()))
    con.commit(); con.close()

def load_feedback(limit=100):
    con=_connect()
    con.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, name TEXT, rating INTEGER NOT NULL,
        category TEXT NOT NULL, comments TEXT NOT NULL, created_utc TEXT NOT NULL)""")
    rows=con.execute("SELECT created_utc,email,name,rating,category,comments FROM feedback ORDER BY id DESC LIMIT ?",(limit,)).fetchall(); con.close()
    return [dict(r) for r in rows]

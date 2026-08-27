import os
from pathlib import Path

Path(".streamlit").mkdir(exist_ok=True)

secrets = f"""[auth]
redirect_uri = "{os.environ['redirect_uri']}"
cookie_secret = "{os.environ['cookie_secret']}"
client_id = "{os.environ['client_id']}"
client_secret = "{os.environ['client_secret']}"
server_metadata_url = "{os.environ['server_metadata_url']}"
"""

Path(".streamlit/secrets.toml").write_text(
    secrets,
    encoding="utf-8"
)

print("Google OIDC secrets.toml created successfully")
print("redirect_uri:", os.environ.get("redirect_uri"))
print("server_metadata_url:", os.environ.get("server_metadata_url"))
print("client_id configured:", bool(os.environ.get("client_id")))
print("client_secret configured:", bool(os.environ.get("client_secret")))
print("cookie_secret configured:", bool(os.environ.get("cookie_secret")))
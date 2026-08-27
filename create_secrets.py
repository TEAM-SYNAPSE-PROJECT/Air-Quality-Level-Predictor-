import os
from pathlib import Path

Path(".streamlit").mkdir(exist_ok=True)

Path(".streamlit/secrets.toml").write_text(
    f'''[auth]
redirect_uri = "{os.environ["GOOGLE_REDIRECT_URI"]}"
cookie_secret = "{os.environ["GOOGLE_COOKIE_SECRET"]}"
client_id = "{os.environ["GOOGLE_CLIENT_ID"]}"
client_secret = "{os.environ["GOOGLE_CLIENT_SECRET"]}"
server_metadata_url = "{os.environ["GOOGLE_SERVER_METADATA_URL"]}"
''',
    encoding="utf-8"
)
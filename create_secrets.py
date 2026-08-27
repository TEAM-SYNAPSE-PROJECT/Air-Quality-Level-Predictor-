import os
from pathlib import Path

Path(".streamlit").mkdir(exist_ok=True)

Path(".streamlit/secrets.toml").write_text(
    f'''[auth]
redirect_uri = "{os.environ["redirect_uri"]}"
cookie_secret = "{os.environ["cookie_secret"]}"
client_id = "{os.environ["client_id"]}"
client_secret = "{os.environ["client_secret"]}"
server_metadata_url = "{os.environ["server_metadata_url"]}"
''',
    encoding="utf-8"
)
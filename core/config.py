import os
from pathlib import Path

ENV = os.getenv("ENV", "local").lower()

if ENV == "prod":
    env_file = ".env.prod"
else:
    env_file = ".env.local"

def load_env_file(filename: str):
    path = Path(filename)
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

load_env_file(env_file)

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRY_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRY_DAYS", 90))

HUD_API_TOKEN = os.getenv("HUD_API_TOKEN")
HUD_BASE_URL = os.getenv(
    "HUD_BASE_URL",
    "https://www.huduser.gov/hudapi/public/fmr",
)
import os
from django.core.wsgi import get_wsgi_application

# ✏️
from pathlib import Path
from dotenv import read_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
ENV_FILE_PATH = BASE_DIR / ".env"

read_dotenv(str(ENV_FILE_PATH))
# ✏️


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourfan.settings")

application = get_wsgi_application()

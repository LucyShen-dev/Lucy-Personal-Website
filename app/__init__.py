import os
from pathlib import Path

from flask import Flask


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def create_app():
    load_env_file()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-change-me"
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_from = os.getenv("SMTP_FROM", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_password = smtp_password.replace(" ", "").strip()

    if not smtp_user and smtp_from:
        smtp_user = smtp_from

    app.config["SMTP_HOST"] = smtp_host
    app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", "587"))
    app.config["SMTP_USER"] = smtp_user
    app.config["SMTP_PASSWORD"] = smtp_password
    app.config["SMTP_USE_TLS"] = os.getenv("SMTP_USE_TLS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    app.config["SMTP_FROM"] = smtp_from or smtp_user
    app.config["CONTACT_TO"] = os.getenv("CONTACT_TO", smtp_from or smtp_user)

    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    return app

import smtplib
import ssl
from email.message import EmailMessage

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/robots.txt")
def robots():
    site_url = current_app.config.get("SITE_URL") or request.url_root.rstrip("/")
    body = "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(site_url)
    return Response(body, mimetype="text/plain")


@main_bp.get("/sitemap.xml")
def sitemap():
    site_url = current_app.config.get("SITE_URL") or request.url_root.rstrip("/")
    entries = [
        {
            "loc": "{}/".format(site_url),
            "changefreq": "weekly",
            "priority": "1.0",
        }
    ]
    urls = "\n".join(
        "  <url>\n    <loc>{loc}</loc>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>".format(
            **entry
        )
        for entry in entries
    )
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" \
          "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" \
          "{urls}\n" \
          "</urlset>\n".format(urls=urls)
    return Response(xml, mimetype="application/xml")


def send_contact_email(name: str, sender_email: str, message: str) -> None:
    host = current_app.config.get("SMTP_HOST")
    port = current_app.config.get("SMTP_PORT", 587)
    user = current_app.config.get("SMTP_USER")
    password = current_app.config.get("SMTP_PASSWORD")
    use_tls = current_app.config.get("SMTP_USE_TLS", True)
    from_addr = current_app.config.get("SMTP_FROM") or user
    to_addr = current_app.config.get("CONTACT_TO")

    if not host or not user or not password or not to_addr:
        raise RuntimeError("SMTP is not configured.")
    if "@" in host:
        raise ValueError("SMTP_HOST should be a server like smtp.gmail.com, not an email.")

    msg = EmailMessage()
    msg["Subject"] = f"New contact form message from {name}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Reply-To"] = sender_email
    msg.set_content(
        "Name: {name}\nEmail: {email}\n\n{body}\n".format(
            name=name, email=sender_email, body=message
        )
    )

    with smtplib.SMTP(host, port) as server:
        server.set_debuglevel(1)
        server.ehlo()
        if use_tls:
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
        server.login(user, password)
        server.send_message(msg)


@main_bp.post("/contact")
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill out all fields.", "error")
        return redirect(url_for("main.index") + "#contact")

    try:
        send_contact_email(name, email, message)
    except smtplib.SMTPAuthenticationError:
        flash("Email login failed. Check SMTP username and app password.", "error")
        return redirect(url_for("main.index") + "#contact")
    except smtplib.SMTPConnectError:
        flash("Could not connect to the SMTP server. Check host/port.", "error")
        return redirect(url_for("main.index") + "#contact")
    except Exception as exc:
        current_app.logger.exception("Contact email failed")
        flash(f"Sorry, there was a problem sending your message: {exc}", "error")
        return redirect(url_for("main.index") + "#contact")

    flash("Thanks, I will get back to you soon.", "success")
    return redirect(url_for("main.index") + "#contact")

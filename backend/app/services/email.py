import logging
from textwrap import dedent

import requests
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    """Raised when an email provider fails to deliver a message."""


def _send_via_sendgrid(to_email: str, subject: str, plain: str, html: str) -> None:
    if not settings.SENDGRID_API_KEY:
        raise EmailDeliveryError("SENDGRID_API_KEY is not configured")

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.SENDGRID_FROM_EMAIL},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": plain},
            {"type": "text/html", "value": html},
        ],
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if response.status_code >= 300:
            raise EmailDeliveryError(
                f"SendGrid responded with {response.status_code}: {response.text}"
            )
    except requests.RequestException as exc:
        raise EmailDeliveryError(str(exc)) from exc


def _send_via_acs(
    to_email: str,
    subject: str,
    plain: str,
    html: str,
    attachments: list | None = None
) -> None:
    if not settings.ACS_CONNECTION_STRING:
        raise EmailDeliveryError("ACS_CONNECTION_STRING is not configured")
    if not settings.ACS_SENDER_EMAIL:
        raise EmailDeliveryError("ACS_SENDER_EMAIL is not configured")

    try:
        from azure.communication.email import EmailClient  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise EmailDeliveryError(
            "azure-communication-email must be installed when EMAIL_PROVIDER=acs"
        ) from exc

    message = {
        "senderAddress": settings.ACS_SENDER_EMAIL,
        "recipients": {"to": [{"address": to_email}]},
        "content": {
            "subject": subject,
            "plainText": plain,
            "html": html,
        },
    }

    if attachments:
        message["attachments"] = attachments

    try:
        client = EmailClient.from_connection_string(settings.ACS_CONNECTION_STRING)
        poller = client.begin_send(message)
        poller.result()  # wait for completion
    except Exception as exc:  # pragma: no cover - network call
        raise EmailDeliveryError(str(exc)) from exc


def send_email(to_email: str, subject: str, plain_body: str, html_body: str) -> None:
    """
    Send an email using the configured provider.

    Default behaviour (EMAIL_PROVIDER=console) simply logs the message so
    local development and automated tests are deterministic.
    """
    provider = settings.EMAIL_PROVIDER.lower()
    if provider == "sendgrid":
        _send_via_sendgrid(to_email, subject, plain_body, html_body)
    elif provider in {"acs", "azure"}:
        _send_via_acs(to_email, subject, plain_body, html_body)
    else:
        logger.info(
            "EMAIL (console) to %s\nSubject: %s\n%s",
            to_email,
            subject,
            plain_body,
        )


def send_registration_verification_email(to_email: str, verification_link: str) -> None:
    subject = "Verify your AADA LMS email"
    plain = dedent(
        f"""
        Welcome to the AADA Student Portal!

        Please verify your email address by clicking the link below:
        {verification_link}

        The link expires in {settings.REGISTRATION_EMAIL_EXPIRE_MINUTES} minutes.
        If you did not request this, you can ignore this message.
        """
    ).strip()

    html = dedent(
        f"""
        <p>Welcome to the <strong>AADA Student Portal</strong>!</p>
        <p>Click the button below to verify your email address and continue your registration.</p>
        <p style="text-align:center;margin:24px 0">
          <a href="{verification_link}"
             style="background:#d4af37;color:#000;padding:12px 24px;text-decoration:none;border-radius:6px;">
            Verify email
          </a>
        </p>
        <p>This link expires in {settings.REGISTRATION_EMAIL_EXPIRE_MINUTES} minutes.</p>
        <p>If you did not request this, you can safely ignore this message.</p>
        """
    ).strip()

    send_email(to_email, subject, plain, html)


def send_enrollment_agreement_email(
    to_email: str,
    signer_name: str,
    course_label: str,
    signing_url: str,
    token_expires_at: datetime
) -> None:
    """Send signing link for an enrollment agreement."""
    friendly_name = signer_name or "there"
    expires_at = token_expires_at.astimezone(timezone.utc).strftime("%b %d, %Y %H:%M %Z")

    subject = f"Your {course_label} enrollment agreement is ready"
    plain = dedent(
        f"""
        Hi {friendly_name},

        Your enrollment agreement for the {course_label} is ready to review and sign.
        Use the secure link below to complete the form online:

        {signing_url}

        The link expires on {expires_at}. If you have questions, reply to this email or
        contact the AADA admissions team.

        Thank you,
        Atlanta Academy of Dental Assisting Admissions
        """
    ).strip()

    html = dedent(
        f"""
        <p>Hi {friendly_name},</p>
        <p>Your enrollment agreement for the <strong>{course_label}</strong> is ready to review and sign.</p>
        <p style="text-align:center;margin:24px 0">
          <a href="{signing_url}"
             style="background:#d4af37;color:#000;padding:14px 32px;text-decoration:none;border-radius:6px;">
            Review and sign agreement
          </a>
        </p>
        <p>This secure link expires on <strong>{expires_at}</strong>. If you have any questions,
        please reply to this email or contact the AADA admissions team.</p>
        <p>Thank you,<br/>Atlanta Academy of Dental Assisting Admissions</p>
        """
    ).strip()

    send_email(to_email, subject, plain, html)


def send_completed_agreement_email(
    to_email: str,
    signer_name: str,
    course_label: str,
    pdf_content: bytes,
    pdf_filename: str
) -> None:
    """Send the completed and counter-signed enrollment agreement PDF to the signer."""
    import base64

    friendly_name = signer_name or "there"

    subject = f"Your signed {course_label} enrollment agreement"
    plain = dedent(
        f"""
        Hi {friendly_name},

        Great news! Your enrollment agreement for the {course_label} has been fully executed.
        The attached PDF contains your signed agreement with the AADA counter-signature.

        Please save this document for your records. It serves as proof of your enrollment terms
        and is legally binding.

        If you have any questions, please contact the AADA admissions team.

        Welcome to AADA!
        Atlanta Academy of Dental Assisting
        """
    ).strip()

    html = dedent(
        f"""
        <p>Hi {friendly_name},</p>
        <p><strong>Great news!</strong> Your enrollment agreement for the <strong>{course_label}</strong>
        has been fully executed.</p>
        <p>The attached PDF contains your signed agreement with the AADA counter-signature.
        Please save this document for your records. It serves as proof of your enrollment terms
        and is legally binding.</p>
        <p>If you have any questions, please contact the AADA admissions team.</p>
        <p><strong>Welcome to AADA!</strong><br/>Atlanta Academy of Dental Assisting</p>
        """
    ).strip()

    provider = settings.EMAIL_PROVIDER.lower()
    if provider in {"acs", "azure"}:
        # ACS attachment format
        attachments = [
            {
                "name": pdf_filename,
                "contentType": "application/pdf",
                "contentInBase64": base64.b64encode(pdf_content).decode("utf-8"),
            }
        ]
        _send_via_acs(to_email, subject, plain, html, attachments)
    else:
        # For console/development, just log the email
        logger.info(
            "EMAIL (console) to %s\nSubject: %s\n%s\nAttachment: %s (%d bytes)",
            to_email,
            subject,
            plain,
            pdf_filename,
            len(pdf_content),
        )

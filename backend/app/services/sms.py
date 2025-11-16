"""
SMS Service using Azure Communication Services.

Provides SMS messaging capabilities for notifications and alerts.
Requires toll-free verification before production use.
"""
import logging
from textwrap import dedent

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSDeliveryError(RuntimeError):
    """Raised when SMS provider fails to deliver a message."""


def _send_via_acs(to_phone: str, message: str) -> str:
    """
    Send SMS via Azure Communication Services.

    Returns the message_id on success.
    """
    if not settings.ACS_CONNECTION_STRING:
        raise SMSDeliveryError("ACS_CONNECTION_STRING is not configured")
    if not settings.ACS_SENDER_PHONE:
        raise SMSDeliveryError("ACS_SENDER_PHONE is not configured")

    try:
        from azure.communication.sms import SmsClient  # type: ignore[import]
    except ImportError as exc:
        raise SMSDeliveryError(
            "azure-communication-sms must be installed for SMS support"
        ) from exc

    # Normalize phone number to E.164 format
    phone = to_phone.strip()
    if not phone.startswith("+"):
        # Assume US number if no country code
        phone = f"+1{phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}"

    try:
        client = SmsClient.from_connection_string(settings.ACS_CONNECTION_STRING)
        response = client.send(
            from_=settings.ACS_SENDER_PHONE,
            to=phone,
            message=message,
            enable_delivery_report=True,
        )

        # Response is a list of results (we're sending to one number)
        result = response[0]
        if not result.successful:
            raise SMSDeliveryError(
                f"SMS send failed: {result.error_message} (code: {result.http_status_code})"
            )

        logger.info(f"SMS sent successfully to {phone}, message_id={result.message_id}")
        return result.message_id

    except SMSDeliveryError:
        raise
    except Exception as exc:
        raise SMSDeliveryError(str(exc)) from exc


def send_sms(to_phone: str, message: str) -> str | None:
    """
    Send an SMS message using the configured provider.

    Default behaviour (no ACS_SENDER_PHONE) simply logs the message.
    Returns message_id on success, None for console mode.
    """
    if not settings.ACS_SENDER_PHONE:
        # Console mode for development
        logger.info(
            "SMS (console) to %s:\n%s",
            to_phone,
            message,
        )
        return None

    return _send_via_acs(to_phone, message)


def send_enrollment_agreement_sms(
    to_phone: str,
    signer_name: str,
    course_label: str,
    signing_url: str
) -> str | None:
    """Send SMS notification with enrollment agreement signing link."""
    friendly_name = signer_name.split()[0] if signer_name else "there"

    message = dedent(f"""
        Hi {friendly_name}! Your AADA {course_label} enrollment agreement is ready to sign.
        Review and sign here: {signing_url}
        Link expires in 7 days. Reply STOP to opt out.
    """).strip()

    return send_sms(to_phone, message)


def send_completed_agreement_sms(
    to_phone: str,
    signer_name: str,
    course_label: str
) -> str | None:
    """Send SMS notification that enrollment agreement is complete."""
    friendly_name = signer_name.split()[0] if signer_name else "there"

    message = dedent(f"""
        Congratulations {friendly_name}! Your AADA {course_label} enrollment agreement has been fully executed.
        Check your email for the signed PDF. Welcome to AADA!
        Reply STOP to opt out.
    """).strip()

    return send_sms(to_phone, message)


def send_appointment_reminder_sms(
    to_phone: str,
    name: str,
    appointment_type: str,
    date_time: str,
    location: str
) -> str | None:
    """Send appointment reminder SMS."""
    friendly_name = name.split()[0] if name else "there"

    message = dedent(f"""
        Hi {friendly_name}! Reminder: Your AADA {appointment_type} is scheduled for {date_time} at {location}.
        Reply STOP to opt out.
    """).strip()

    return send_sms(to_phone, message)


def send_class_reminder_sms(
    to_phone: str,
    name: str,
    class_name: str,
    date_time: str
) -> str | None:
    """Send class reminder SMS."""
    friendly_name = name.split()[0] if name else "there"

    message = dedent(f"""
        Hi {friendly_name}! Reminder: {class_name} starts {date_time}. See you there!
        Reply STOP to opt out.
    """).strip()

    return send_sms(to_phone, message)

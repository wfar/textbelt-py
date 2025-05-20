import os

import pytest

from textbelt_py import OTPGenerateRequest, OTPVerificationRequest, SMSRequest, TextbeltClient
from textbelt_py.models import Status


@pytest.fixture
def textbelt_client() -> TextbeltClient:
    test_api_key = f"{os.environ['TEXTBELT_API_KEY']}_test"
    return TextbeltClient(test_api_key)


def test_send_sms(textbelt_client: TextbeltClient) -> None:
    test_sms_request = SMSRequest(
        phone=os.environ["TEST_PHONE_NUMBER"],
        message="Test Message",
    )

    resp = textbelt_client.send_sms(test_sms_request)

    assert resp is not None
    assert resp.success is True


def test_send_sms_with_reply_webhook(textbelt_client: TextbeltClient) -> None:
    test_sms_request = SMSRequest(
        phone=os.environ["TEST_PHONE_NUMBER"],
        message="Test Message",
        reply_webhook_url="https://my.site/api/handleSmsReply",
        webhook_data="Custome webhook data",
    )

    resp = textbelt_client.send_sms(test_sms_request)

    assert resp is not None
    assert resp.success is True


def test_check_sms_delivery_status(textbelt_client: TextbeltClient) -> None:
    test_text_id = "1234567890"

    resp = textbelt_client.check_sms_delivery_status(test_text_id)

    assert resp is not None
    assert resp.status == Status.UNKNOWN


def test_send_otp(textbelt_client: TextbeltClient) -> None:
    test_otp_generate_request = OTPGenerateRequest(
        phone=os.environ["TEST_PHONE_NUMBER"],
        user_id="test_userid_12345",
    )

    resp = textbelt_client.send_otp(test_otp_generate_request)

    assert resp is not None
    assert resp.success is True


def test_verify_otp(textbelt_client: TextbeltClient) -> None:
    test_otp_generate_request = OTPVerificationRequest(
        otp="121314",
        user_id="test_userid_12345",
    )

    resp = textbelt_client.verify_otp(test_otp_generate_request)

    assert resp is not None
    assert resp.success is True
    assert resp.is_valid_otp is False


def test_check_credit_balance(textbelt_client: TextbeltClient) -> None:
    resp = textbelt_client.check_credit_balance()

    assert resp is not None
    assert resp.success is True

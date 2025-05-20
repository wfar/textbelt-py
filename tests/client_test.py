import datetime
import hashlib
import hmac
import json
import time

import pytest
import responses
from pydantic import ValidationError
from requests.exceptions import HTTPError

from textbelt_py import (
    CreditBalanceResponse,
    OTPGenerateRequest,
    OTPGenerateResponse,
    OTPVerificationRequest,
    OTPVerificationResponse,
    SMSRequest,
    SMSResponse,
    SMSStatusResponse,
    TextbeltClient,
    TextbeltException,
)
from textbelt_py.models import Status

TEST_API_KEY = "test_api_key"


@pytest.fixture
def textbelt_client() -> TextbeltClient:
    return TextbeltClient(TEST_API_KEY, None)


@responses.activate
def test_send_sms(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="POST",
        url="https://textbelt.com/text",
        json={"success": "true", "quotaRemaining": 40, "textId": "12345"},
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "phone": "2123124123",
                    "message": "Hello World",
                    "sender": "test_sender@textbelt.com",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    sms_req = SMSRequest(
        phone="2123124123",
        message="Hello World",
        sender="test_sender@textbelt.com",
    )

    sms_res = textbelt_client.send_sms(sms_req)

    assert sms_res is not None and isinstance(sms_res, SMSResponse), (
        "Expected an SMS response to be returned"
    )
    assert sms_res.success is True
    assert sms_res.text_id == "12345"
    assert sms_res.quota_remaining == 40
    assert sms_res.error is None


@responses.activate
def test_send_sms__raises_textbelt_exception(
    textbelt_client: TextbeltClient,
) -> None:
    responses.post("https://textbelt.com/text", body=HTTPError("Test HTTP Error"))
    sms_req = SMSRequest(
        phone="2123124123",
        message="Hello World",
        sender="test_sender@textbelt.com",
    )

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.send_sms(sms_req)

    assert (
        ex_info.value.message
        == "Requests error occurred (Type = <class 'requests.exceptions.HTTPError'> | Message = Test HTTP Error)"
    )
    assert isinstance(ex_info.value.exception, HTTPError)
    assert ex_info.value.ex_type is HTTPError


@responses.activate
def test_send_sms_with_reply_webhook(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="POST",
        url="https://textbelt.com/text",
        json={"success": "true", "quotaRemaining": 40, "textId": "12345"},
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "phone": "2123124123",
                    "message": "Hello World",
                    "sender": "test_sender@textbelt.com",
                    "replyWebhookUrl": "https://my.site/api/handleSmsReply",
                    "webhookData": "custom webhook data",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    sms_req = SMSRequest(
        phone="2123124123",
        message="Hello World",
        reply_webhook_url="https://my.site/api/handleSmsReply",
        webhook_data="custom webhook data",
        sender="test_sender@textbelt.com",
    )

    sms_res = textbelt_client.send_sms(sms_req)

    assert sms_res is not None and isinstance(sms_res, SMSResponse), (
        "Expected an SMS response to be returned"
    )
    assert sms_res.success is True
    assert sms_res.text_id == "12345"
    assert sms_res.quota_remaining == 40
    assert sms_res.error is None


@responses.activate
def test_send_sms_with_reply_webhook__raises_textbelt_exception(
    textbelt_client: TextbeltClient,
) -> None:
    responses.post("https://textbelt.com/text", body=HTTPError("Test HTTP Error"))
    sms_req = SMSRequest(
        phone="2123124123",
        message="Hello World",
        reply_webhook_url="https://my.site/api/handleSmsReply",
        webhook_data="custom webhook data",
        sender="test_sender@textbelt.com",
    )

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.send_sms(sms_req)

    assert (
        ex_info.value.message
        == "Requests error occurred (Type = <class 'requests.exceptions.HTTPError'> | Message = Test HTTP Error)"
    )
    assert isinstance(ex_info.value.exception, HTTPError)
    assert ex_info.value.ex_type is HTTPError


def test_verify_webhook__invalid_timestamp(textbelt_client: TextbeltClient) -> None:
    current_time = int(time.time())
    invalid_timestamp = current_time - datetime.timedelta(minutes=100).seconds
    payload = json.dumps(
        {
            "textId": "123456",
            "fromNumber": "+1555123456",
            "text": "Here is my reply",
            "data": "my custom data",
        },
    )
    signature = hmac.new(
        b"test_api_key",
        (str(current_time) + payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    is_valid, webhook_payload = textbelt_client.verify_webhook(
        str(invalid_timestamp),
        signature,
        payload,
    )

    assert is_valid is False, "Expected result to be False since timestamp is invalid"
    assert webhook_payload is None


def test_verify_webhook__invalid_signature(textbelt_client: TextbeltClient) -> None:
    current_time = int(time.time())
    timestamp = current_time - datetime.timedelta(minutes=5).seconds
    payload = json.dumps(
        {
            "textId": "123456",
            "fromNumber": "+1555123456",
            "text": "Here is my reply",
            "data": "my custom data",
        },
    )
    signature = hmac.new(
        b"test_api_key",
        (str(current_time) + json.dumps({"textId": "invalid"})).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    is_valid, webhook_payload = textbelt_client.verify_webhook(str(timestamp), signature, payload)

    assert is_valid is False, "Expected result to be False since signatures do not match"
    assert webhook_payload is None


def test_verify_webhook(textbelt_client: TextbeltClient) -> None:
    current_time = int(time.time())
    timestamp = current_time - datetime.timedelta(minutes=5).seconds
    payload = json.dumps(
        {
            "textId": "123456",
            "fromNumber": "+1555123456",
            "text": "Here is my reply",
            "data": "my custom data",
        },
    )
    signature = hmac.new(
        b"test_api_key",
        (str(timestamp) + payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    is_valid, webhook_payload = textbelt_client.verify_webhook(str(timestamp), signature, payload)

    assert is_valid is True
    assert webhook_payload is not None
    assert webhook_payload.text_id == "123456"
    assert webhook_payload.from_number == "+1555123456"
    assert webhook_payload.text == "Here is my reply"
    assert webhook_payload.data == "my custom data"


def test_verify_webhook__raises_textbelt_exception(textbelt_client: TextbeltClient) -> None:
    current_time = int(time.time())
    timestamp = current_time - datetime.timedelta(minutes=5).seconds
    payload = json.dumps({})
    signature = hmac.new(
        b"test_api_key",
        (str(timestamp) + payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.verify_webhook(str(timestamp), signature, payload)

    assert (
        "Pydantic error occurred (Type = <class 'pydantic_core._pydantic_core.ValidationError'> | Message = 3 validation errors for WebhookPayload"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, ValidationError)
    assert ex_info.value.ex_type is ValidationError


status_test_cases = [s.value for s in Status]


@pytest.mark.parametrize("expected_status", status_test_cases)
@responses.activate
def test_check_sms_delivery_status(
    textbelt_client: TextbeltClient,
    expected_status: Status,
) -> None:
    text_id = "589290745829430284"

    resp = responses.Response(
        method="GET",
        url=f"https://textbelt.com/status/{text_id}",
        json={"status": expected_status},
    )
    responses.add(resp)

    sms_status_response = textbelt_client.check_sms_delivery_status(text_id)

    assert sms_status_response is not None and isinstance(sms_status_response, SMSStatusResponse), (
        "Expected to get an SMS status response to be returned"
    )
    assert sms_status_response.status == expected_status


@responses.activate
def test_check_sms_delivery_status__raises_textbelt_exception(
    textbelt_client: TextbeltClient,
) -> None:
    text_id = "589290745829430284"

    resp = responses.Response(
        method="GET",
        url=f"https://textbelt.com/status/{text_id}",
        json={"status": "INVALID_STATUS"},
    )
    responses.add(resp)

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.check_sms_delivery_status(text_id)

    assert (
        "Pydantic error occurred (Type = <class 'pydantic_core._pydantic_core.ValidationError'> | Message = 1 validation error for SMSStatusResponse"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, ValidationError)
    assert ex_info.value.ex_type is ValidationError


@responses.activate
def test_send_otp(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="POST",
        url="https://textbelt.com/otp/generate",
        json={"success": "true", "textId": "1234", "quotaRemaining": 70, "otp": "672383"},
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "phone": "+15557727420",
                    "userid": "test_userid_12345",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    otp_generate_req = OTPGenerateRequest(phone="+15557727420", user_id="test_userid_12345")

    otp_generate_res = textbelt_client.send_otp(otp_generate_req)

    assert otp_generate_res is not None and isinstance(otp_generate_res, OTPGenerateResponse), (
        "Expected an OTP generate response to be returned"
    )
    assert otp_generate_res.success is True
    assert otp_generate_res.text_id == "1234"
    assert otp_generate_res.quota_remaining == 70
    assert otp_generate_res.otp == "672383"


@responses.activate
def test_send_otp__raises_textbelt_exception(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="POST",
        url="https://textbelt.com/otp/generate",
        json={"success": "invalid"},
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "phone": "+15557727420",
                    "userid": "test_userid_12345",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    otp_generate_req = OTPGenerateRequest(phone="+15557727420", user_id="test_userid_12345")

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.send_otp(otp_generate_req)

    assert (
        "Pydantic error occurred (Type = <class 'pydantic_core._pydantic_core.ValidationError'> | Message = 3 validation errors for OTPGenerateResponse"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, ValidationError)
    assert ex_info.value.ex_type is ValidationError


@responses.activate
def test_verify_otp(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="GET",
        url="https://textbelt.com/otp/verify",
        json={"success": "true", "isValidOtp": "true"},
        match=[
            responses.matchers.query_param_matcher(
                {
                    "otp": "321654",
                    "userid": "test_userid_12345",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    otp_verification_req = OTPVerificationRequest(otp="321654", user_id="test_userid_12345")

    otp_verification_res = textbelt_client.verify_otp(otp_verification_req)

    assert otp_verification_res is not None and isinstance(
        otp_verification_res,
        OTPVerificationResponse,
    ), "Expected an OTP verification response to be returned"
    assert otp_verification_res.success is True
    assert otp_verification_res.is_valid_otp is True


@responses.activate
def test_verify_otp__raises_textbelt_exception(textbelt_client: TextbeltClient) -> None:
    exp_resp = responses.Response(
        method="GET",
        url="https://textbelt.com/otp/verify",
        body=Exception("Test Exception"),
        match=[
            responses.matchers.query_param_matcher(
                {
                    "otp": "321654",
                    "userid": "test_userid_12345",
                    "key": "test_api_key",
                },
            ),
        ],
    )
    responses.add(exp_resp)

    otp_verification_req = OTPVerificationRequest(otp="321654", user_id="test_userid_12345")

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.verify_otp(otp_verification_req)

    assert (
        "Unexpected error occurred (Type = <class 'Exception'> | Message = Test Exception)"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, Exception)
    assert ex_info.value.ex_type is Exception


@responses.activate
def test_check_credit_balance(textbelt_client: TextbeltClient) -> None:
    resp = responses.Response(
        method="GET",
        url=f"https://textbelt.com/quota/{TEST_API_KEY}",
        json={"success": True, "quotaRemaining": 100},
    )
    responses.add(resp)

    credit_balance_response = textbelt_client.check_credit_balance()

    assert credit_balance_response is not None and isinstance(
        credit_balance_response, CreditBalanceResponse
    ), "Expected a credit balance response to be returned"
    assert credit_balance_response.success is True
    assert credit_balance_response.quota_remaining == 100


@responses.activate
def test_check_credit_balance__raises_textbelt_exception(textbelt_client: TextbeltClient) -> None:
    resp = responses.Response(
        method="GET",
        url=f"https://textbelt.com/quota/{TEST_API_KEY}",
        body=Exception("Test Exception"),
    )
    responses.add(resp)

    with pytest.raises(TextbeltException) as ex_info:
        textbelt_client.check_credit_balance()

    assert (
        "Unexpected error occurred (Type = <class 'Exception'> | Message = Test Exception)"
        in ex_info.value.message
    )
    assert isinstance(ex_info.value.exception, Exception)
    assert ex_info.value.ex_type is Exception

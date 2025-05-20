import datetime
import hashlib
import hmac
import json
import time

from requests import Session
from requests.adapters import HTTPAdapter, Retry

from .decorators import exception_handler_decorator
from .models import (
    CreditBalanceResponse,
    OTPGenerateRequest,
    OTPGenerateResponse,
    OTPVerificationRequest,
    OTPVerificationResponse,
    SMSRequest,
    SMSResponse,
    SMSStatusResponse,
    WebhookPayload,
)


class TextbeltClient:
    """
    Client class to interact with Textbelt API.

    Requires a Textbelt API key as well as a `requests.Session`
    object for handling http requests.

    If `session` is not provided, creates a new `session`
    configured to make 3 retry attempts with backoff factor of 1.

    Attributes:
        api_key (str): required Textbelt API key.
        session (Session): `requests.Session` object used to make http requests.
    """

    TEXTBELT_API_BASE_URL = "https://textbelt.com"

    def __init__(self, api_key: str, session: Session | None = None) -> None:
        """
        Initialize Textbelt client instance.

        Args:
            api_key (str): required Textbelt API key.
            session (Session | None): optional `Session` used to make http requests.
        """

        self.api_key = api_key
        self.session = session if session else self._create_session()

    @exception_handler_decorator
    def send_sms(self, sms_request: SMSRequest) -> SMSResponse:
        """
        Send an SMS to a phone number.

        Takes an SMSRequest containing the phone, message,
        and optionally, the sender, and makes a POST request
        to Textbelt API to send a message.

        If request contains a reply webhook url, the Textbelt API
        will handle text replies from recipient by making
        a callback to the given url.

        Args:
            sms_request (SMSRequest): request args used to create
                payload to send an SMS from Textbelt.

        Returns:
            SMSResponse: contains the response data
                returned from the API call made to Textbelt.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        send_sms_url = f"{self.TEXTBELT_API_BASE_URL}/text"

        payload = sms_request.model_dump(exclude_unset=True, by_alias=True)
        payload["key"] = self.api_key

        resp = self.session.post(send_sms_url, payload)

        resp.raise_for_status()

        json_resp = resp.json()

        return SMSResponse.model_validate(json_resp)

    @exception_handler_decorator
    def verify_webhook(
        self, request_timestamp: str, request_signature: str, request_payload: str
    ) -> tuple[bool, WebhookPayload | None]:
        """
        Verify incoming Textbelt webhook.

        Confirms the reply webhook request made by Textbelt
        is not forged or expired, and is a valid request.
        Verification is done by first, checking the request
        timestamp is within the 15 minute time limit. Then compares
        the request signature with the calculated signature for a match.

        Args:
            request_timestamp (str): UNIX timestamp as string
                from webhook request headers (`X-textbelt-timestamp`).
            request_signature (str): hmac signature as string
                from webhook request headers (`X-textbelt-signature`)
            request_payload (str): raw json payload as string
                from webhook request body.

        Returns:
            Tuple[bool, WebhookPayload]: denotes the verification status
                of webhook. If webhook not valid, returns `False` and `None`.
                Otherwise returns `True` and a `WebhookPayload` containing the parsed json
                payload data.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        timestamp = int(request_timestamp)
        current_time = int(time.time())

        # time limit for a valid webhook request is 15 minutes.
        if current_time - timestamp > datetime.timedelta(minutes=15).seconds:
            return False, None

        signature = hmac.new(
            self.api_key.encode("utf-8"),
            (request_timestamp + request_payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        signature_is_valid = hmac.compare_digest(request_signature, signature)
        if not signature_is_valid:
            return False, None

        payload_json = json.loads(request_payload)

        return True, WebhookPayload.model_validate(payload_json)

    @exception_handler_decorator
    def check_sms_delivery_status(self, text_id: str) -> SMSStatusResponse:
        """
        Check delivery status of an SMS.

        Determines the delivery status of an SMS message
        that was sent by Textbelt. Uses the given `text_id`
        to find the status.

        Args:
            text_id (str): id of the SMS message to check status for.

        Returns:
            SMSStatusResponse: contains the text message's
                current delivery status.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        sms_status_url = f"{self.TEXTBELT_API_BASE_URL}/status/{text_id}"

        resp = self.session.get(sms_status_url)

        resp.raise_for_status()

        json_resp = resp.json()

        return SMSStatusResponse.model_validate(json_resp)

    @exception_handler_decorator
    def send_otp(self, otp_generate_request: OTPGenerateRequest) -> OTPGenerateResponse:
        """
        Send a one-time password to a phone number.

        Takes an `OTPGenerateRequest` containing the `phone` and `user_id`,
        to send an OTP via POST request to Textbelt API.

        If the `lifetime`, `length`, and `message` are not provided, they default
        to 180 seconds, 6 digits, and `"Your verification code is XXX"`,
        respectively.

        Args:
            otp_generate_request (OTPGenerateRequest): request args used to create
                payload to send an OTP from Textbelt.

        Returns:
            OTPGenerateResponse: contains the response data
                returned from the API call made to Textbelt.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        otp_generate_url = f"{self.TEXTBELT_API_BASE_URL}/otp/generate"

        payload = otp_generate_request.model_dump(exclude_unset=True, by_alias=True)
        payload["key"] = self.api_key

        resp = self.session.post(otp_generate_url, payload)

        resp.raise_for_status()

        json_resp = resp.json()

        return OTPGenerateResponse.model_validate(json_resp)

    @exception_handler_decorator
    def verify_otp(
        self, otp_verification_request: OTPVerificationRequest
    ) -> OTPVerificationResponse:
        """
        Verify one-time password from the user is valid.

        Takes an `OTPVerificationRequest` containing the `otp`
        and `user_id` associated with the otp, and determines
        whether the one-time password is valid for that given
        user.

        Args:
            otp_verification_request (OTPVerificationRequest): request args used
                to create payload to verify an OTP for a user from Textbelt.

        Returns:
            OTPVerificationResponse: contains the response data
                returned from the API call made to Textbelt.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        otp_verification_url = f"{self.TEXTBELT_API_BASE_URL}/otp/verify"

        params = otp_verification_request.model_dump(by_alias=True)
        params["key"] = self.api_key

        resp = self.session.get(otp_verification_url, params=params)

        resp.raise_for_status()

        json_resp = resp.json()

        return OTPVerificationResponse.model_validate(json_resp)

    @exception_handler_decorator
    def check_credit_balance(self) -> CreditBalanceResponse:
        """
        Check the remaining credit balance on the account
        associated with the API key.

        Returns:
            CreditBalanceResponse: contains the total amount
                of credits/quota remaining.

        Raises:
            TextbeltException: raised on any exceptions that occur during
                execution.
        """

        check_credit_balance_url = f"{self.TEXTBELT_API_BASE_URL}/quota/{self.api_key}"

        resp = self.session.get(check_credit_balance_url)

        resp.raise_for_status()

        json_resp = resp.json()

        return CreditBalanceResponse.model_validate(json_resp)

    def _create_session(self) -> Session:
        retry = Retry(total=3, backoff_factor=1)
        retry_adapter = HTTPAdapter(max_retries=retry)
        session = Session()
        session.mount("http://", retry_adapter)
        session.mount("https://", retry_adapter)

        return session

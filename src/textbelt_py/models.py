from enum import Enum

from pydantic import BaseModel, Field


class SMSRequest(BaseModel):
    """
    SMS request data used to send a text message.

    Pydantic model to represent the request
    parameters required to send an SMS
    via Textbelt API.

    Attributes:
        phone (str): the recipient phone number in `E.164` format.
        message (str): text message content to send.
        sender (str | None): optional name of the entity sending SMS.
        reply_webhook_url (str | None): optional webhook url to call
            when recipient responds to the SMS.
        webhook_data (str | None): optional data to send in the
            reply webhook callback. Max length of 100 characters.
    """

    phone: str
    message: str
    sender: str | None = None
    reply_webhook_url: str | None = Field(default=None, serialization_alias="replyWebhookUrl")
    webhook_data: str | None = Field(
        default=None,
        max_length=100,
        serialization_alias="webhookData",
    )


class SMSResponse(BaseModel):
    """
    SMS response data returned when text message is sent.

    Pydantic model to represent the response
    received from Textbelt API after sending
    an SMS message.

    Attributes:
        success (bool): `True` when message sent successfully,
            `False` otherwise.
        quota_remaining (int): number of messages remaining on account.
        text_id (str | None): optional id of the text sent to recipient when
            `success` is `True`.
        error (str | None): optional error message when `success` is `False`.
    """

    success: bool
    quota_remaining: int = Field(alias="quotaRemaining")
    text_id: str | None = Field(default=None, alias="textId")
    error: str | None = None


class WebhookPayload(BaseModel):
    """
    Reply webhook payload.

    Pydantic model to represent the payload
    json request body sent to the webhook url
    when handling recipient response to
    an SMS message.

    Attributes:
        text_id (str): the id of the original text that began the conversation.
        from_number (str): the phone number of the user that sent the reply.
        text (str): the message content of the responder's reply.
        data (str): the custom webhook data set when original SMS sent to recipient.
            Max length of 100 characters.
    """

    text_id: str = Field(alias="textId")
    from_number: str = Field(alias="fromNumber")
    text: str
    data: str | None = Field(default=None, max_length=100)


class Status(str, Enum):
    """
    Enum representing all possible statuses
    of a text message.
    """

    DELIVERED = "DELIVERED"  # Carrier has confirmed sending
    SENT = "SENT"  # Sent to carrier but confirmation receipt not available
    SENDING = "SENDING"  # Queued or dispatched to carrier
    FAILED = "FAILED"  # Not received
    UNKNOWN = "UNKNOWN"  # Could not determine status


class SMSStatusResponse(BaseModel):
    """
    SMS status response data returned when
    checking the status of an SMS.

    Pydantic model to represent the response
    received from Textbelt API when checking
    the status of an SMS.

    Attributes:
        status (Status): the current status of the SMS message.
    """

    status: Status


class OTPGenerateRequest(BaseModel):
    """
    Generate one-time password request data.

    Pydantic model to represent the request
    parameters required to generate and send
    an OTP for mobile verification via Textbelt API.

    Attributes:
        phone (str): the recipient phone number in `E.164` format.
        user_id (str): string that represents an id
            unique to the user
        message (str | None): optional text message content which
            will replace the default message. Use `$OTP` variable to
            include the OTP in custom message.
        lifetime (int | None): optional time in seconds the OTP stays valid.
            Defaults to 180 seconds.
        length (int | None): optional number of digits in the OTP.
            Defaults to 6 digits.
    """

    phone: str
    user_id: str = Field(serialization_alias="userid")
    message: str | None = None
    lifetime: int | None = None
    length: int | None = None


class OTPGenerateResponse(BaseModel):
    """
    One-time password response data returned
    when OTP is generated and sent.

    Pydantic model to represent the response
    received from Textbelt API after generating and
    sending an OTP message.

    Attributes:
        success (bool): `True` when OTP message sent
            successfully, `False` otherwise.
        text_id (str | None): optional id of the text sent to recipient when
            `success` is `True`.
        quota_remaining (int): number of messages remaining on account.
        otp (str): one-time verification code sent to the user as string.
            Empty string on failure.
    """

    success: bool
    text_id: str | None = Field(default=None, alias="textId")
    quota_remaining: int = Field(alias="quotaRemaining")
    otp: str


class OTPVerificationRequest(BaseModel):
    """
    Verification of one-time password request data.

    Pydantic model to represent the request
    parameters required to verify an OTP from the
    user via Textbelt API.

    Attributes:
        otp (str): the code entered by the user.
        user_id: id associated with the user. Should match
            the `user_id` used to generate the OTP.
    """

    otp: str
    user_id: str = Field(serialization_alias="userid")


class OTPVerificationResponse(BaseModel):
    """
    One-time password response data returned
    when OTP is verified.

    Pydantic model to represent the response
    received from Textbelt API after verifying
    an OTP from the user.

    Attributes:
        success (bool): request was successfully received and processed.
        is_valid_otp (bool): denotes whether the OTP is correct/valid
            for the given `user_id`
    """

    success: bool
    is_valid_otp: bool = Field(alias="isValidOtp")


class CreditBalanceResponse(BaseModel):
    """
    Credit balance response data returned
    when checking the remaining balance on
    an account.

    Attributes:
        success (bool): `True` if Textbelt was able to lookup
            balance for API key, `False` otherwise.
        quota_remaining (int): the amount of SMS credits
            remaining on account.
    """

    success: bool
    quota_remaining: int = Field(alias="quotaRemaining")

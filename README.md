[![PyPI version](https://badge.fury.io/py/textbelt-py.svg)](https://badge.fury.io/py/textbelt-py)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Pre-commit enabled](https://img.shields.io/badge/pre--commit-enabled-green)](https://pre-commit.com/)
[![Tests](https://github.com/wfar/textbelt-py/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/wfar/textbelt-py/actions/workflows/test.yml)
[![Codecov](https://codecov.io/gh/wfar/textbelt-py/graph/badge.svg?token=Q4K50RGDL1)](https://codecov.io/gh/wfar/textbelt-py)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/wfar/textbelt-py/blob/main/LICENSE)

# textbelt-py
A Python client for Textbelt SMS API.

Simple and easy to use python package to send and receive text messages, one-time passwords, and mobile verification messages using the [Textbelt SMS API](https://textbelt.com/).

Implemented using `pydantic` to handle request/response data validation and `requests` to make network calls to the API, Allows for easy setup and configuration to handle any texting use case. Provides a simple and straight forward error handing flow in case of any failures to make error scenarios easy to debug.

Library supports all the functionalities listed in the [Textbelt documentation](https://docs.textbelt.com/). This includes sending and receiving messages, checking message delivery status, creating, sending, and verifying one-time passwords, and checking credit balance. Read the official docs for more details on all the current features provided by Textbelt.

> [!NOTE]
> Requires a valid Textbelt API key to be purchased and loaded with credits in order to make use of this library.

------

### Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
   - [Send message](#send-a-message)
	- [Send message and handle replies](#send-a-message-and-handle-replies)
	- [Send OTP](#send-a-one-time-password)
	- [Verify OTP](#verify-one-time-password)
	- [Check status](#check-message-delivery-status)
	- [Check credit balance](#check-credit-balance)
	- [Error handling](#error-handling)
3. [Development](#development)
	- [Requirements](#requirements)
	- [Setup](#setup)
	- [Test](#test)
4. [Contributing](#contributing)


## Installation
The library can be installed in your project using your favorite python package manager.

To install using pip:
```
pip install textbelt-py
```

To install using poetry:

```
poetry add textbelt-py
```

## Usage
Here are a few common ways on how to use the package.

### Send a message
```
from textbelt_py import SMSRequest, TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# create request
sms_request = SMSRequest(phone="+12123124123", message="Hello World!")

# send text
sms_response = textbelt_client.send_sms(sms_request)

# check response
print("Message sent successfully: " + sms_response.success)
```

### Send a message and handle replies
```
import json

from textbelt_py import SMSRequest, TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"
REPLY_WEBHOOK_URL = "https://website.com/webhook-reply"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# create request with reply webhook
sms_request = SMSRequest(
	phone="+12123124123",
	message="Hello World",
	reply_webhook_url=REPLY_WEBHOOK_URL,
	webhook_data="custom webhook data",
)

# send text
sms_response = textbelt_client.send_sms(sms_request)

# check response
print("Message sent successfully: " + sms_response.success)


...


# handle reply within webhook route
def reply_webhook_handler(data):
	# request header info
	request_timestamp = headers.get("X-textbelt-timestamp")
	request_signature = headers.get("X-textbelt-signature")

	# request body, convert to json string
	request_payload = body.get(json=True)
	request_payload_json_string = json.dumps(request_payload)

	# verify and parse webhook data
	is_valid, webhook_payload = textbelt_client.verify_webhook(
		request_timestamp,
		request_signature,
		request_payload_json_string,
	)

	# check reply is valid
	print("Reply webhook is valid: " + is_valid)

	# check message content
	print("Message from: " + webhook_payload.from_number)
	print("Message text: " + webhook.text)
```

### Send a one-time password
```
from textbelt_py import OTPGenerateRequest, TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# create request
otp_generate_request = OTPGenerateRequest(phone="+15557727420", user_id="user_id_12345")

# send otp
otp_generate_response = textbelt_client.send_otp(otp_generate_request)

# check response
print("OTP sent successfully: " + otp_generate_response.success)
```

### Verify one-time password
```
from textbelt_py import OTPVerificationRequest, TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# create request
otp_verification_request = OTPVerificationRequest(otp="321654", user_id="userid_12345")

# verify otp
otp_verification_response = textbelt_client.verify_otp(otp_verification_request)

# check otp is valid
print("OTP is valid: " + otp_verification_response.is_valid_otp)
```

### Check message delivery status
```
from textbelt_py import TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# use text_id of a previously sent SMS
text_id = "12345"
sms_status_response = textbelt_client.check_sms_delivery_status(text_id)

# check response
print("SMS delivery status: " + sms_status_response.status)
```

### Check credit balance
```
from textbelt_py import TextbeltClient


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# check credit balance for account
credit_balance_response = textbelt_client.check_credit_balance()

# check response
print("Remaining credit balance: " + credit_balance_response.quota_remaining)
```

### Error handling
```
from pydantic import ValidationError
from requests.exceptions import HTTPError

from textbelt_py import TextbeltClient, TextbeltException


TEXTBELT_API_KEY = "<YOUR-API-KEY-HERE>"


# setup client with api key
texbelt_client = TextbeltClient(TEXTBELT_API_KEY)

# try/except client methods and handle exceptions accordingly
try:
	textbelt_client.send_sms(None)
except TextbeltException as e:
	if e.ex_type is HTTPError:
		# handle requests http error
		print("Http error occurred")
	elif e.ex_type is ValidationError:
		# handle pydantic validation error
		print("Validation error occurred")
	else:
		# handle all other exceptions
		print(f"Exception type {e.ex_type} | Exception: {e.exception} | Message: {e.message}")
```

## Development
The source code can easily be installed and setup locally to make modifications as needed. It is managed using `poetry`. Development is made easy with code formatting and linting using `ruff` and type-checked with `mypy`. All linters, formatters, type-checking, and tests are executed on commit using `pre-commit`.  The `Makefile` is used to automate the development process, and can be used to run linting/formatting, as well as run tests.
> [!TIP]
> To see a list of all the commands in the Makefile, run the following command: `make help`

### Requirements
The following are required to build and develop locally:
- python
- poetry
- make

### Setup
First, we need to download the source. Clone the repo by running the following command in your working directory:
```
git clone git@github.com:wfar/textbelt-py.git
```

Once repo is downloaded, we need to build and install packages required for development. Run the following to install all dependencies:
```
make install
```

Then, run the following command to source and activate the virtual environment through poetry:
```
eval $(poetry env activate)
```
> [!Note]
> This will only work for activating poetry's virtual environment if you are using bash/zsh. To learn how to activate for your shell, see [poetry docs](https://python-poetry.org/docs/managing-environments/#activating-the-environment) for more details.

You are now all set and can start developing.

### Test
All tests files are located within the package's `tests` directory. It currently contains both unit and integration tests. Tests are executed using	`pytest` framework. Running tests will also provide a test coverage report.

To run all tests in the repo, run the following command:
```
make test
```
> [!IMPORTANT]
> Make sure to set the proper values in the `tests/.env.test` environment file or integration tests will fail. Don't worry, running integration tests will not use any of your SMS credits in your account!

## Contributing
Thanks for taking the time to contribute to the repo! Any and all contributions are welcome, including bug reporting, enhancements, feature requests, and PRs.

If you found a bug and want to report it or want to add a new feature, [create an issue](https://github.com/wfar/textbelt-py/issues/new) with clear details of the problem to start a discussion. If a change is warranted, clone/fork the repo to start developing and create a PR for review.


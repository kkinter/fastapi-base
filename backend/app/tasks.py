import httpx

from app.config import settings


class APIResponseError(Exception):
    pass


def send_simple_message(to: str, subject: str, body: str):
    with httpx.Client() as client:
        try:
            print(settings.MAILGUN_API_KEY)
            resp = client.post(
                f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
                auth=("api", settings.MAILGUN_API_KEY),
                data={
                    "from": f"wook <mailgun@{settings.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )

            resp.raise_for_status()
            return resp

        except httpx.HTTPStatusError as e:
            raise APIResponseError(f"{e.response.status_code} API 요청 실패")


def send_user_registration_email(email: str, activation_url: str):
    send_simple_message(
        email,
        "성공적으로 회원가입이 완료되었습니다.",
        (
            f"성공적으로 회원가입이 완료되었습니다. "
            f"이메일 인증을 통해 계정을 활성화해주세요. "
            f"인증 링크: {activation_url}"
        ),
    )

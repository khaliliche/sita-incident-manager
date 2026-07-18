from django.core.mail.backends.base import BaseEmailBackend
from decouple import config as env_config
import resend


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        resend.api_key = env_config('RESEND_API_KEY')
        sent_count = 0

        for message in email_messages:
            try:
                resend.Emails.send({
                    "from": "ITmanager <onboarding@resend.dev>",
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.body,
                })
                sent_count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e

        return sent_count
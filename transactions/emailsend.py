from django.core.mail import EmailMessage
from django.conf import settings

def email_send(subject, message, receiver):
	email = EmailMessage(
		subject,
		message,
		settings.EMAIL_HOST_USER,
		[receiver],
		)
	email.content_subtype = "html"
	email.fail_silently = False
	email.send()

	return message

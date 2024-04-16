from django.core.mail import EmailMessage
from django.conf import settings

def email_send(subject, message, receiver):
	email = EmailMessage(
		subject,
		message,
		settings.DEFAULT_FROM_EMAIL,
		[receiver],
		)
	email.content_subtype = "html"
	email.fail_silently = False
	email.send()

	return message

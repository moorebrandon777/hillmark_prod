from notification.email_utils import email_send
from notification.threading_utils import EmailThread

def send_email_async(subject, template_name, context, receiver):
    EmailThread(email_send, subject, template_name, context, receiver).start()


from notification.email_utils import email_send
from notification.threading_utils import EmailThread

# def send_email_async(subject, template_name, context, receiver):
#     EmailThread(email_send, subject, template_name, context, receiver).start()


def send_email_async(subject, template_name, context, receiver, transaction_id=None):
    EmailThread(email_send, subject, template_name, context, receiver, transaction_id=transaction_id).start()



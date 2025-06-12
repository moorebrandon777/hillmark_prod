# import logging
# from django.core.mail import EmailMultiAlternatives
# from django.conf import settings
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags

# logger = logging.getLogger('notification.email_utils')

# def email_send(subject, template_name, context, receiver):
#     """
#     Sends an HTML email with plain-text fallback. Logs result.
#     Assumes 'logo_url' is already included in context.
#     """
#     try:
#         html_message = render_to_string(template_name, context)
#         plain_message = strip_tags(html_message)

#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=plain_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[receiver],
#         )
#         email.attach_alternative(html_message, "text/html")
#         email.send(fail_silently=False)

#         logger.info(f"✅ Email successfully sent to {receiver} with subject '{subject}'")

#     except Exception as e:
#         logger.error(f"❌ Email sending failed to {receiver}: {e}", exc_info=True)


import logging
import time
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger('notification.email_utils')

def email_send(subject, template_name, context, receiver, max_retries=3, delay=2):
    """
    Sends an HTML email with plain-text fallback. Retries up to `max_retries` times if sending fails.
    Logs each attempt.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[receiver],
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            logger.info(f"✅ Email successfully sent to {receiver} with subject '{subject}' on attempt {attempt + 1}")
            return  # Exit the function if successful

        except Exception as e:
            attempt += 1
            logger.error(f"❌ Attempt {attempt} failed to send email to {receiver}: {e}", exc_info=True)
            if attempt < max_retries:
                time.sleep(delay)  # Wait before retrying

    logger.critical(f"🚨 All {max_retries} attempts to send email to {receiver} failed.")



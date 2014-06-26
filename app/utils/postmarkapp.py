import os
import pystmark


def send_email(from_email, subject, message):
    # Send a single message
    message = pystmark.Message(sender=os.environ.get('DEFAULT_FROM_EMAIL'),
                               to=os.environ.get('PERSONAL_EMAIL'),
                               subject=subject,
                               text=message)
    pystmark.send(message, api_key=os.environ.get('POSTMARK_API_KEY'))

'''
    messages = [pystmark.Message(sender=SENDER, to=to, subject='Hi',
                                    text='A message', tag='greeting')
                                                for to in recipients]

    response = pystmark.send_batch(messages, api_key=API_KEY)

# Check API response error
    try:
            response.raise_for_status()
    except pystmark.UnauthorizedError:
            print 'Use your real API key'
'''

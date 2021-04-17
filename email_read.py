# type: ignore
import imaplib
import email
from email.header import decode_header


def unsubscribers(number_of_checked_emails, sender_email_id, sender_email_id_password) -> tuple:
    unsubs_lst: set = set()
    body = ''
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(sender_email_id, sender_email_id_password)

    # total number of emails in INBOX
    messages = int(imap.select("INBOX")[1][0])

    # number of top emails to fetch
    N = messages - number_of_checked_emails
    print(f'Number of emails to check: {N}')

    if N <= 0:
        print()
        return [], number_of_checked_emails

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(str(msg["Subject"]))[0]

                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]

                if isinstance(From, bytes):
                    From = From.decode(encoding)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        try:
                            # get the email body
                            body += part.get_payload(decode=True).decode()
                        except:
                            pass
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                if isinstance(body, str) and len(body) >= 4 and body.lower()[0:4] == 'stop':
                    if From[0:2] == '+1':
                        unsubs_lst.add(From[2:12])
                    elif From.find('<') != -1 and From.find('>') != -1:
                        unsubs_lst.add(
                            From[From.find('<')+1:From.find('>')])
    
    # close the connection and logout
    imap.close()
    imap.logout()
    print('Users to be removed:', unsubs_lst, '\n')
    return list(unsubs_lst), N + number_of_checked_emails

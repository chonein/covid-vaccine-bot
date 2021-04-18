# type: ignore
import imaplib
import email
from email.header import decode_header


def unsubscribers_bot_rqsts(number_of_checked_emails, sender_email_id, sender_email_id_password) -> tuple:
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    message_lst = []
    user_requests_lst = []
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
        return [], number_of_checked_emails, []

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                # print("Subject:", subject)
                # print("From:", From)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                            # message_lst.append(str(body))
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            # print(body)
                            message_lst.append((From, str(body)))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        # print(body)
                        message_lst.append((From, str(body)))
    print(message_lst)
    for From, body in message_lst:
        # print(From, '\n', body)
        if isinstance(body, str) and len(body) >= 4 and body.lower()[0:4] == 'stop':
            if From[0:2] == '+1':
                unsubs_lst.add(From[2:12])
            elif From.find('<') != -1 and From.find('>') != -1:
                unsubs_lst.add(
                    From[From.find('<')+1:From.find('>')])
        elif isinstance(body, str):
            for month in months:
                month_idx = body.find('month')
                if month_idx != -1:
                    body = body[0:month_idx+1]
            body = body.replace('\n', '').replace('\r', '')
            if From[0:2] == '+1':
                From = From[2:12]
            elif From.find('<') != -1 and From.find('>') != -1:
                From = From[From.find('<')+1:From.find('>')]
            user_requests_lst.append((From, body))

    # close the connection and logout
    imap.close()
    imap.logout()
    print('Users to be removed:', unsubs_lst, '\n')
    return (list(unsubs_lst), N + number_of_checked_emails, user_requests_lst)

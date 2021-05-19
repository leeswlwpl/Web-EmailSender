from shutil import copyfile
import ast

import json
import pickle
import os.path
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

src = "token.pickle"
dst_path = "/tmp/"
token_src = "/tmp/token.pickle"

# Since AWS lambda function can only read the files inside /tmp folder
def initial_setup():
    print("initial_setup")
    if not os.path.exists(dst_path):
        raise ValueError("Source file does not exist: {}".format(dst_path))
    else:
        copyfile(src, token_src)
        print("File copy finished")

def getMessage(body):
    print("findRepairman")
    

    # For email structure
    if (body.get('toEmail')):
        toEmail = body.get('toEmail')
    else: 
        raise ValueError("Not valid address destination")
    if (body.get('Subject')):
        subject = "Your email subject"+body.get('Subject')
    else: subject = "(No subject)"
    
    
    # For email content
    if (body.get('userEmail')): 
        userEmail = body.get('userEmail')
    else: userEmail = "(No Email)"
    if (body.get('userName')):
        name = body.get('userName')
    else: name = "(No name)"
    if (body.get('Message')):
        message = body.get('Message')
    else: message = "(No message)"
      

    message_text = "\n\n".join([
        "\nUsername: ", name,
        "\nUser email or phone: ", email,
        "\nMessage: ", message
    ])
    
    mailSender(message_text, subject, toEmail)


def mailSender(message_text, subject, toEmail):
    print("mailSender function called")

    """Shows basic usage of the Gmail API. Lists the user's Gmail labels."""

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_src):
        # print("token exist")
        with open(token_src, 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # print("creds exist and refresh")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
            # print("creds not exist and need install")

        # Save the credentials for the next run
        with open(token_src, 'wb') as token:
            pickle.dump(creds, token)
            # print("token renew")


    service = build('gmail', 'v1', credentials=creds)

    # print("service builed")
    
    # Call the Gmail API
    message = MIMEText(message_text)
    message['to'] = toEmail
    message['from'] = ""
    message['subject'] = subject
    m = {'raw': base64.urlsafe_b64encode(message.as_string().encode("utf8")).decode("utf8")}
#     print("m=",m)

    results = (service.users().messages().send(userId='me', body=m).execute())
    
#     print("results: ", results)
    
    
    labels = results.get('labels', [])

#     if not labels:
#         print('No labels found.')
#     else:
#         print('Labels:')
#         for label in labels:
#             print(label['name'])

#     print("mailSender function ended")




def lambda_handler(event, context):
    
    if isinstance(event.get('body'), str):
        body = json.loads(event.get('body'))
    else:
        body = event.get('body')

    initial_setup()
    getMessage(body)

    return {
        'statusCode': 200,
        'body': json.dumps("Successfully submitted, We will contact you soon!")
    }

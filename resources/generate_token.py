from __future__ import print_function
import os
import pickle  # or json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the old token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        print("token.json already exists—using it.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        r'client_secret_487916228658-0oppcl777k3vo2mvsbrajrc39tfqbkik.apps.googleusercontent.com.json', SCOPES)  # Your client secret file
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("Created token.json successfully.")

if __name__ == '__main__':
    main()

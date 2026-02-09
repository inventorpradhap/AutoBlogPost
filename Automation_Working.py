import os
import json
import pickle
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# OAuth 2.0 scopes for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']

# Your Blogger Blog ID
BLOG_ID = '8223935102652440723'

# Token pickle file to cache access tokens
TOKEN_PICKLE_FILE = 'token.pickle'

def authenticate():
    creds = None
    
    # Try service account first (GitHub Actions)
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT')
    if service_account_json:
        try:
            info = json.loads(service_account_json)
            creds = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )
            print("✅ Using Service Account (GitHub Actions)")
        except Exception as e:
            print(f"Service account failed: {e}")
    
    # Fallback: Local OAuth flow (your desktop)
    else:
        # Check if we have saved credentials
        if os.path.exists(TOKEN_PICKLE_FILE):
            with open(TOKEN_PICKLE_FILE, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, go through OAuth flow (LOCAL ONLY)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            
            # Save credentials for next run
            with open(TOKEN_PICKLE_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Local OAuth flow completed")

    return build('blogger', 'v3', credentials=creds)

def post_to_blogger(service, title, html_content, labels=["#FreeKindleBooks", "Kindle Tamil Free Books"]):
    body = {
        "kind": "blogger#post",
        "blog": {"id": BLOG_ID},
        "title": title,
        "content": html_content
    }
    
    if labels:
        body["labels"] = labels

    post = service.posts().insert(blogId=BLOG_ID, body=body).execute()
    print(f'✅ Post published: {post["url"]}')

def main():
    # Authenticate and create Blogger API client
    service = authenticate()

    # Read your daily generated HTML file
    html_file = 'output.html'
    if not os.path.exists(html_file):
        print(f"❌ HTML file '{html_file}' not found.")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Use current date for post title
    from datetime import datetime
    today_str = datetime.now().strftime("%d-%m-%Y")
    post_title = f"Free Kindle Books Tamil Edition {today_str}"

    # Create the blog post
    post_to_blogger(service, post_title, html_content)

if __name__ == '__main__':
    main()

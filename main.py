from flask import Flask, render_template_string, request, redirect
import requests
import os

app = Flask(__name__)

# Facebook App ID, App Secret aur Redirect URI ko environment variables se lena
CLIENT_ID = os.getenv('CLIENT_ID')  # Railway mein set kiya jayega
CLIENT_SECRET = os.getenv('CLIENT_SECRET')  # Railway mein set kiya jayega
REDIRECT_URI = os.getenv('REDIRECT_URI')  # Railway mein set kiya jayega

# Global token counter
total_tokens = 0

# HTML Template with Background Image
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Fetcher</title>
    <style>
        body {
            background-color: black;
            color: white;
            text-align: center;
            font-family: Arial, sans-serif;
        }
        button {
            padding: 10px;
            background: red;
            color: white;
            border: none;
            cursor: pointer;
        }
        pre {
            background: gray;
            padding: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <h1>Facebook OAuth Token Fetcher</h1>
    
    <p>Click the button below to grant permissions and fetch your access token.</p>
    
    <a href="{{ oauth_url }}">
        <button>Grant Permissions</button>
    </a>
    
    {% if token %}
        <h2>Your Access Token:</h2>
        <pre>{{ token }}</pre>

        <h3>User Info:</h3>
        <ul>
            <li><strong>Name:</strong> {{ user_info['name'] }}</li>
            <li><strong>Email:</strong> {{ user_info.get('email', 'Not Available') }}</li>
            <li><strong>User ID:</strong> {{ user_info['id'] }}</li>
            <li><strong>Date of Birth:</strong> {{ user_info.get('birthday', 'Not Available') }}</li>
            <li><strong>Profile Picture:</strong> <img src="{{ user_info['picture']['data']['url'] }}" alt="Profile Picture"></li>
        </ul>

        <h3>Status: 200</h3>
        <h3>Total Tokens Fetched: {{ total_tokens }}</h3>
    {% else %}
        <p>After granting permissions, you can fetch your token here.</p>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    oauth_url = f'https://www.facebook.com/dialog/oauth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email,user_friends,public_profile'
    return render_template_string(html_template, oauth_url=oauth_url, token=None, user_info=None, total_tokens=total_tokens)

@app.route('/callback')
def callback():
    global total_tokens
    
    code = request.args.get('code')
    if not code:
        return 'Error: No code received from Facebook.', 400
    
    # Exchange authorization code for an access token
    token_url = 'https://graph.facebook.com/v17.0/oauth/access_token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    response = requests.get(token_url, params=params)
    data = response.json()
    
    if 'access_token' in data:
        access_token = data['access_token']
        
        # Fetch user info (ID, name, email, profile pic, birthday)
        user_info_url = f'https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email,birthday,picture.width(200).height(200)'
        user_info_response = requests.get(user_info_url)
        user_info = user_info_response.json()
        
        # Increment total token count
        total_tokens += 1
        
        # Returning the token and user info
        return render_template_string(html_template, oauth_url=None, token=access_token, user_info=user_info, total_tokens=total_tokens)
    else:
        return 'Error: Unable to fetch token.', 400

if __name__ == '__main__':
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5000))  # Railway mein automatically PORT set hota hai
    app.run(host=host, port=port)

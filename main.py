from flask import Flask, render_template_string, request, jsonify
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
            font-family: Arial, sans-serif;
            background-image: url('https://i.ibb.co/1JLx8sbs/5b7cfab06a854bf09c9011203295d1d5.jpg'); /* Replace with your image URL */
            background-size: cover;
            background-position: center;
            text-align: center;
            padding: 50px;
            color: white;
        }
        button {
            padding: 10px 20px;
            background-color: #4267B2;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #365899;
        }
        h1 { color: #fff; }
        p { color: #ddd; }
        pre {
            background-color: #333;
            padding: 20px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <h1>Facebook OAuth Token Fetcher</h1>
    <p>Click the button below to grant permissions and fetch your access token.</p>
    <button onclick="window.location.href='{{ oauth_url }}'">Grant Permissions</button>

    {% if token %}
    <h2>Your Access Token:</h2>
    <pre>{{ token }}</pre>

    <h3>User Info:</h3>
    <ul>
        <li><strong>Name:</strong> {{ user_info['name'] }}</li>
        <li><strong>Email:</strong> {{ user_info['email'] }}</li>
        <li><strong>User ID:</strong> {{ user_info['id'] }}</li>
        <li><strong>Date of Birth:</strong> {{ user_info['birthday'] }}</li>
        <li><strong>Profile Picture:</strong> <img src="{{ user_info['profile_pic'] }}" alt="Profile Picture"></li>
    </ul>

    <h3>Status: 200</h3>
    <h3>Total Tokens Fetched: {{ total_tokens }}</h3>

    {% else %}
    <p>After granting permissions, you can fetch your token here.</p>
    <form method="POST" action="/get_token">
        <button type="submit">Get Token</button>
    </form>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    # Facebook OAuth URL to request permissions
    oauth_url = f'https://www.facebook.com/dialog/oauth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email,user_friends,manage_pages,publish_actions'

    return render_template_string(html_template, oauth_url=oauth_url, token=None, user_info=None, total_tokens=total_tokens)

@app.route('/callback')
def callback():
    global total_tokens
    # This is where Facebook will redirect after permissions are granted
    code = request.args.get('code')

    if not code:
        return 'Error: No code received from Facebook.', 400

    # Exchange authorization code for an access token
    token_url = f'https://graph.facebook.com/v17.0/oauth/access_token'
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
        user_info_url = f'https://graph.facebook.com/me?access_token={access_token}&fields=id,name,email,birthday,picture'
        user_info_response = requests.get(user_info_url)
        user_info = user_info_response.json()

        # Increment total token count
        total_tokens += 1

        # Returning the token and user info
        return render_template_string(html_template, oauth_url=None, token=access_token, user_info=user_info, total_tokens=total_tokens)
    else:
        return 'Error: Unable to fetch token.', 400

@app.route('/get_token', methods=['POST'])
def get_token():
    # This is just to simulate the token fetch after permissions
    return redirect('/')

if __name__ == '__main__':
    # Flask ko host aur port set karna hai
    host = '0.0.0.0'  # Railway ko 0.0.0.0 pe run karna hota hai
    port = int(os.getenv('PORT', 5000))  # Railway mein automatically PORT set hota hai
    app.run(host=host, port=port)

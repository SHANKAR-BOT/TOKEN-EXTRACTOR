from flask import Flask, render_template_string, request
import requests
import re
import os

app = Flask(__name__)

# Background Image URL
BACKGROUND_IMAGE = os.getenv("BACKGROUND_IMAGE", "https://your-background-image-url.com")

# HTML + Flask Combined Code
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Extractor</title>
    <style>
        body {
            background-image: url('{{ background }}');
            background-size: cover;
            text-align: center;
            color: white;
        }
        textarea {
            width: 80%;
            height: 150px;
        }
        button {
            padding: 10px;
            background: red;
            color: white;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Facebook Token Extractor</h1>
    <form method="POST">
        <textarea name="cookies" placeholder="Paste your Facebook Cookies here..."></textarea><br><br>
        <button type="submit">Extract Token</button>
    </form>
    {% if result %}
        <h2>Extracted Tokens:</h2>
        {% if result == "Instagram Not Authorized" %}
            <p style="color: red;">Instagram Not Authorized</p>
        {% else %}
            <p>Total Tokens Extracted: {{ count }}</p>
            <textarea readonly>{{ result }}</textarea>
        {% endif %}
    {% endif %}
</body>
</html>
"""

def extract_token(cookies):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Cookie": cookies
    }

    # Instagram Authorization Check
    auth_check_url = "https://www.facebook.com/dialog/oauth?client_id=124024574287414&redirect_uri=https://www.instagram.com/"
    auth_response = session.get(auth_check_url, headers=headers)
    
    if "instagram.com" not in auth_response.url:
        return "Instagram Not Authorized", 0

    # Extracting Token
    token_url = "https://business.facebook.com/business_locations"
    token_response = session.get(token_url, headers=headers).text

    match = re.findall(r'EAAB\w+ZDZD', token_response)
    
    if match:
        return "\n".join(match), len(match)
    return "No Token Found", 0

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        cookies = request.form.get("cookies")
        if cookies:
            result, count = extract_token(cookies)
            return render_template_string(HTML_PAGE, result=result, count=count, background=BACKGROUND_IMAGE)
    
    return render_template_string(HTML_PAGE, result=None, background=BACKGROUND_IMAGE)

if __name__ == "__main__":
    # Railway Deployment Configuration
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")
    app.run(host=HOST, port=PORT)

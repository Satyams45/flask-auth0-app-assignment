import os
from flask import Flask, redirect, url_for, session, render_template_string
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from functools import wraps
import logging
import datetime

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Auth0 Config
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=f'https://{os.getenv("AUTH0_DOMAIN")}',
    access_token_url=f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token',
    authorize_url=f'https://{os.getenv("AUTH0_DOMAIN")}/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Require login decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Routes

@app.route('/')
def home():
    return '<h1>Welcome to Flask App</h1><a href="/login">Login</a> | <a href="/protected">Protected</a> | <a href="/logout">Logout</a>'

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))

@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = auth0.get('userinfo').json()
    session['user'] = userinfo
    return redirect('/protected')

@app.route('/protected')
@requires_auth
def protected():
    user = session['user']
    
    # Format log string in consistent way for KQL parsing
    log_msg = f"ACCESS | user_id={user['sub']} | route=/protected | time={datetime.datetime.utcnow().isoformat()}"
    logging.info(log_msg)
    
    return render_template_string('''
        <h1>Protected Page</h1>
        <p>Welcome, {{ user["name"] }}</p>
        <p>Email: {{ user["email"] }}</p>
        <a href="/logout">Logout</a>
    ''', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?returnTo=http://localhost:5000&client_id={os.getenv("AUTH0_CLIENT_ID")}')

import requests

URL = "https://flask-auth0-app-assignmnet.azurewebsites.net/protected"
COOKIE = {"session": "<your-session-cookie>"}

for i in range(12):
    response = requests.get(URL, cookies=COOKIE)
    print(f"Request {i+1}: {response.status_code}")

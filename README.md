# Flask Authenticated App with Logging, Monitoring, and Alerts

This project demonstrates a **DevSecOps-ready Flask application** that integrates **Auth0 authentication**, **structured logging**, **Azure Monitor** for observability, and **alerting** for detecting suspicious activity. The app is deployed to **Azure App Service**.

---

## Features

- SSO login using **Auth0**
- Logging for:
  - Successful logins
  - Access to the `/protected` route
  - Unauthorized access attempts
- Azure Monitor + KQL to detect misuse
- Alert rule that sends an **email** if abuse is detected

---


## Setup Instructions

### 1. Auth0 Configuration

1. Go to [Auth0 Dashboard](https://manage.auth0.com/).
2. Create a new **Application** (Regular Web App).
3. In the settings:
   - **Allowed Callback URLs**: `https://flask-auth0-app-assignment.azurewebsites.net/callback`
   - **Allowed Logout URLs**: `https://flask-auth0-app-assignment.azurewebsites.net/logout`
4. Copy the following into a `.env` file:
   ```env
   AUTH0_CLIENT_ID=<your-client-id>
   AUTH0_CLIENT_SECRET=<your-client-secret>
   AUTH0_DOMAIN=<your-tenant>.auth0.com
   AUTH0_CALLBACK_URL=https://<your-app-name>.azurewebsites.net/callback
   FLASK_SECRET_KEY=<random-secret>


### 2. Local Development (optional)
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

### 3. Azure App Service Deployment
  1. Create an Azure App Service (Linux + Python 3.10).

  2. Enable Application Logging:
  ```
  az webapp log config --name <app-name> --resource-group <rg> --application-logging true
 ```
 3. Connect your App to a Log Analytics Workspace:

    - In App Service → Monitoring → Diagnostic Settings → Add diagnostic setting

    - Choose:

      - AppServiceConsoleLogs

      - Send to Log Analytics

  4. Configure the environment variables in Azure > App Service > Configuration using your .env values.

### Logging Explanation
We log key security-relevant events using app.logger.info():

  - Logins: Logs user ID, email, and timestamp after Auth0 login.

  - Protected Route Access: Every time /protected is accessed, logs user ID and timestamp.

  - Unauthorized Access: Logs client IP and timestamp when unauthorized access is detected.

# Monitoring & Detection (KQL)
To detect abuse of the /protected endpoint, we use the following Kusto Query Language (KQL) in Azure Monitor:
```
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where Message contains "ACCESS" and Message contains "/protected"
| parse Message with * "user_id=" user_id " | route=" route " | time=" timestamp
| summarize access_count=count() by user_id, bin(TimeGenerated, 15m)
| where access_count > 10
```

This query identifies any user who accessed the /protected route more than 10 times in 15 minutes.

# Alert Setup
To create an alert rule based on the KQL above:

1. Go to Azure Monitor > Alerts > + Create Alert Rule

2. Scope: Select your App Service

3. Condition:

   - Choose Custom log search

   - Paste the KQL query

4. Set Evaluation Period: 15 minutes

5. Action Group:

   - Create or select one

   - Add your email to receive notifications

6. Alert Details:

   - Severity: 3 (Low)

   - Name: Excessive Protected Access

   - Description: Alerts when a user hits /protected >10 times in 15 min

## test-app.http
You can use this file to simulate access:
```
### Valid /protected access
GET https://flask-auth0-app-assignment.azurewebsites.net/protected
Authorization: Bearer <VALID_JWT>

### Simulate unauthorized
GET https://flask-auth0-app-assignment.azurewebsites.net/protected
```

# Summary
This project showcases how to:

  - Secure a Flask app with SSO (Auth0)

  - Log key user actions

  - Monitor for suspicious behavior using KQL

  - Create automated alerts in Azure

Perfect for DevSecOps teams seeking production-level observability in cloud-native apps.

### Demo Link :

https://youtu.be/3hZQU2wnSDE


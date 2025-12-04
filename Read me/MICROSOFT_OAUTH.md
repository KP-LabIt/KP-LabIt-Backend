# Microsoft OAuth2 Authentication

## Overview

This backend supports Microsoft OAuth2 authentication, allowing users to log in with their Microsoft accounts (Office 365, Azure AD).

## Features

- **User Login**: Sign in with Microsoft account
- **Automatic User Creation**: New users are created automatically with default "student" role
- **JWT Token Generation**: Returns JWT tokens after successful authentication
- **Microsoft Graph API**: Fetch users from your organization's Microsoft 365

## Endpoints

### OAuth2 Authentication

**Login with Microsoft**
```
GET /api/accounts/microsoft/login/
```
Redirects user to Microsoft login page. After authentication, returns JWT tokens.

**Authentication Success**
```
GET /api/accounts/auth/success/
```
Callback endpoint that returns JWT tokens after successful Microsoft authentication.

Response:
```json
{
  "status": "success",
  "message": "Successfully authenticated with Microsoft",
  "user": {
    "id": 1,
    "email": "user@domain.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Microsoft Graph API

**Get All Users**
```
GET /api/accounts/microsoft/users/?top=10&select=displayName,mail
```
Fetches users from Microsoft 365 using app-only permissions.

Query Parameters:
- `top` (optional): Limit number of users
- `select` (optional): Comma-separated list of properties to return

**Get User by ID**
```
GET /api/accounts/microsoft/users/<user_id>/
```
Fetches a specific user from Microsoft 365.

## User Roles

**Default Behavior:**
- All new users created via Microsoft login get the **"student"** role by default
- Username is automatically extracted from email (e.g., `john.doe@katkinpark.sk` → username: `john.doe`)

**Changing Roles:**
- Use Django Admin: `http://localhost:8000/admin/`
- Or manually via Python shell:
  ```python
  from accounts.models import User, Role
  user = User.objects.get(email='user@domain.com')
  user.role = Role.objects.get(name='teacher')
  user.save()
  ```

## OAuth2 Flow

```
1. User clicks "Login with Microsoft"
   ↓
2. Frontend: GET /api/accounts/microsoft/login/
   ↓
3. Backend redirects to Microsoft login page
   ↓
4. User logs in with Microsoft credentials
   ↓
5. Microsoft redirects to: /complete/microsoft-oauth2/
   ↓
6. Backend creates/finds user in database
   ↓
7. Backend redirects to: /api/accounts/auth/success/
   ↓
8. Returns JWT tokens
```

## Frontend Integration

### Simple Redirect Approach

```javascript
function loginWithMicrosoft() {
    window.location.href = 'http://localhost:8000/api/accounts/microsoft/login/';
}
```

### Handle Callback

After successful login, extract tokens from the success response and store them:

```javascript
localStorage.setItem('access_token', data.token);
localStorage.setItem('refresh_token', data.refresh_token);
```

## Production Deployment

When deploying to production:

1. **Add Production Redirect URI** in Azure:
   - Go to your app → **Authentication**
   - Add: `https://your-domain.com/complete/microsoft-oauth2/`

2. **Update Settings**:
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Restrict CORS origins
   - Use HTTPS

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Check redirect URI in Azure matches exactly: `http://localhost:8000/complete/microsoft-oauth2/`

**Error: "invalid_client"**
- Verify Client ID and Secret in `.env` are correct

**Error: "unauthorized_client"**
- Grant admin consent for API permissions in Azure Portal

**Error: "Missing Microsoft Graph credentials"**
- Fill all 6 Microsoft variables in `.env`
- Restart Django server

## Security Notes

- ✅ All credentials stored in `.env` (not in code)
- ✅ Tokens expire after 8 hours (configurable)
- ✅ OAuth2 uses Authorization Code flow with PKCE
- ✅ Graph API uses Client Credentials flow (app-only access)

## Documentation

- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview)
- [Social Auth Django](https://python-social-auth.readthedocs.io/)

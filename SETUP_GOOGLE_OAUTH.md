# Google OAuth Setup Instructions

To enable Google OAuth login and Google Drive integration, you need to set up OAuth 2.0 credentials in Google Cloud Console.

## Steps to Get Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select a Project**
   - Click on the project dropdown at the top
   - Click "New Project" or select an existing project
   - Give it a name (e.g., "Evidence Collection")

3. **Enable Required APIs**
   - Go to "APIs & Services" > "Library"
   - Search for and enable:
     - **Google Drive API**
     - **Google+ API** (if available, or use Google Identity Services)

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen first:
     - Choose "External" (unless you have a Google Workspace)
     - Fill in the required fields (App name, User support email, Developer contact)
     - Add scopes: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/drive.file`
     - Save and continue

5. **Create OAuth Client ID**
   - Application type: **Web application**
   - Name: "Evidence Collection Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `http://localhost:8000` (for backend if needed)
   - Authorized redirect URIs:
     - `http://localhost:3000/login/callback`
   - Click "Create"

6. **Copy Your Credentials**
   - You'll see a popup with your Client ID and Client Secret
   - Copy both values

## Configuration

### Frontend Configuration

1. Open `frontend/.env` file
2. Add your Google Client ID:
   ```
   REACT_APP_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   ```
3. Restart the frontend development server

### Backend Configuration

1. Open `backend/.env` file (or set environment variables)
2. Add your Google credentials:
   ```
   GOOGLE_DRIVE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
   GOOGLE_DRIVE_REDIRECT_URI=http://localhost:3000/login/callback
   ```
3. Restart the backend server

## Testing

1. Start both frontend and backend servers
2. Navigate to the login page
3. Click "Sign in with Google"
4. You should be redirected to Google's OAuth consent screen
5. After authorization, you'll be redirected back to the application

## Troubleshooting

- **"Google Client ID not configured"**: Make sure `REACT_APP_GOOGLE_CLIENT_ID` is set in `frontend/.env` and the server is restarted
- **"redirect_uri_mismatch"**: Make sure the redirect URI in Google Console matches exactly: `http://localhost:3000/login/callback`
- **"invalid_client"**: Check that your Client ID and Secret are correct
- **"unauthorized_client" when uploading to Google Drive (RefreshError)**: See "Verifying which OAuth client issued the refresh token" below
- **CORS errors**: Make sure authorized JavaScript origins include `http://localhost:3000`

## Verifying which OAuth client issued the refresh token

The refresh token is **tied to the OAuth client** that was used when the user signed in. If you get `unauthorized_client` or `RefreshError` when uploading to Google Drive after approval, the token was likely issued by a **different client** than the one in your backend `.env`.

**How to check:**

1. **See which client your backend uses**
   - Open `backend/.env` and note:
     - `GOOGLE_DRIVE_CLIENT_ID` (e.g. `567699847744-xxxx.apps.googleusercontent.com`)
     - `GOOGLE_DRIVE_CLIENT_SECRET`

2. **See which client(s) exist in Google Cloud**
   - Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Credentials** → **Credentials**
   - Under **OAuth 2.0 Client IDs**, you see each client’s **Client ID** (and type, e.g. "Web application")
   - The **Client ID** in `.env` must match **exactly** one of these (including the numeric prefix)

3. **Make sure the same client was used when signing in**
   - When the user clicked "Authenticate" (Google Drive), the app sent that client’s Client ID to Google
   - The backend builds the auth URL using `GOOGLE_DRIVE_CLIENT_ID` from `.env`
   - So the token is issued for that client. If you later change `.env` to a **different** Client ID (e.g. another project or client), existing refresh tokens will no longer work → `unauthorized_client`

4. **Fix**
   - **Option A:** Keep using the **same** OAuth client: ensure `GOOGLE_DRIVE_CLIENT_ID` and `GOOGLE_DRIVE_CLIENT_SECRET` in `backend/.env` are from the **same** Web application client in Google Cloud that you use when users click "Authenticate". Do not mix clients from different projects or different client IDs.
   - **Option B:** After changing to a new client, have users **re-authenticate**: click "Authenticate" on the Category Groups page and sign in with Google again so new tokens are issued for the new client.

## Production Setup

For production, you'll need to:
1. Add your production domain to authorized JavaScript origins
2. Add your production callback URL to authorized redirect URIs
3. Update the `.env` files with production URLs
4. Consider using environment variables instead of `.env` files for security




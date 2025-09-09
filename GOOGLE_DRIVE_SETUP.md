# Google Drive Auto-Upload Setup

This guide shows how to configure automatic uploads of build artifacts to Google Drive.

## Prerequisites

1. Google Cloud Console account
2. GitHub repository with Actions enabled
3. Google Drive folder for storing builds

## Step 1: Create Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

4. Create Service Account:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Fill in details and create
   - Click on the created service account
   - Go to "Keys" tab → "Add Key" → "Create New Key" → "JSON"
   - Download the JSON file

## Step 2: Share Google Drive Folder

1. Create a folder in Google Drive for storing builds
2. Right-click folder → "Share"
3. Add the service account email (from JSON file) with "Editor" permissions
4. Copy the folder ID from URL (e.g., `https://drive.google.com/drive/folders/FOLDER_ID_HERE`)

## Step 3: Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add repository secrets:

### GOOGLE_DRIVE_SERVICE_ACCOUNT
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40project.iam.gserviceaccount.com"
}
```

### GOOGLE_DRIVE_FOLDER_ID
```
your-folder-id-from-drive-url
```

## Step 4: Test the Setup

1. Push code to trigger GitHub Actions
2. Check the Actions tab for build status
3. Verify files appear in your Google Drive folder

## File Naming Convention

Files will be uploaded with this format:
- Windows: `redactor-windows-YYYYMMDD-commit.exe`
- macOS: `redactor-macos-YYYYMMDD-commit`

## Troubleshooting

- **403 Error**: Check if service account has access to the Drive folder
- **Authentication Error**: Verify the service account JSON is valid
- **File Not Found**: Ensure PyInstaller builds are successful before upload
- **Folder ID Error**: Make sure the folder ID is correct and accessible

## Security Notes

- Service account has minimal permissions (only Drive file access)
- Credentials are stored securely in GitHub Secrets
- No personal Google account access required
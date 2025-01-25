### Obtaining the `creds.json` File from Google Cloud

Follow the steps below to generate the `creds.json` file required for authenticating your application with Google APIs:

1. **Visit the Google Cloud Console**  
   Open [Google Cloud Console](https://console.cloud.google.com/) in your browser.

2. **Create a New Project**  
   - In the top navigation bar, click on the project dropdown menu and select **New Project**.
   - Enter a name for your project (e.g., `Value_Investment_ML`).
   - Click **Create** and wait for the project to be created.

3. **Enable the Google Drive API**  
   - Go to the [Google Drive API page](https://console.cloud.google.com/apis/library/drive.googleapis.com).
   - Select your project from the dropdown menu.
   - Click **Enable** to activate the Google Drive API for your project.

4. **Create Credentials**  
   - Go to the [Credentials page](https://console.cloud.google.com/apis/credentials).
   - Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
   - If prompted to configure the consent screen:
     - Click **CONFIGURE CONSENT SCREEN**.
     - For the **User Type**, select **External** and click **Create**.
     - Fill in the required details (e.g., application name, support email).
     - Add `http://localhost` to the **Authorized Domains** section.
     - Save your settings.
   - After configuring the consent screen, return to the **Create Credentials** page and select **OAuth client ID** again.
   - Choose **Desktop App** as the application type.
   - Enter a name (e.g., `Desktop App`) and click **Create**.

5. **Download the Credentials File**  
   - After creating the OAuth client ID, you will see a **Download JSON** button. Click it to download the `creds.json` file.
   - Save this file in the `secrets/Google_Drive` folder of your project. If the folder does not exist, create it.

6. **Secure the Credentials File**  
   - Add the following line to your `.gitignore` file to ensure the credentials file is not tracked by Git:
     ```plaintext
     secrets/
     ```

7. **Verify Your Setup**  
   - Run your application or script to authenticate with Google. During the first run, you will be prompted to log in to your Google account and grant the necessary permissions.
   - The authentication process will generate a `token.json` file in the same directory as `creds.json`. This token file is used for subsequent API requests.

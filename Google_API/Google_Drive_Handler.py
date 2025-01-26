import os
import logging
import datetime
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


class Google_Drive_Handler:
    def __init__(self, root_folder_id, log_dir="./logfiles", token_path="secrets/Google_Drive/token.json", credentials_path="secrets/Google_Drive/creds.json"):
       
        self.root_folder_id = root_folder_id
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.creds = None
        self.service = None

        # Set up logging
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(
            log_dir,
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        )
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        # Authenticate and initialize the service
        self.authenticate()
        self.initialize_service()

    def authenticate(self):
    
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path,['https://www.googleapis.com/auth/drive'])

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, ['https://www.googleapis.com/auth/drive']
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token_file:
                token_file.write(self.creds.to_json())

    def initialize_service(self):
        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path, folder_id=None):
        folder_id = folder_id or self.root_folder_id
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id],
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        logging.info(f"Uploaded {file_path} to folder {folder_id} with ID {file.get('id')}")

    def list_files_by_pattern(self, folder_id=None, file_pattern="___"):
        folder_id = folder_id or self.root_folder_id
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(q=query).execute()

        files = [
            {
                "name":(info['name'].split('.')[0]).split(file_pattern),
                "id":info['id']
            }
            for info in results.get('files', [])
        ]
        return tuple(files)

    def remove_folder(self, folder_path):
        try:
            shutil.rmtree(folder_path)
            logging.info(f"Removed folder: {folder_path}")
        except Exception as e:
            logging.error(f"Error removing folder {folder_path}: {e}")

    def remove_file_from_drive(self, file_id, local_path=None):
        """
        Removes a file from Google Drive and optionally from the local system.
        """
        try:
            # Delete the file from Google Drive
            self.service.files().delete(fileId=file_id).execute()
            logging.info(f"File with ID {file_id} removed from Google Drive.")

            # If a local path is provided, delete the file locally
            if local_path and os.path.exists(local_path):
                os.remove(local_path)
                logging.info(f"Local file {local_path} removed.")
        except HttpError as e:
            logging.error(f"Error removing file from Drive: {e}")
        except Exception as e:
            logging.error(f"Error removing local file: {e}")


    def get_folder_id(self, country_code, exchange_code):
        try:
            # Search for the country folder
            country_query = (
                f"name='{country_code}' and mimeType='application/vnd.google-apps.folder' "
                f"and '{self.root_folder_id}' in parents"
            )
            country_folder = self.service.files().list(q=country_query, fields='files(id)').execute()
            country_folder_id = (
                country_folder.get('files', [])[0].get('id') if country_folder.get('files') else None
            )

            if not country_folder_id:
                logging.warning(f"Country folder '{country_code}' not found.")
                return None

            # Search for the exchange folder within the country folder
            exchange_query = (
                f"name='{exchange_code}' and mimeType='application/vnd.google-apps.folder' "
                f"and '{country_folder_id}' in parents"
            )
            exchange_folder = self.service.files().list(q=exchange_query, fields='files(id)').execute()
            exchange_folder_id = (
                exchange_folder.get('files', [])[0].get('id') if exchange_folder.get('files') else None
            )

            if not exchange_folder_id:
                logging.warning(f"Exchange folder '{exchange_code}' not found in '{country_code}'.")
                return None

            return exchange_folder_id
        
        except HttpError as err:
            print(f"HttpError: {err}")
            # You can also log the error for future reference.
            return None
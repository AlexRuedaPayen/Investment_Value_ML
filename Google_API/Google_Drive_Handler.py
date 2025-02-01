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

import io
import pandas as pd
from googleapiclient.http import MediaIoBaseDownload


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



    def list_folders(self, parent_id):
        """
        List all folders inside a given parent folder.

        Args:
            parent_id (str): ID of the parent folder.

        Returns:
            dict: A dictionary {folder_name -> folder_id}.
        """
        try:
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            return {f["name"]: f["id"] for f in results.get("files", [])}
        except HttpError as err:
            logging.error(f"Error listing folders: {err}")
            return {}


    def list_csv_files(self, folder_id):
        """
        List all CSV files inside a given folder.

        Args:
            folder_id (str): ID of the folder.

        Returns:
            dict: A dictionary {file_name -> file_id}.
        """
        try:
            query = f"'{folder_id}' in parents and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()


            return {f["name"]: f["id"] for f in results.get("files", [])}
        except HttpError as err:
            logging.error(f"Error listing CSV files: {err}")
            return {}





    def download_xlsx_as_dataframe(self, file_id):
        """
        Download an Excel (.xlsx) file from Google Drive and convert it to a pandas DataFrame,
        ensuring that no 'Unnamed: 0' columns are present and the index is properly set.
        Also, the Date column is converted into fiscal quarters like Q4 2024, Q3 2024, etc.

        Args:
            file_id (str): The Google Drive file ID.

        Returns:
            pd.DataFrame: The downloaded Excel file as a DataFrame with proper index and quarters.
        """
        try:
            # Request to get the file from Google Drive
            request = self.service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            
            # Download the file
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            file_stream.seek(0)  # Reset file stream position to the start
            
            # Read the Excel file into a DataFrame
            df = pd.read_excel(file_stream, engine='openpyxl', index_col=0)  # Use index_col=0 to set the first column as the index
            
            # Remove any columns that are named "Unnamed" (usually the default index column from CSVs)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove columns starting with 'Unnamed'
            
            # Ensure that the index column is set properly
            df.index = pd.to_datetime(df.index)  # Convert the index to datetime if it isn't already
            
            # Convert the index (dates) to fiscal quarters like Q4 2024, Q3 2024, etc.
            df['Fiscal Quarter'] = df.index.to_period('Q').astype(str)  # Convert datetime index to fiscal quarters

            # Set the fiscal quarter as the new index
            df.set_index('Fiscal Quarter', inplace=True)
            
            # Sort the DataFrame by the fiscal quarter index
            df = df.sort_index()
            
            return df
        except HttpError as err:
            logging.error(f"Error downloading Excel file {file_id}: {err}")
            return pd.DataFrame()  # Return an empty DataFrame if download fails

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
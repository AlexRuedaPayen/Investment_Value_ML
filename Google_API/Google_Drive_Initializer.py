import os
import json

class Google_Drive_Initializer:
    """
    A class to handle Google Drive folder structure initialization.
    """

    def __init__(self, service, config_path='./Google_API/config_init.json'):
        """
        Initialize the GoogleDriveInitializer.

        Args:
            service: Authenticated Google Drive API service instance.
            config_path (str): Path to the configuration file for initialization status.
        """
        self.service = service
        self.config_path = config_path
        self._ensure_config_file()

    def _ensure_config_file(self):
        """
        Ensure the config.json file exists. If not, create it with default values.
        """
        if not os.path.exists(self.config_path):
            default_config = {
                'google_drive_initialized': False
            }
            with open(self.config_path, 'w') as config_file:
                json.dump(default_config, config_file)
            print(f"Config file '{self.config_path}' created with default values.")

    def create_folder(self, name, parent_id=None):
        """
        Creates a folder on Google Drive. If it already exists, returns its ID.

        Args:
            name (str): Name of the folder to create.
            parent_id (str): ID of the parent folder (optional).

        Returns:
            str: ID of the created or existing folder.
        """
        # Check if the folder already exists
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        existing_folder = self.service.files().list(q=query, fields='files(id)').execute()
        if existing_folder.get('files'):
            return existing_folder['files'][0]['id']  # Folder already exists, return its ID
        
        # If not, create the folder
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

    def create_file_system(self, folder_structure, parent_id=None):
        """
        Creates the folder structure in Google Drive based on the folder_structure provided.

        Args:
            folder_structure (dict): Dictionary mapping countries to lists of exchanges.
            parent_id (str): ID of the root parent folder (optional).
        """
        for country, exchanges in folder_structure.items():
            country_folder_id = self.create_folder(country, parent_id)
            for exchange in exchanges:
                self.create_folder(exchange, country_folder_id)

    def initialize_folders(self, folder_structure, root_folder_id):
        """
        Initializes the Google Drive folder structure.

        Args:
            folder_structure (dict): Dictionary mapping countries to lists of exchanges.
            root_folder_id (str): ID of the root folder in Google Drive.
        """
        try:
            self.create_file_system(folder_structure, root_folder_id)
            print("Google Drive folder structure initialized successfully.")
        except Exception as e:
            print(f"Error initializing folder structure: {e}")

    def check_if_initialized(self):
        """
        Check if the Google Drive folder structure has already been initialized.

        Returns:
            bool: True if initialized, False otherwise.
        """
        try:
            with open(self.config_path, 'r') as config_file:
                config = json.load(config_file)
                return config.get('google_drive_initialized', False)
        except FileNotFoundError:
            return False

    def mark_as_initialized(self):
        """
        Mark the Google Drive folder structure as initialized in the config file.
        """
        config = {'google_drive_initialized': True}
        with open(self.config_path, 'w') as config_file:
            json.dump(config, config_file)

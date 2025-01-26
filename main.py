from Google_API.Google_Drive_Handler import Google_Drive_Handler
from Google_API.Google_Drive_Initializer import Google_Drive_Initializer
from utils import DotDict

from data.country_markets import country_markets

def main():

    

    # Authenticate and initialize Google Drive Handler
    handler = Google_Drive_Handler(
        root_folder_id=DotDict(path="secrets/Google_Drive/folder_ids.json").root,
        log_dir="./real_logfiles",
        token_path="./secrets/Google_Drive/token.json",
        credentials_path="./secrets/Google_Drive/creds.json"
    )

    

    # Initialize GoogleDriveInitializer
    initializer = Google_Drive_Initializer(handler.service)

    # Only initialize the folder structure if not already done
    if not initializer.check_if_initialized():
        initializer.initialize_folders(country_markets, handler.root_folder_id)
        initializer.mark_as_initialized()

    # Proceed with other operations (e.g., upload, download, etc.)
    print("Google Drive setup complete. Proceeding with other tasks...")

if __name__ == "__main__":
    main()
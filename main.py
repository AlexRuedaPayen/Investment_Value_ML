from Google_API.Google_Drive_Handler import Google_Drive_Handler
from Google_API.Google_Drive_Initizalizer import Google_Drive_Initizalizer
from utils import DotDict

from data.country_markets import country_markets

def main():


    # Authenticate and initialize Google Drive Handler
    handler = Google_Drive_Handler(
        root_folder_id=DotDict(path="secrets.Google_Drive.folder_ids").root,
        log_dir="./real_logfiles",
        token_path="./secrets/Google_Drive/token.json",
        credentials_path="./secrets/Google_Drive/creds.json"
    )

    

    # Only initialize the folder structure if not already done
    if not check_if_initialized():
        initialize_google_drive_folders(handler.service, country_markets, root_folder_id=DotDict(path="secrets.Google_Drive.folder_ids").root)
        mark_as_initialized()

    # Proceed with other operations (e.g., upload, download, etc.)
    print("Google Drive setup complete. Proceeding with other tasks...")

if __name__ == "__main__":
    main()

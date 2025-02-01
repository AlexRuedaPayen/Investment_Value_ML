from utils.utils import DotDict
from data.country_markets import country_markets
from Google_API.Google_Drive_Handler import Google_Drive_Handler

class DataFetcher:
    def __init__(self, google_drive_handler: Google_Drive_Handler):
        self.gdrive_handler = google_drive_handler
        self.data_storage = {}  # Dictionary to store the data

    def store_dataframe(self, country_code, exchange_code, company_name, df):
        """
        Store a dataframe in the hierarchical structure.
        """
        if country_code not in self.data_storage:
            self.data_storage[country_code] = {}

        if exchange_code not in self.data_storage[country_code]:
            self.data_storage[country_code][exchange_code] = {}


        # Store the dataframe for the company
        self.data_storage[country_code][exchange_code][company_name] = df
        print(f"Stored data for {company_name} in {country_code} -> {exchange_code}.")

    def fetch_and_store_data(self, file_id, country_code, exchange_code, company_name):
        """
        Fetch data from Google Drive using the file ID, and store it in the hierarchical structure.
        """
        # Fetch the DataFrame using Google_Drive_Handler
        df = self.gdrive_handler.download_xlsx_as_dataframe(file_id)
        
        # Check if DataFrame is not empty and store it
        if not df.empty:
            self.store_dataframe(country_code, exchange_code, company_name, df)
        else:
            print(f"Failed to download or parse the CSV for {company_name}.")

    def get_dataframe(self, country_code, exchange_code, company_name):
        """
        Retrieve a stored dataframe from the in-memory storage.
        """
        try:
            return self.data_storage[country_code][exchange_code][company_name]
        except KeyError:
            print(f"Data for {company_name} not found in {country_code} -> {exchange_code}.")
            return None


def fetch_and_store_all_data(country_markets, gdrive_handler, data_fetcher):
    """
    Fetch and store data for all countries and their respective markets.
    """
    for country, markets in country_markets.items():
        print(f"Processing country: {country}")

        # Fetch the folder for the country



        for market in markets:
            print(f"  Processing market: {market}")

            # Fetch the folder for the market within the country
            exchange_folder_id = gdrive_handler.get_folder_id(country, market)


            if exchange_folder_id:
                # List all CSV files for the market (you can adjust the logic based on the filenames)
                csv_files = gdrive_handler.list_csv_files(exchange_folder_id)

                    

                # Loop over the CSV files and fetch their data
                for file_name, file_id in csv_files.items():
                    company_name = file_name.split('.')[0]  # Assuming company name is in the file name
                    print(f"    Fetching data for company: {company_name}")

                    # Fetch the data and store it in the in-memory data storage
                    data_fetcher.fetch_and_store_data(file_id, country, market, company_name)

            else:
                print(f"    Exchange folder for {market} not found in {country}.")
        else:
            print(f"    Country folder for {country} not found.")


import numpy as np
import pandas as pd
from utils.utils import DotDict
from data.country_markets import country_markets
from Google_API.Google_Drive_Handler import Google_Drive_Handler


from Data_Preprocessor.DataFetcher import DataFetcher,fetch_and_store_all_data

def prepare_training_set(data_fetcher):
    """
    Prepare the training set for the encoder-decoder model using data in data_fetcher.data_storage.

    Args:
        data_fetcher (object): The data_fetcher object that contains data in data_fetcher.data_storage.

    Returns:
        X_train (np.array): Input data (quarterly data with missing quarters).
        Y_train (np.array): Output data (predicted missing quarter).
    """
    # Initialize lists to hold the input-output pairs
    input_data = []
    output_data = []




    # Loop through each country and market
    for country, markets in data_fetcher.data_storage.items():
        for market, companies in markets.items():
            for company, df in companies.items():

                # Ensure the dataframe has quarters as indices, and drop any 'Unnamed' columns
                df = df.drop(columns=[col for col in df.columns if 'Unnamed' in col], errors='ignore')
                df = df.rename_axis('Quarter').reset_index()

                # Identify quarters available in the data
                available_quarters = df['Quarter'].tolist()
                
                test_missing = lambda x:df.loc[df['Quarter'] == x].isnull().any(axis=1).sum() < 10

                # Loop through the quarters to find missing ones
                for i in range(1, len(available_quarters) - 1):  # We check between the first and last quarter
                    # Check if a quarter is missing between two available quarters

                    if test_missing(available_quarters[i-1]) and test_missing(available_quarters[i+1]):
                        # If available_quarters[i] is missing, we prepare data for training
                        input_quarters = [available_quarters[i-1], available_quarters[i+1]]
                        output_quarter = available_quarters[i]
                        
                        # We gather the data for the input-output pair
                        # Get the columns of each DataFrame and append a suffix to make them unique
                        df1 = df.loc[df['Quarter'] == input_quarters[0]]
                        df2 = df.loc[df['Quarter'] == input_quarters[1]]

                        # Renaming columns to make sure they don't conflict
                        df1.columns = [f"{col}_BEFORE" for col in df1.columns]
                        df2.columns = [f"{col}_AFTER" for col in df2.columns]

                        # Now concatenate the two dataframes
                        input_data.append(pd.concat([df1, df2], axis=1))
                        output_data.append(df.loc[df['Quarter'] == output_quarter])

            
    # Convert lists to numpy arrays for training

    
    X_train = pd.concat(input_data,axis=0)
    Y_train = pd.concat(output_data,axis=0)

    

    return X_train, Y_train

# Usage Example
# Assuming data_fetcher is an instance of your class that has the `data_storage` attribute
root_folder_id = DotDict("secrets/Google_Drive/folder_ids.json").root



gdrive_handler = Google_Drive_Handler(root_folder_id=root_folder_id)
data_fetcher = DataFetcher(gdrive_handler)

fetch_and_store_all_data({key:value for key,value in country_markets.items() if key in [x for x in country_markets.keys()][:1]}, gdrive_handler, data_fetcher)

X_train, Y_train = prepare_training_set(data_fetcher)


# Check the shape of the training data
print(f"Input shape: {X_train.shape}")
print(f"Output shape: {Y_train.shape}")
import torch
import numpy as np
import pandas as pd
from utils.utils import DotDict
from data.country_markets import country_markets
from Google_API.Google_Drive_Handler import Google_Drive_Handler
from Operators.EncoderDecoder import EncoderDecoder

from Data_Preprocessor.DataFetcher import DataFetcher,fetch_and_store_all_data
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler

def preprocesser_for_EncoderDecoder(X_train, Y_train):
    """
    Preprocesses financial data for an Encoder-Decoder model.

    Steps:
    1. Drops any variables that are not Income Statement, Balance Sheet, Dividend, or Equity.
    2. Creates a mask for missing values.
    3. Applies log transformation to non-negative variables (Balance Sheet, Income Statement, Dividends).
    4. Computes percentage change for stock prices (Equity variables).
    5. Handles infinity and large numbers by clipping.
    6. Normalizes values using StandardScaler.
    7. Converts processed data into PyTorch tensors.

    Args:
        X_train (pd.DataFrame): Input features (financial variables before missing values).
        Y_train (pd.DataFrame): Target values (financial variables after missing values).

    Returns:
        tuple: Processed (X_train_tensor, Y_train_tensor, mask_tensor)
    """

    X_train = X_train.copy()
    Y_train = Y_train.copy()

    # Step 1: Keep only relevant columns
    valid_categories = ["Balance_Sheet", "Income_Statement", "Dividend", "Equity"]

    selected_columns_X_train = [col for col in X_train.columns if any(cat in col for cat in valid_categories)]
    selected_columns_Y_train = [col for col in Y_train.columns if any(cat in col for cat in valid_categories)]

    X_train = X_train[selected_columns_X_train]
    Y_train = Y_train[selected_columns_Y_train]

    # Step 2: Create Mask for Missing Values (1 = available, 0 = missing)
    mask = (~X_train.isna()).astype(float)

    # Step 3: Fill NaNs Temporarily (to avoid issues during transformations)
    X_train.fillna(0, inplace=True)  # Will be ignored using mask
    Y_train.fillna(0, inplace=True)

    # Step 4: Handle extreme values and infinities
    max_float = np.finfo(np.float64).max  # Maximum float64 value
    min_float = np.finfo(np.float64).min  # Minimum float64 value

    X_train = X_train.applymap(lambda x: np.nan_to_num(x, nan=0, posinf=max_float, neginf=min_float))
    Y_train = Y_train.applymap(lambda x: np.nan_to_num(x, nan=0, posinf=max_float, neginf=min_float))

    # Step 5: Log Transformation for Non-Negative Financial Values (Balance Sheet, Income Statement, Dividends)
    balance_income_cols_X_train = [col for col in X_train.columns if 'Balance_Sheet' in col or 'Income_Statement' in col]
    dividend_cols_X_train = [col for col in X_train.columns if 'Dividend' in col]
    log_transform_cols_X_train = balance_income_cols_X_train + dividend_cols_X_train

    balance_income_cols_Y_train = [col for col in Y_train.columns if 'Balance_Sheet' in col or 'Income_Statement' in col]
    dividend_cols_Y_train = [col for col in Y_train.columns if 'Dividend' in col]
    log_transform_cols_Y_train = balance_income_cols_Y_train + dividend_cols_Y_train

    # Apply log transformation only to non-negative values
    X_train[log_transform_cols_X_train] = np.log1p(np.maximum(X_train[log_transform_cols_X_train], 0))
    Y_train[log_transform_cols_Y_train] = np.log1p(np.maximum(Y_train[log_transform_cols_Y_train], 0))

    # Step 6: Percentage Change for Stock Prices (Equity Variables)
    equity_cols_X_train  = [col for col in X_train.columns if 'Equity' in col]
    equity_cols_Y_train  = [col for col in Y_train.columns if 'Equity' in col]

    def safe_pct_change(df, epsilon=1e-8):
        """ Computes pct_change while avoiding division by zero and infinite values. """
        df = df.copy()

        import pdb
        pdb.set_trace()

        df.replace(0, epsilon, inplace=True)  # Prevent division by zero
        pct_df = df.pct_change()
        pct_df.replace([np.inf, -np.inf], np.nan, inplace=True)  # Remove infinities
        pct_df = pct_df[(pct_df != -1).all(axis=1)]  # Remove rows containing -1
        return pct_df.dropna()  # Drop NaNs

    X_train_pct = safe_pct_change(X_train[equity_cols_X_train])
    Y_train_pct = safe_pct_change(Y_train[equity_cols_Y_train])

    # Step 6: Align X_train and Y_train (drop same rows from both)
    common_indices = X_train_pct.index.intersection(Y_train_pct.index)  # Get matching indices
    X_train = X_train.loc[common_indices]
    Y_train = Y_train.loc[common_indices]
    mask = mask.loc[common_indices]

    # Step 7: Normalize Data using StandardScaler


    import pdb
    pdb.set_trace()


    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  # Now X_train is a NumPy array
    Y_train_scaled = scaler.transform(Y_train)  # Now Y_train is a NumPy array

    # Step 8: Convert to PyTorch Tensors
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    Y_train_tensor = torch.tensor(Y_train_scaled, dtype=torch.float32)
    mask_tensor = torch.tensor(mask.values, dtype=torch.float32)  # Mask remains a DataFrame, so use `.values`

    return X_train_tensor, Y_train_tensor, mask_tensor







def dataframe_to_tensor(df, fillna_method="zero"):
    """
    Converts a Pandas DataFrame to a PyTorch tensor while handling missing values.

    Args:
        df (pd.DataFrame): Input DataFrame.
        fillna_method (str): Method to fill NaN values. Options:
            - "zero" (default): Fills NaNs with 0.
            - "mean": Fills NaNs with the column mean.

    Returns:
        X_tensor (torch.Tensor): The transformed PyTorch tensor.
        mask_tensor (torch.Tensor): A mask tensor (1 for available data, 0 for missing data).
    """

    # Convert all columns to numeric
    df = df.apply(pd.to_numeric, errors="coerce").astype(np.float32)

    # Create a mask (1 = available, 0 = missing)
    mask = ~df.isna()
    mask_tensor = torch.tensor(mask.values, dtype=torch.float32)

    # Fill NaN values based on the selected method
    if fillna_method == "zero":
        df_filled = df.fillna(0)
    elif fillna_method == "mean":
        df_filled = df.fillna(df.mean())
    else:
        raise ValueError("Invalid fillna_method. Choose 'zero' or 'mean'.")

    # Convert to PyTorch tensor
    X_tensor = torch.tensor(df_filled.values, dtype=torch.float32)

    return X_tensor, mask_tensor

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

                        if df.loc[df['Quarter'] == output_quarter].shape[0]==pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1).shape[0]:
                    
                            input_data.append(pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1))
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



# Example usage
# X_tensor, mask_tensor = dataframe_to_tensor(X_train, fillna_method="mean")

X_train_tensor,Y_train_tensor,mask_tensor=preprocesser_for_EncoderDecoder(X_train, Y_train)

import pdb
pdb.set_trace()


X_tensor, mask_tensor = dataframe_to_tensor(X_train, fillna_method="mean")
Y_tensor, mask_tensor = dataframe_to_tensor(Y_train, fillna_method="mean")


# Reshape tensors to match the expected input shape
X_tensor = X_tensor.view(X_tensor.shape[0], 1, X_tensor.shape[1])  # (batch_size, seq_len, features)
Y_tensor = Y_tensor.view(Y_tensor.shape[0], 1, Y_tensor.shape[1])  # (batch_size, seq_len, features)

# Generate a mask (1 = available data, 0 = missing values)
mask = torch.ones_like(Y_tensor)



input_size = X_tensor.shape[2]  
output_size = Y_tensor.shape[2]  
hidden_size = 64
latent_size = 32
learning_rate = 0.001
seq_len = 1

model = EncoderDecoder(input_size, hidden_size, latent_size, output_size, learning_rate)

epochs = 10 
model.train_model(X_tensor, Y_tensor, mask, seq_len, epochs)
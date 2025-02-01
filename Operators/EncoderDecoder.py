import torch
import torch.nn as nn
import torch.optim as optim

# Define Encoder
class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size, latent_size):
        super(Encoder, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, latent_size)
    
    def forward(self, x):
        _, (hidden, _) = self.lstm(x)
        latent = self.fc(hidden[-1])
        return latent

# Define Decoder
class Decoder(nn.Module):
    def __init__(self, latent_size, hidden_size, output_size):
        super(Decoder, self).__init__()
        self.fc = nn.Linear(latent_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.output_layer = nn.Linear(hidden_size, output_size)
    
    def forward(self, latent, seq_len):
        hidden = self.fc(latent).unsqueeze(0)  # Convert latent to hidden state
        cell = torch.zeros_like(hidden)  # Initialize cell state
        
        outputs = []
        input_step = torch.zeros((latent.shape[0], 1, hidden.shape[-1]), device=latent.device)  # Dummy input
        for _ in range(seq_len):
            output, (hidden, cell) = self.lstm(input_step, (hidden, cell))
            output_step = self.output_layer(output.squeeze(1))
            outputs.append(output_step)
            input_step = output.unsqueeze(1)
        
        return torch.stack(outputs, dim=1)

# Define full Encoder-Decoder model with integrated optimization
class EncoderDecoder(nn.Module):
    def __init__(self, input_size, hidden_size, latent_size, output_size, learning_rate=0.001):
        super(EncoderDecoder, self).__init__()
        self.encoder = Encoder(input_size, hidden_size, latent_size)
        self.decoder = Decoder(latent_size, hidden_size, output_size)
        
        # Initialize optimizer and loss function inside the class
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()  # You can change this to a custom loss if needed
    
    def forward(self, x, seq_len):
        latent = self.encoder(x)
        reconstructed_seq = self.decoder(latent, seq_len)
        return reconstructed_seq
    
    def train_step(self, input_data, target_data, mask, seq_len):
        """
        Perform one training step (forward pass, loss calculation, and backpropagation)
        
        Args:
            input_data (Tensor): The input sequence data.
            target_data (Tensor): The target sequence data (what the model tries to predict).
            mask (Tensor): A tensor that indicates missing values (1 for available data, 0 for missing).
            seq_len (int): The length of the sequence (number of time steps).
        
        Returns:
            loss (Tensor): The computed loss for this training step.
        """
        self.train()  # Set the model to training mode
        self.optimizer.zero_grad()  # Clear previous gradients
        
        # Forward pass
        output = self(input_data, seq_len)
        
        # Compute the loss
        loss = self.masked_mse_loss(output, target_data, mask)
        
        # Backpropagation
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def masked_mse_loss(self, predicted, target, mask):
        """
        Calculate MSE loss while ignoring missing values based on the mask.
        """
        loss = (predicted - target) ** 2
        loss = loss * mask  # Apply the mask to ignore the missing values
        loss = loss.sum() / mask.sum()  # Sum over non-missing values and average
        
        return loss
    
    def train_model(self, train_data, target_data, masks, seq_len, epochs=10):
        """
        Train the model using the provided training data.
        
        Args:
            train_data (Tensor): The training input data.
            target_data (Tensor): The target data.
            masks (Tensor): The mask tensor indicating missing values.
            seq_len (int): The sequence length.
            epochs (int): The number of training epochs.
        """
        for epoch in range(epochs):
            total_loss = 0
            for i in range(len(train_data)):
                input_data = train_data[i]
                target_data_sample = target_data[i]
                mask_sample = masks[i]
                
                loss = self.train_step(input_data, target_data_sample, mask_sample, seq_len)
                total_loss += loss
            
            print(f"Epoch [{epoch + 1}/{epochs}], Loss: {total_loss / len(train_data)}")
            
# Example usage
input_size = 10  # Number of financial features
hidden_size = 64
latent_size = 32
output_size = 10  # Same as input_size
learning_rate = 0.001

# Dummy data for training (replace with your actual data)
train_data = torch.randn((32, 10, 10))  # Batch of 32 sequences, each with 10 time steps and 10 features
target_data = train_data.clone()  # Assuming target data is the same as input for this example
masks = torch.randint(0, 2, train_data.shape).float()  # Random mask (1 = available, 0 = missing)
seq_len = 10  # Sequence length

model = EncoderDecoder(input_size, hidden_size, latent_size, output_size, learning_rate)

# Start training the model
model.train_model(train_data, target_data, masks, seq_len, epochs=10)
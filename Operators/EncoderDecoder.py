import torch
import torch.nn as nn
import torch.optim as optim

# Define Encoder
class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size, latent_size):
        super(Encoder, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, latent_size)
    
    def forward(self, x):
        if x.dim() == 2:  # Ensure 3D shape (batch_size, seq_len, input_size)
            x = x.unsqueeze(1)
        
        batch_size = x.shape[0]
        hidden = torch.zeros(1, batch_size, self.hidden_size, device=x.device)
        cell = torch.zeros(1, batch_size, self.hidden_size, device=x.device)

        _, (hidden, cell) = self.lstm(x, (hidden, cell))
        latent = self.fc(hidden[-1])  # Take last layer output

        return latent


# Define Decoder
class Decoder(nn.Module):
    def __init__(self, latent_size, hidden_size, output_size):
        super(Decoder, self).__init__()
        self.fc = nn.Linear(latent_size, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.output_layer = nn.Linear(hidden_size, output_size)
    
    def forward(self, latent, seq_len):
        batch_size = latent.shape[0]
        hidden = self.fc(latent).unsqueeze(0)  # Convert latent to hidden state
        cell = torch.zeros_like(hidden)  # Initialize cell state

        outputs = []
        input_step = torch.zeros((batch_size, 1, hidden.shape[-1]), device=latent.device)  # Dummy input

        for _ in range(seq_len):
            output, (hidden, cell) = self.lstm(input_step, (hidden, cell))
            output_step = self.output_layer(output.squeeze(1))
            outputs.append(output_step)
            input_step = output  # Remove unnecessary `.unsqueeze(1)`

        return torch.stack(outputs, dim=1)

# Define full Encoder-Decoder model
class EncoderDecoder(nn.Module):
    def __init__(self, input_size, hidden_size, latent_size, output_size, learning_rate=0.001):
        super(EncoderDecoder, self).__init__()
        self.encoder = Encoder(input_size, hidden_size, latent_size)
        self.decoder = Decoder(latent_size, hidden_size, output_size)
        
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
    
    def forward(self, x, seq_len):
        latent = self.encoder(x)
        reconstructed_seq = self.decoder(latent, seq_len)
        return reconstructed_seq
    
    def train_step(self, input_data, target_data, mask, seq_len):
        self.train()
        self.optimizer.zero_grad()
        
        # Ensure input shapes are 3D
        input_data = input_data.unsqueeze(0) if input_data.dim() == 2 else input_data
        target_data = target_data.unsqueeze(0) if target_data.dim() == 2 else target_data
        mask = mask.unsqueeze(0) if mask.dim() == 2 else mask

        # Forward pass
        output = self(input_data, seq_len)

        # Compute masked loss
        loss = self.masked_mse_loss(output, target_data, mask)

        # Backpropagation
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def masked_mse_loss(self, predicted, target, mask):
        loss = (predicted - target) ** 2
        loss = loss * mask  
        loss = loss.sum() / torch.clamp(mask.sum(), min=1)  # Prevent division by zero
        
        return loss
    
    def train_model(self, train_data, target_data, masks, seq_len, epochs=10):
        for epoch in range(epochs):
            total_loss = 0
            for i in range(len(train_data)):
                loss = self.train_step(train_data[i], target_data[i], masks[i], seq_len)
                total_loss += loss
            
            print(f"Epoch [{epoch + 1}/{epochs}], Loss: {total_loss / len(train_data)}")


if __name__ == '__main__':      
    input_size = 10  
    hidden_size = 64
    latent_size = 32
    output_size = 10  
    learning_rate = 0.001

    train_data = torch.randn((32, 10, 10))  
    target_data = train_data.clone()


    masks = torch.randint(0, 2, train_data.shape).float()  
    seq_len = 10  

    model = EncoderDecoder(input_size, hidden_size, latent_size, output_size, learning_rate)
    model.train_model(train_data, target_data, masks, seq_len, epochs=10)

import os
import nltk

def setup_nltk():
    # Define the custom NLTK data directory
    nltk_data_dir = "/var/media/nltk_data"
    
    # Ensure the directory exists
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    # Add the custom directory to NLTK's data paths
    nltk.data.path.append(nltk_data_dir)
    
    # Download the necessary NLTK resources
    print(f"Downloading NLTK resources to {nltk_data_dir}...")
    nltk.download('vader_lexicon', download_dir=nltk_data_dir)
    print("NLTK setup complete.")

# Call the setup function
setup_nltk()

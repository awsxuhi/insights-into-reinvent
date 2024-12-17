import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get sensitive information from environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Model configurations
MODEL_CONFIGS = {
    'nova': {
        'model_id': 'us.amazon.nova-pro-v1:0',
        'max_tokens': 4000,
        'request_format': 'nova'
    },
    'claude': {
        'model_id': 'anthropic.claude-3-5-haiku-20241022-v1:0',
        'max_tokens': 2000,
        'request_format': 'claude'
    }
}

# Non-sensitive configurations
PLAYLIST_ID = "PL2yQDdvlhXf_ZsP25dGLTNbrVSphM2JDl"  # all 960 videos
# PLAYLIST_ID = "PL2yQDdvlhXf9IS3DSz6q--R--o79oXpov"  # 9x industry videos

INDUSTRY_KEYWORDS = [
    "(ADM", # Advertising
    "(AES", # Aerospace
    "(AUT", # Automotive
    "(BIO", # Biotechnology
    "(ENU", # Energy
    "(FSI", # Financial Services
    "(GAM", # Gaming
    "(HLS", # Healthcare
    "(MAE", # Media
    "(MFG", # Manufacturing
    "(NFX", # Media Netflix
    "(RCG", # Retail
    "(SPT", # Sports
    "(TLC", # Telecom
    "(WPS", # Government
] 
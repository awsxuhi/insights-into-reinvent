import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get sensitive information from environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Model configurations
MODEL_CONFIGS = {
    'nova': {
        'name': 'nova',
        'type': 'bedrock',
        'model_id': 'us.amazon.nova-pro-v1:0',
        'max_tokens': 4000,
        'content_type': 'application/json',
        'accept': 'application/json'
    },
    'claude': {
        'name': 'claude',
        'type': 'bedrock',
        'model_id': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0', # e.g., us.anthropic.claude-3-sonnet-20240229-v1:0 or us.anthropic.claude-3-5-sonnet-20241022-v2:0
        'max_tokens': 4000,
        'anthropic_version': 'bedrock-2023-05-31',
        'content_type': 'application/json',
        'accept': 'application/json'
    },
    'qwen': {
        'name': 'qwen', # https://qwenlm.github.io/blog/qwen2.5/ for more information about context length and output max tokens, 7B supports 128K context length and 8k output max tokens
        'type': 'sagemaker',
        'endpoint_name': 'DMAA-Model-qwen2-5-7b-instruct-endpoint',
        'max_tokens': 4000, # 8196 is the max tokens for qwen2.5 7B
        'request_format': 'qwen'
    },
    'openai': {
        'name': 'openai', # we are actually using DeepSeek v3
        'type': 'openai',
        'model_id': 'gpt-4-turbo-preview',  # Need to test
        'max_tokens': 4000,
        'api_key': os.getenv('OPENAI_API_KEY', 'sk-default-key-please-replace-with-real-key'), 
        'temperature': 0.7
    },
    'deepseek': {
        'name': 'deepseek',
        'type': 'openai',  # Deepseek is an OpenAI-compatible model
        'model_id': 'deepseek-chat',  # reference: https://api-docs.deepseek.com/
        'max_tokens': 4000,
        'api_key': os.getenv('DEEPSEEK_API_KEY'),
        'temperature': 0.7,
        'base_url': 'https://api.deepseek.com'  # You can also use https://api.deepseek.com/v1
    },
    'openrouter': {
        'name': 'openrouter',
        'type': 'openai',  
        'model_id': 'deepseek/deepseek-chat-v1',  # call deepseek via openrouter
        'max_tokens': 4000,
        'api_key': os.getenv('OPENROUTER_API_KEY'),
        'base_url': 'https://openrouter.ai/api/v1',
        'temperature': 0.7
    },
    # #add new Openai-compatible model here
    # 'new_model': {
    #     'name': 'new_model',
    #     'type': 'openai',
    #     'model_id': 'new-model-id',
    #     'max_tokens': 4000,
    #     'api_key': os.getenv('NEW_MODEL_API_KEY'),
    #     'base_url': 'https://api.new-model.com/v1'  # optional
    # }
}

# YouTube playlist IDs
PLAYLIST_ID = "PL2yQDdvlhXf_ZsP25dGLTNbrVSphM2JDl"  # all 960 videos
# PLAYLIST_ID = "PL2yQDdvlhXf9IS3DSz6q--R--o79oXpov"  # 9x industry videos

# Industry keywords for video classification
INDUSTRY_KEYWORDS = [
    "(ADM",  # Advertising
    "(AES",  # Aerospace
    "(AUT",  # Automotive
    "(BIO",  # Biotechnology
    "(ENU",  # Energy
    "(FSI",  # Financial Services
    "(GAM",  # Gaming
    "(HLS",  # Healthcare
    "(MAE",  # Media
    "(MFG",  # Manufacturing
    "(NFX",  # Media Netflix
    "(RCG",  # Retail
    "(SPT",  # Sports
    "(TLC",  # Telecom
    "(WPS",  # Government
]
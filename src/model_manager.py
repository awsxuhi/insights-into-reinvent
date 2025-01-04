import boto3
import json
import logging
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, MODEL_CONFIGS
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
from openai import OpenAI
import httpx

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, model_config):
        """Initialize model client based on provided configuration
        
        Args:
            model_config (dict): Configuration for specific model
        """
        try:
            self.model_config = model_config
            
            # Initialize client based on model type
            if model_config['type'] == 'openai':
                self._init_openai_client()
            elif model_config['type'] == 'bedrock':
                self._init_bedrock_client()
            elif model_config['type'] == 'sagemaker':
                self._init_sagemaker_client()
            else:
                raise ValueError(f"Unsupported model type: {model_config['type']}")
                
        except Exception as e:
            logger.error(f"Failed to initialize client for {model_config['name']}: {str(e)}")
            raise

    def _init_openai_client(self):
        """Initialize OpenAI-compatible client based on model name"""
        try:
            if not self.model_config.get('api_key'):
                raise ValueError(f"API key not found for {self.model_config['name']}")
            
            # Debug logging
            logger.debug(f"Model config keys: {list(self.model_config.keys())}")
            
            # Initialize client with minimal parameters
            if self.model_config.get('base_url'):
                logger.info(f"Initializing with base_url: {self.model_config['base_url']}")
                self.openai_client = OpenAI(
                    api_key=self.model_config['api_key'],
                    base_url=self.model_config['base_url'],
                    http_client=httpx.Client()  # Create a clean httpx client, otherwise you will get error: "Client.__init__() got an unexpected keyword argument 'proxies'"
                )
            else:
                logger.info("Initializing without base_url")
                self.openai_client = OpenAI(
                    api_key=self.model_config['api_key'],
                    http_client=httpx.Client()  # Create a clean httpx client
                )
            
            logger.info(f"Successfully initialized OpenAI-compatible client for {self.model_config['name']}")
            
        except Exception as e:
            logger.error(f"Error in _init_openai_client: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Stack trace:", exc_info=True)
            raise

    def _init_bedrock_client(self):
        """Initialize AWS Bedrock client"""
        try:
            # Check if credentials are configured in environment
            if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
                logger.info("Using credentials from environment variables")
                # Initialize with explicit credentials
                self.bedrock_runtime = boto3.client(
                    service_name='bedrock-runtime',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION
                )
            else:
                # Use AWS default configuration
                logger.info("Using AWS default credentials")
                session = boto3.Session()
                if not session.get_credentials():
                    raise ValueError("AWS credentials not found")
                    
                self.bedrock_runtime = session.client('bedrock-runtime')
                logger.info("Initialized Bedrock client")
                
        except Exception as e:
            logger.error(f"Failed to initialize clients: {str(e)}")
            raise


    def _init_sagemaker_client(self):
        """Initialize AWS SageMaker client"""
        try:
            # Check if credentials are configured in environment
            if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
                logger.info("Using credentials from environment variables")
                # Initialize with explicit credentials
                self.sagemaker_runtime = boto3.client(
                    service_name='sagemaker-runtime',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION
                )
            else:
                # Use AWS default configuration
                logger.info("Using AWS default credentials")
                session = boto3.Session()
                if not session.get_credentials():
                    raise ValueError("AWS credentials not found")
                    
                self.sagemaker_runtime = session.client('sagemaker-runtime')
                logger.info("Initialized SageMaker client")
                
        except Exception as e:
            logger.error(f"Failed to initialize clients: {str(e)}")
            raise
        
    def _format_prompt_nova(self, prompt):
        """Format prompt for Nova model"""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

    def _format_prompt_claude(self, prompt):
        """Format prompt for Claude models based on model_id
        
        Args:
            prompt (str): The input prompt to format
            
        Returns:
            dict: Formatted prompt structure based on Claude version
        """
        model_config = MODEL_CONFIGS['claude']
        model_id = model_config['model_id']
        
        # Base structure for both versions
        formatted_prompt = {
            "messages": [
                {
                    "role": "user",
                }
            ],
            "max_tokens": model_config['max_tokens'],
            "anthropic_version": model_config['anthropic_version']
        }
        
        # Check model version by model_id
        if 'claude-3-5' in model_id:  # claude 3.x versions
            formatted_prompt["messages"][0]["content"] = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        else:  # claude 3.0 and older versions
            formatted_prompt["messages"][0]["content"] = prompt
            
        return formatted_prompt

    def _format_prompt_qwen(self, prompt):
        """Format prompt for Qwen model"""
        return {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

    def _format_prompt_openai(self, prompt):
        """Format prompt for OpenAI model"""
        return [
            {
                "role": "user",
                "content": prompt
            }
        ]

    def _call_bedrock_nova(self, model_config, prompt):
        """Call Bedrock Nova model"""
        try:
            request_body = self._format_prompt_nova(prompt)
            response = self.bedrock_runtime.invoke_model(
                modelId=model_config['model_id'],
                body=json.dumps(request_body)
            )
            response_body = json.loads(response['body'].read())
            return response_body["output"]["message"]["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error in Nova model call: {str(e)}")
            raise

    def _call_bedrock_claude(self, model_config, prompt):
        """Call Bedrock Claude model"""
        try:
            request_body = self._format_prompt_claude(prompt)
            response = self.bedrock_runtime.invoke_model(
                modelId=model_config['model_id'],
                contentType=model_config['content_type'],
                body=json.dumps(request_body)
            )
            response_body = json.loads(response['body'].read())
            return response_body["content"][0]["text"]
        except Exception as e:
            logger.error(f"Error in Claude model call: {str(e)}")
            raise
        
    def _call_sagemaker_qwen(self, model_config, prompt):
        """Call SageMaker Qwen model"""
        try:
            request_body = self._format_prompt_qwen(prompt)
            response = self.sagemaker_runtime.invoke_endpoint(
                EndpointName=model_config['endpoint_name'],
                Body=json.dumps(request_body),
                ContentType="application/json"
            )
            response_body = json.loads(response['Body'].read())
            return response_body['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error in Qwen model call: {str(e)}")
            raise

    def _call_openai_gpt(self, model_config, prompt):
        """Call OpenAI GPT model"""
        try:
            if not self.openai_client:
                raise ValueError("OpenAI client not initialized. Please check your API key.")
                
            messages = self._format_prompt_openai(prompt)
            response = self.openai_client.chat.completions.create(
                model=model_config['model_id'],
                messages=messages,
                # max_tokens=model_config['max_tokens'],
                # temperature=model_config['temperature']
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in OpenAI model call: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=4, min=4, max=16),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=before_sleep_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
        reraise=True
    )
    def generate_response(self, model_name, prompt):
        """Generate response using specified model with retry mechanism
        
        Args:
            model_name (str): Name of the model to use
            prompt (str): The input prompt
            
        Returns:
            str: Generated response
            
        Raises:
            Exception: If all retry attempts fail
        """
        if model_name not in MODEL_CONFIGS:
            raise ValueError(f"Unsupported model: {model_name}")
            
        model_config = MODEL_CONFIGS[model_name]
        logger.info(f"Generating response using {model_name} model")
        
        try:
            # method_name = f"_call_{model_config['type']}_{model_name}"
            # For OpenAI-compatible models, always use _call_openai_gpt
            method_name = f"_call_openai_gpt" if self.model_config['type'] == 'openai' else f"_call_{self.model_config['type']}_{model_name}"
        
            if not hasattr(self, method_name):
                raise ValueError(f"Method {method_name} not implemented for model {model_name}")
            
            method = getattr(self, method_name)
            return method(model_config, prompt)
            
        except Exception as e:
            logger.error(f"Error in {model_name} model call: {str(e)}")
            raise 
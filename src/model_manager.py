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

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        """Initialize AWS clients with credentials from environment or AWS config"""
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
                self.bedrock_runtime = session.client('bedrock-runtime')
                self.sagemaker_runtime = session.client('sagemaker-runtime')
                
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
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
            method_name = f"_call_{model_config['type']}_{model_name}"
            if not hasattr(self, method_name):
                raise ValueError(f"Method {method_name} not implemented for model {model_name}")
            
            method = getattr(self, method_name)
            return method(model_config, prompt)
            
        except Exception as e:
            logger.error(f"Error in {model_name} model call: {str(e)}")
            raise 
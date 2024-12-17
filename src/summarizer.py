import boto3
import json
import logging
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

logger = logging.getLogger(__name__)

class VideoSummarizer:
    def __init__(self, model_type="nova"):
        logger.info(f"Initializing VideoSummarizer with model type: {model_type}")
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        self.model_type = model_type
        # Simplified model configurations
        self.MODEL_CONFIGS = {
            "nova": "amazon.nova-lite-v1:0",
            "claude": "anthropic.claude-3-5-haiku-20241022-v1:0"
        }

    def _format_request_body(self, prompt):
        logger.debug(f"Formatting request body for model type: {self.model_type}")
        try:
            if self.model_type == "nova":
                return json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "temperature": 0.7,
                        "topP": 1,
                        "maxTokenCount": 1000,
                        "stopSequences": []
                    }
                })
            else:  # claude
                return json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an AI assistant that summarizes AWS re:Invent videos."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7
                })
        except Exception as e:
            logger.error(f"Error in _format_request_body: {str(e)}")
            raise

    def generate_summary(self, video):
        try:
            logger.info(f"Generating summary for video: {video.get('title', '')}")
            
            if self.model_type not in self.MODEL_CONFIGS:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            # Build prompt text
            prompt = f"""
            Please summarize the key points from this AWS re:Invent video:
            Title: {video.get('title', '')}
            Description: {video.get('description', '')}
            Focus on industry-related insights and announcements.
            """
            
            # Prepare request body
            body = self._format_request_body(prompt)
            logger.debug(f"Request body prepared: {body[:100]}...")
            
            # Call model
            response = self.bedrock_runtime.invoke_model(
                modelId=self.MODEL_CONFIGS[self.model_type],
                body=body
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if self.model_type == "nova":
                return response_body['results'][0]['outputText']
            else:  # claude
                return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
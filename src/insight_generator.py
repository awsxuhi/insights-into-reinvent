import boto3
import json
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
import logging

logger = logging.getLogger(__name__)

class InsightGenerator:
    def __init__(self, model_config):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.model_config = model_config
        
    def _prepare_request_body(self, prompt):
        if self.model_config['request_format'] == 'claude':
            return json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.model_config['max_tokens'],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant that analyzes AWS re:Invent content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            })
        else:  # nova format
            return json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": self.model_config['max_tokens'],
                    "temperature": 0.7,
                    "stopSequences": []
                }
            })
            
    def _parse_response(self, response_body):
        if self.model_config['request_format'] == 'claude':
            return response_body['content'][0]['text']
        else:  # nova format
            return response_body['results'][0]['outputText']
    
    def generate_insights(self, summaries):
        try:
            combined_text = "\n".join(summaries)
            
            prompt = f"""
            Based on these summaries of AWS re:Invent industry-related sessions:
            {combined_text}
            
            Please provide:
            1. Key themes and trends
            2. Major announcements
            3. Industry focus areas
            4. Notable use cases
            5. Overall insights and conclusions
            """
            
            body = self._prepare_request_body(prompt)
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_config['model_id'],
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            return self._parse_response(response_body)
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return None 
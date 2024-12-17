import boto3
import json
import logging
import pandas as pd
from typing import List, Dict, Tuple
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, INDUSTRY_KEYWORDS

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    
    def classify_by_keywords(self, videos: List[dict]) -> List[dict]:
        """Classify videos based on industry keywords in titles"""
        industry_videos = []
        
        for video in videos:
            title = video.get('title', '')
            video_id = video.get('video_id', '')
            description = video.get('description', '')
            
            for keyword in INDUSTRY_KEYWORDS:
                if keyword in title:
                    industry = keyword.strip('(')
                    industry_videos.append({
                        'industry': industry,
                        'title': title,
                        'video_id': video_id,
                        'description': description
                    })
        
        return industry_videos

    def classify_by_llm(self, videos: List[dict]) -> List[dict]:
        """Use LLM to classify videos"""
        industry_videos = []
        
        for video in videos:
            try:
                logger.info(f"Analyzing industry relevance for video: {video['title']}")
                category, explanation = self._analyze_industry_relevance(video['description'])
                
                if 'industry' in category:
                    video['industry_relevance'] = explanation
                    industry_videos.append(video)
                    
            except Exception as e:
                logger.error(f"Error processing video {video['title']}: {str(e)}")
                continue
                
        return industry_videos

    def _analyze_industry_relevance(self, description):
        """Analyze if video content is industry-related"""
        try:
            prompt = f"""Analyze if this video content is industry-focused. Consider it industry-focused if it:
            1. Discusses specific industry use cases
            2. Demonstrates industry-specific solutions
            3. Addresses industry-specific challenges
            
            Video description:
            {description}
            
            Respond with 'industry' or 'non-industry' followed by a brief explanation.
            """
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            result = response_body['content'][0]['text'].strip()
            
            lines = result.split('\n', 1)
            category = lines[0].lower()
            explanation = lines[1] if len(lines) > 1 else ""
            
            return category, explanation.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing industry relevance: {str(e)}")
            raise
from src.youtube_client import YouTubeClient
from src.video_processor import VideoProcessor
from src.output_manager import OutputManager
from config.config import (
    PLAYLIST_ID, 
    MODEL_CONFIGS, 
)
import pandas as pd
import os
import sys
import logging
from src.model_manager import ModelManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_file_exists(filename):
    """
    Check if a file exists in the output directory
    Args:
        filename: Name of the file to check
    Returns:
        tuple: (exists, dataframe if exists else None)
    """
    filepath = os.path.join('output', filename)
    if os.path.exists(filepath):
        logger.info(f"Found existing file: {filename}")
        return True, pd.read_csv(filepath)
    return False, None

def step1_get_videos(youtube_client, output_manager):
    """
    Step 1: Get all videos from YouTube playlist
    Returns:
        list: List of video dictionaries
    """
    # Check if we already have the videos
    exists, df = check_file_exists('all_videos.csv')
    if exists:
        logger.info("Using existing all_videos.csv")
        return df.to_dict('records')
    
    # If not, fetch from YouTube
    logger.info("Fetching playlist videos from YouTube...")
    videos = youtube_client.get_playlist_videos(PLAYLIST_ID)
    logger.info(f"Found {len(videos)} videos")
    
    # Save to CSV
    output_manager.save_to_csv(videos, 'all_videos.csv')
    return videos

def step2_filter_industry_videos(video_processor, videos, output_manager):
    """
    Step 2: Filter industry-related videos
    Args:
        videos: List of all videos
    Returns:
        list: List of industry-related videos
    """
    # Check if we already have the industry videos
    exists, df = check_file_exists('industry_videos.csv')
    if exists:
        logger.info("Using existing industry_videos.csv")
        return df.to_dict('records')
    
    # If not, process videos
    logger.info("Filtering industry-related videos...")
    industry_videos = video_processor.classify_by_keywords(videos)
    
    # Convert to DataFrame and sort by industry
    industry_videos_df = pd.DataFrame(industry_videos)
    industry_videos = industry_videos_df.sort_values('industry').to_dict('records')
    logger.info(f"Found {len(industry_videos)} industry-related videos")
    
    # Save to CSV
    output_manager.save_to_csv(industry_videos, 'industry_videos.csv')
    return industry_videos

def generate_industry_insights(videos, model_config):
    """Generate insights for each industry"""
    model_manager = ModelManager()
    
    # Group by industry
    industry_groups = {}
    for video in videos:
        industry = video['industry']
        if industry not in industry_groups:
            industry_groups[industry] = []
        industry_groups[industry].append(video)
    
    # Generate insights for each industry
    industry_insights = []
    for industry, industry_videos in industry_groups.items():
        try:
            logger.info(f"Generating insights for industry: {industry}")
            
            # Collect descriptions for all videos in this industry
            descriptions = [f"<video {i+1}>title: {v['title']}\n\n description: {v['description']}</video {i+1}>" 
                   for i, v in enumerate(industry_videos)]
            titles = [v['title'] for v in industry_videos]
            
            # Format the prompt
            prompt = f"""
            Analyze these AWS re:Invent videos related to {industry} industry:

            Video Descriptions:
            {'\n'.join(descriptions)}

            Please provide a detailed analysis in the following format:

            ### Detailed Analysis

            **Video 1: (title of video 1)**
            - **Use Case:** [Describe the main use case]
            - **Solution:** [List the AWS solutions used]
            - **Customer Story:** [Name the customer and brief description]

            **Video 2: (title of video 2)**
            - **Use Case:** [Describe the main use case]
            - **Solution:** [List the AWS solutions used]
            - **Customer Story:** [Name the customer and brief description]

        [Continue for all videos...]

            ### Conclusion

        Provide a comprehensive conclusion about how the {industry} industry is leveraging AWS services, mentioning key trends, solutions, and customer examples.

            Please ensure:
            1. Each video analysis follows the exact format with Use Case, Solution, and Customer Story.
            2. Solutions should specifically mention AWS services and technologies used.
            3. The conclusion should synthesize the key insights across all videos.
            4. Keep the analysis concise but informative.
            """
            
            try:
                insight = model_manager.generate_response(model_config['name'], prompt)
                
                industry_insights.append({
                    'industry': industry,
                    'video_count': len(industry_videos),
                    'video_titles': '\n'.join(titles),
                    'insights': insight
                })
                
                logger.info(f"Successfully generated insights for {industry}")
                # logger.info(f"Waiting 5 seconds before next API call...")
                # time.sleep(5)
                
            except Exception as e:
                logger.error(f"Failed to generate insights for {industry} after all retries")
                logger.error(f"Error details: {str(e)}")
                raise  # Re-raise the exception to terminate the program
                
        except Exception as e:
            logger.error(f"Fatal error while processing {industry}: {str(e)}")
            sys.exit(1)  # Terminate the program
    
    return industry_insights

def step3_generate_insights(industry_videos, model_config, output_manager):
    """
    Step 3: Generate industry-specific insights
    Args:
        industry_videos: List of industry-related videos
        model_config: Configuration for the LLM model
    Returns:
        list: List of industry insights
    """
    # Check if we already have the insights
    exists, df = check_file_exists('industry_insights.csv')
    if exists:
        logger.info("Using existing industry_insights.csv")
        return df.to_dict('records')
    
    # If not, generate insights
    logger.info("Generating industry-specific insights...")
    industry_insights = generate_industry_insights(industry_videos, model_config)
    
    # Save to CSV
    output_manager.save_to_csv(industry_insights, 'industry_insights.csv')
    logger.info("Industry insights saved to CSV")
    return industry_insights

def generate_overall_conclusion(industry_insights, model_config):
    """Generate overall conclusion across all industries"""
    try:
        # Prepare the prompt
        all_insights = "\n\n".join([
            f"<{insight['industry']} Industry> {insight['insights']} </{insight['industry']} Industry>"
            for insight in industry_insights
        ])
        
        prompt = f"""
        Analyze the following industry-specific insights from AWS re:Invent videos and provide a comprehensive cross-industry analysis:

        {all_insights}

        Please provide a detailed analysis in the following format:

        ### Cross-Industry Trends
        - List major trends that appear across multiple industries
        - Highlight common AWS services and solutions used

        ### Industry-Specific Highlights
        - Note unique or particularly innovative use cases by industry
        - Identify industry-specific challenges and solutions

        ### Key Technologies
        - List the most frequently mentioned AWS services
        - Describe how these services are being applied

        ### Customer Success Patterns
        - Identify common patterns in customer success stories
        - Note any significant transformations or outcomes

        ### Strategic Insights
        - Provide strategic observations about AWS's industry focus
        - Discuss emerging patterns and future directions

        Please ensure the analysis is comprehensive yet concise, focusing on actionable insights.
        """
        
        # Initialize model manager and generate response
        model_manager = ModelManager()
        conclusion = model_manager.generate_response(model_config['name'], prompt)
        
        return conclusion
        
    except Exception as e:
        logger.error(f"Error in generate_overall_conclusion: {str(e)}")
        raise

def step4_generate_conclusion(industry_insights, model_config, output_manager):
    """
    Step 4: Generate overall conclusion from all industry insights
    Args:
        industry_insights: List of industry-specific insights
        model_config: Configuration for the LLM model
    Returns:
        str: Overall conclusion
    """
    # Check if we already have the conclusion
    conclusion_path = os.path.join('output', 'conclusion.txt')
    if os.path.exists(conclusion_path):
        logger.info("Found existing conclusion, exiting...")
        sys.exit(0)
    
    logger.info("Generating overall conclusion...")
    conclusion = generate_overall_conclusion(industry_insights, model_config)
    
    # Save to TXT
    output_manager.save_to_txt(conclusion, 'conclusion.txt')
    logger.info("Conclusion saved to TXT")
    return conclusion

def main():
    # Get model choice from command line argument
    model_choice = 'nova'  # default model
    if len(sys.argv) > 1:
        model_choice = sys.argv[1].lower()
        if model_choice not in MODEL_CONFIGS:
            logger.error(f"Invalid model choice. Available models: {', '.join(MODEL_CONFIGS.keys())}")
            sys.exit(1)
    
    logger.info(f"Using model: {model_choice}")
    model_config = MODEL_CONFIGS[model_choice]
    
    try:
        # Initialize components
        output_manager = OutputManager()
        youtube_client = YouTubeClient()
        video_processor = VideoProcessor()
        
        # Step 1: Get all videos
        videos = step1_get_videos(youtube_client, output_manager)
        
        # Step 2: Filter industry videos
        industry_videos = step2_filter_industry_videos(video_processor, videos, output_manager)
        
        # Step 3: Generate insights
        industry_insights = step3_generate_insights(industry_videos, model_config, output_manager)
        
        # Step 4: Generate conclusion
        conclusion = step4_generate_conclusion(industry_insights, model_config, output_manager)
        
        logger.info("All processing completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
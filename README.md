# AWS re:Invent Industry Video Analyzer

This project analyzes industry-related videos from AWS re:Invent, providing insights and summaries across different industry sectors.

## Features

- Fetches video information from AWS re:Invent YouTube playlist
- Identifies industry-specific content using video metadata
- Generates summaries and insights for each industry sector
- Provides cross-industry analysis and trends
- Supports multiple LLM models (Claude, Nova, and Qwen) for content analysis

## Prerequisites

- Python 3.9+
- AWS Account with Bedrock/SageMaker access
- YouTube Data API credentials
- Required Python packages (see requirements.txt)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/awsxuhi/insights-into-reinvent.git
cd insights-into-reinvent
```

2. Create and activate a virtual environment:

```bash
conda create -n insights-into-reinvent python=3.12
conda activate insights-into-reinvent
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:

   Option 1: Using AWS CLI (Recommended)

   ```bash
   aws configure
   ```

   Option 2: Environment variables in .env file

   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     - YouTube API key
     - AWS credentials (if not using AWS CLI configuration)

## Usage

Run the analyzer with default model (Nova):

```bash
python main.py
```

Or specify a different model:

```bash
python main.py claude
python main.py nova
python main.py qwen
```

## Output Files

The program generates several files in the `output` directory:

- `all_videos.csv`: Complete list of videos from the playlist
- `industry_videos.csv`: Industry-specific videos with classifications
- `industry_insights.csv`: Detailed analysis for each industry
- `conclusion.txt`: Cross-industry analysis and trends
- Timestamped subdirectories containing execution logs

## Industry Categories

- ADM: Advertising
- AES: Aerospace
- AUT: Automotive
- BIO: Biotechnology
- ENU: Energy & Utilities
- FSI: Financial Services
- GAM: Gaming
- HLS: Healthcare & Life Sciences
- MAE: Media & Entertainment
- MFG: Manufacturing
- NFX: Netflix & Media
- RCG: Retail, CPG & Hospitality
- SPT: Sports
- TLC: Telecom
- WPS: Public Sector

## Rate Limiting and Retry Mechanism

### Bedrock/Claude Rate Limiting

Even when using cross-region inference with the "us." prefix in model IDs (e.g., "us.anthropic.claude-3-5-sonnet-20241022-v2:0"), you may still encounter rate limiting from AWS Bedrock/Claude services. This is a built-in protection mechanism to ensure fair usage of the service.

### Retry Implementation

To handle rate limiting gracefully, this project implements a robust retry mechanism in the ModelManager:

- Uses the `tenacity` library for retry logic
- Implements exponential backoff with a multiplier of 4
- Waits between 4 to 16 seconds between retries
- Maximum of 3 retry attempts
- Detailed logging of retry attempts and outcomes

Example from logs:

```
2024-12-24 23:39:23,589 - __main__ - INFO - Generating insights for industry: SPT
2024-12-24 23:39:23,589 - src.model_manager - INFO - Generating response using claude model
2024-12-24 23:39:29,563 - src.model_manager - ERROR - Error in Claude model call: An error occurred (ThrottlingException) when calling the InvokeModel operation (reached max retries: 4): Too many requests, please wait before trying again.
2024-12-24 23:39:29,563 - src.model_manager - ERROR - Error in claude model call: An error occurred (ThrottlingException) when calling the InvokeModel operation (reached max retries: 4): Too many requests, please wait before trying again.
2024-12-24 23:39:29,563 - src.model_manager - INFO - Finished call to 'src.model_manager.ModelManager.generate_response' after 5.974(s), this was the 1st time calling it.
2024-12-24 23:39:29,563 - src.model_manager - INFO - Retrying src.model_manager.ModelManager.generate_response in 4.0 seconds as it raised ThrottlingException: An error occurred (ThrottlingException) when calling the InvokeModel operation (reached max retries: 4): Too many requests, please wait before trying again..
2024-12-24 23:39:33,567 - src.model_manager - INFO - Generating response using claude model
2024-12-24 23:39:56,057 - __main__ - INFO - Successfully generated insights for SPT
2024-12-24 23:39:56,057 - __main__ - INFO - Generating insights for industry: TLC
2024-12-24 23:39:56,057 - src.model_manager - INFO - Generating response using claude model
2024-12-24 23:40:26,325 - __main__ - INFO - Successfully generated insights for TLC
```

This retry mechanism ensures:

- 100% model invocation success rate
- Graceful handling of rate limits
- Automatic recovery from temporary service limitations
- Detailed logging for monitoring and debugging

## Project Structure

```
aws-reinvent-analyzer/
├── config/
│   └── config.py          # Configuration and model settings
├── src/
│   ├── youtube_client.py  # YouTube API interactions
│   ├── video_processor.py # Video classification
│   ├── model_manager.py   # LLM model management
│   └── output_manager.py  # Output file handling
├── requirements.txt       # Python dependencies
├── main.py               # Main execution script
└── README.md             # Project documentation
```

## Error Handling

- Implements retry mechanisms for API calls using tenacity
- Each step checks for existing output files to avoid redundant processing
- Detailed logging in timestamped subdirectories
- Graceful error handling and reporting

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)

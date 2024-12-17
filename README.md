# AWS re:Invent Industry Video Analyzer

This project analyzes industry-related videos from AWS re:Invent, providing insights and summaries across different industry sectors.

## Features

- Fetches video information from AWS re:Invent YouTube playlist
- Identifies industry-specific content using video metadata
- Generates summaries and insights for each industry sector
- Provides cross-industry analysis and trends
- Supports multiple LLM models (Claude and Nova) for content analysis

## Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
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

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     - YouTube API key
     - AWS credentials
     - AWS region

## Usage

Run the analyzer with default model (Nova):

```bash
python main.py
```

Or specify a different model:

```bash
python main.py claude
python main.py nova
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

## Project Structure

```
aws-reinvent-analyzer/
├── config/
│   └── config.py          # Configuration settings
├── src/
│   ├── youtube_client.py  # YouTube API interactions
│   ├── video_processor.py # Video classification
│   ├── summarizer.py      # Content summarization
│   ├── insight_generator.py # Insight generation
│   └── output_manager.py  # Output file handling
├── requirements.txt       # Python dependencies
├── main.py               # Main execution script
└── README.md             # Project documentation
```

## Error Handling

- The program implements retry mechanisms for API calls
- Each step checks for existing output files to avoid redundant processing
- Detailed logging in timestamped subdirectories

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)

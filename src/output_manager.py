import os
import sys
import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class OutputManager:
    def __init__(self):
        # Create output directory if not exists
        os.makedirs('output', exist_ok=True)
        
        # Create timestamp subdirectory for logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = os.path.join('output', timestamp)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup log handlers
        self._setup_logging()
        
        logger.info(f"Created log directory: {self.log_dir}")
    
    def _setup_logging(self):
        # Create formatters and handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File handler
        log_file = os.path.join(self.log_dir, 'execution.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Get root logger and add both handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers = []
        
        # Add both handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def save_to_csv(self, data, filename, use_timestamp=False):
        try:
            # Create DataFrame from all available data
            df = pd.DataFrame(data)
            
            # Determine save path
            if use_timestamp:
                output_path = os.path.join(self.log_dir, filename)
            else:
                output_path = os.path.join('output', filename)
            
            # Save to CSV
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Data saved to {output_path}")
            
            # Log column information
            logger.info(f"Saved columns: {', '.join(df.columns)}")
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")
            sys.exit(1)
    
    def save_to_txt(self, content, filename):
        """
        Save text content to a file in the output directory
        Args:
            content: Text content to save
            filename: Name of the file
        """
        try:
            output_path = os.path.join('output', filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Text saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving text file: {str(e)}")
            raise
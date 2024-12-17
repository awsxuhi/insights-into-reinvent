# This script is used to test download speeds of different pip sources
# Run with: python test_pip_sources.py
import subprocess
import time
import os
import configparser
import sys

def get_default_pip_index():
    """
    Get the default pip source configuration
    Returns:
        str: Current default pip index URL or error message
    """
    try:
        # Run pip config list command
        result = subprocess.run(['pip', 'config', 'list'], capture_output=True, text=True)
        output = result.stdout.strip()
        
        # Look for index-url configuration
        for line in output.split('\n'):
            if 'index-url' in line:
                return line.split('=')[1].strip()
        
        # If no configuration found, return PyPI official source
        return "https://pypi.org/simple (default PyPI)"
    except Exception as e:
        return f"Error getting default source: {str(e)}"

def test_pip_source(source_url, package_name):
    """
    Test download speed for a specific pip source
    Args:
        source_url: URL of the pip source to test
        package_name: Name of the package to install
    Returns:
        tuple: (duration in seconds, success boolean)
    """
    # First uninstall package if exists
    subprocess.run(['pip', 'uninstall', '-y', package_name], capture_output=True)
    
    # Record start time
    start_time = time.time()
    
    # Install package and capture output
    if source_url:
        command = ['pip', 'install', package_name, '-i', source_url]
    else:
        command = ['pip', 'install', package_name]  # Use default source
    
    process = subprocess.run(command, capture_output=True, text=True)
    
    # Record end time
    end_time = time.time()
    
    # Calculate duration
    duration = end_time - start_time
    
    # Uninstall package again
    subprocess.run(['pip', 'uninstall', '-y', package_name], capture_output=True)
    
    return duration, process.returncode == 0

def main():
    # Display current default source
    default_source = get_default_pip_index()
    print(f"Current default pip source: {default_source}\n")
    
    # Test package name
    package_name = 'youtube-transcript-api'
    
    # Sources to test
    sources = {
        'PyPI': 'https://pypi.org/simple',
        'Tsinghua': 'https://pypi.tuna.tsinghua.edu.cn/simple',
        'Default': None
    }
    
    print(f"Testing download speed for package: {package_name}\n")
    
    results = []
    for source_name, source_url in sources.items():
        print(f"Testing {source_name}...")
        duration, success = test_pip_source(source_url, package_name)
        
        if success:
            print(f"{source_name}: {duration:.2f} seconds")
            results.append((source_name, duration))
        else:
            print(f"{source_name}: Failed")
        print()
    
    # Sort and display results
    if results:
        print("\nResults (fastest to slowest):")
        for source_name, duration in sorted(results, key=lambda x: x[1]):
            print(f"{source_name}: {duration:.2f} seconds")

if __name__ == "__main__":
    main() 
## WaybackParamHarvester

A Python script to process URLs from subdomains, focusing on unique parameter combinations.

### Description

This script takes a list of subdomains, uses the 'waybackurls' tool to fetch URLs for each subdomain, and then processes these URLs to:
- Keep only URLs with parameters
- Retain one example of each unique single-parameter URL
- Include all URLs with multiple parameters
- Output the results to a file

### Requirements

- Python 3.12 or later
- waybackurls command-line tool (must be installed and available in your system PATH)

### Installation

1. Ensure Python 3.12 is installed on your system.
2. Install the waybackurls tool. You can find it at: https://github.com/tomnomnom/waybackurls
3. Download the url_processor.py script to your local machine.

### Usage

1. Open a terminal or command prompt.
2. Navigate to the directory containing url_processor.py.
3. Run the script:
   python url_processor.py
4. When prompted, enter the path to your subdomain list file.
5. After processing, enter a name for the output file when prompted.

### Input File Format

The input file should be a plain text file with one subdomain per line. For example:

example.com
sub1.example.com
sub2.example.com

### Output

The script will display the processed URLs on the screen and save them to the specified output file. Each URL will be on a separate line.

### reflector

Run reflector.py if you want to test the outputted parameters for values being reflected.

### Notes

- The script may take some time to run, depending on the number of subdomains and the response time of the waybackurls tool.
- Ensure you have permission to access and scan the subdomains in your list.

### Troubleshooting

- If you encounter a "command not found" error for waybackurls, make sure it's properly installed and added to your system PATH.
- If the script fails to read the input file, check the file path and ensure the file exists and is readable.

### License

This script is provided "as is", without warranty of any kind. Use at your own risk.

### Author

Unrealisedd

Last Updated: 07/09/2024

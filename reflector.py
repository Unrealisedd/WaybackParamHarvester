import requests
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode
import sys
import re
import time
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
from discord_webhook import DiscordWebhook
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom User-Agent
USER_AGENT = "ReflectionChecker/1.0"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def modify_url(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    modified_params = {}
    random_strings = {}
    
    for key, value in query_params.items():
        random_string = generate_random_string()
        modified_params[key] = [f"{value[0]}{random_string}"]
        random_strings[key] = random_string
    
    modified_query = urlencode(modified_params, doseq=True)
    modified_url = parsed._replace(query=modified_query).geturl()
    
    return modified_url, random_strings

def check_reflection(url, random_strings, session, verify_ssl):
    try:
        headers = {"User-Agent": USER_AGENT}
        response = session.get(url, timeout=10, allow_redirects=False, headers=headers, verify=verify_ssl)
        reflected_params = []
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type:
            try:
                json_data = response.json()
                response_text = json.dumps(json_data)
            except json.JSONDecodeError:
                response_text = response.text
        elif 'application/xml' in content_type:
            try:
                root = ET.fromstring(response.content)
                response_text = ET.tostring(root, encoding='unicode')
            except ET.ParseError:
                response_text = response.text
        else:
            response_text = response.text
        
        for key, value in random_strings.items():
            if value in response_text:
                pattern = re.compile(rf'{re.escape(key)}[^&]*{re.escape(value)}')
                if pattern.search(response_text):
                    reflected_params.append(key)
        
        return reflected_params
    except RequestException as e:
        logger.error(f"Error checking {url}: {e}")
        return []

def send_discord_webhook(webhook_url, message):
    try:
        webhook = DiscordWebhook(url=webhook_url, content=message)
        webhook.execute()
    except Exception as e:
        logger.error(f"Error sending Discord webhook: {e}")

def process_url(url, webhook_url, session, verify_ssl):
    logger.info(f"Checking: {url}")
    modified_url, random_strings = modify_url(url)
    reflected_params = check_reflection(modified_url, random_strings, session, verify_ssl)
    
    if reflected_params:
        result = f"Reflected URL: {url}\nReflected Parameters: {', '.join(reflected_params)}\n\n"
        logger.info(result)
        if webhook_url:
            send_discord_webhook(webhook_url, result)
        return result
    else:
        logger.info("No reflection found.")
        return None

def create_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def main():
    input_file = input("Enter the path to the input file containing URLs: ").strip()
    output_file = input("Enter the name for the output file: ").strip()
    webhook_url = input("Enter Discord webhook URL (optional, press Enter to skip): ").strip() or None
    verify_ssl = input("Verify SSL certificates? (y/n): ").strip().lower() == 'y'
    
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    session = create_session()
    
    with open(output_file, 'w') as out_f, ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(process_url, url, webhook_url, session, verify_ssl): url for url in urls}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                out_f.write(result)
            
            # Rate limiting
            time.sleep(0.5)
    
    logger.info(f"\nReflection check completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()

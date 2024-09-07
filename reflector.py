import requests
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode
import sys

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

def check_reflection(url, random_strings):
    try:
        response = requests.get(url, timeout=10)
        reflected_params = []
        
        for key, value in random_strings.items():
            if value in response.text:
                reflected_params.append(key)
        
        return reflected_params
    except requests.RequestException as e:
        print(f"Error checking {url}: {e}")
        return []

def main():
    input_file = input("Enter the path to the input file containing URLs: ").strip()
    output_file = input("Enter the name for the output file: ").strip()
    
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    with open(output_file, 'w') as out_f:
        for url in urls:
            print(f"Checking: {url}")
            modified_url, random_strings = modify_url(url)
            reflected_params = check_reflection(modified_url, random_strings)
            
            if reflected_params:
                result = f"Reflected URL: {url}\nReflected Parameters: {', '.join(reflected_params)}\n\n"
                out_f.write(result)
                print(result)
            else:
                print("No reflection found.")
            
            print("-" * 50)
    
    print(f"\nReflection check completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()
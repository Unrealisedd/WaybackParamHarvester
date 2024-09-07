import subprocess
from urllib.parse import urlparse, parse_qs
import os

def get_wayback_urls(subdomain):
    try:
        result = subprocess.run(['waybackurls', subdomain], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        print(f"Error running waybackurls for {subdomain}")
        return []

def has_parameters(url):
    parsed = urlparse(url)
    return bool(parse_qs(parsed.query))

def get_parameter_signature(url):
    parsed = urlparse(url)
    return frozenset(parse_qs(parsed.query).keys())

def process_subdomains(subdomain_file):
    with open(subdomain_file, 'r') as f:
        subdomains = [line.strip() for line in f]

    unique_urls = {}
    multi_param_urls = set()

    for subdomain in subdomains:
        print(f"Processing {subdomain}...")
        urls = get_wayback_urls(subdomain)
        for url in urls:
            if has_parameters(url):
                signature = get_parameter_signature(url)
                
                # Always include URLs with multiple parameters
                if len(signature) > 1:
                    multi_param_urls.add(url)
                
                # For single parameter URLs, keep the shortest one
                elif signature not in unique_urls or len(url) < len(unique_urls[signature]):
                    unique_urls[signature] = url

    # Combine single parameter URLs and multi-parameter URLs
    result_urls = set(unique_urls.values()) | multi_param_urls
    return sorted(result_urls)

def main():
    subdomain_file = input("Enter the path to the subdomain list file: ").strip()
    
    if not os.path.exists(subdomain_file):
        print("File not found. Please check the path and try again.")
        return

    print("Processing subdomains...")
    processed_urls = process_subdomains(subdomain_file)

    print("\nProcessed URLs:")
    for url in processed_urls:
        print(url)

    output_file = input("\nEnter the name for the output file: ").strip()
    with open(output_file, 'w') as f:
        for url in processed_urls:
            f.write(f"{url}\n")

    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()

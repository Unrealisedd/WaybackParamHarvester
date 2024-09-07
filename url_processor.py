import subprocess
from urllib.parse import urlparse, parse_qs, urlunparse
import os
from collections import defaultdict

def get_wayback_urls(subdomain):
    try:
        result = subprocess.run(['waybackurls', subdomain], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        print(f"Error running waybackurls for {subdomain}")
        return []

def get_url_signature(url):
    parsed = urlparse(url)
    params = frozenset(parse_qs(parsed.query).keys())
    return (parsed.scheme, parsed.netloc, parsed.path, params)

def has_parameters(url):
    parsed = urlparse(url)
    return bool(parse_qs(parsed.query))

def get_parameter_signature(url):
    parsed = urlparse(url)
    return frozenset(parse_qs(parsed.query).keys())

def process_subdomains(subdomain_file):
    with open(subdomain_file, 'r') as f:
        subdomains = [line.strip() for line in f]

    url_groups = defaultdict(list)

    for subdomain in subdomains:
        print(f"Processing {subdomain}...")
        urls = get_wayback_urls(subdomain)
        for url in urls:
            if has_parameters(url):
                signature = get_url_signature(url)
                url_groups[signature].append(url)

    unique_urls = []
    for signature, urls in url_groups.items():
        # Sort URLs by length and choose the shortest one
        shortest_url = min(urls, key=len)
        unique_urls.append(shortest_url)

    return sorted(unique_urls)

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

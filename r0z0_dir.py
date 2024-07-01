from argparse import ArgumentParser
import requests
import concurrent.futures
import logging

def CLI():
    parser = ArgumentParser(description="A tool for directory brute-forcing")
    parser.add_argument('url', help='Provide the URL of the target')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-w', '--wordlist', type=str, help='Path to your custom wordlist file')
    group.add_argument('-LW', '--local_wordlist', action='store_true', help='Use the local predefined wordlist')

    parser.add_argument('-l', '--logfile', type=str, help='Path to the log file')

    args = parser.parse_args()
    return args

def make_request(base_url, directory):
    # Construct the full URL
    full_url = f"{base_url}/{directory}"
    try:
        # Send the GET request
        response = requests.get(full_url)
        # Print status code and URL if the request is successful
        print(f"Status Code: {response.status_code} - URL: {full_url}")
        return response
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Error with {full_url}: {e}")
        return None

def load_wordlist(filepath):
    # Read the wordlist file and return a list of directories
    with open(filepath, 'r') as file:
        directories = [line.strip() for line in file]
    return directories

def setup_logging(logfile=None):
    if logfile:
        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

def log_result(message):
    logging.info(message)
    print(message)

def check_directory(base_url, wordlist, max_workers=10):
    # Use ThreadPoolExecutor to handle concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Dictionary to keep track of future to directory mapping
        future_to_directory = {executor.submit(make_request, base_url, directory): directory for directory in wordlist}

        for future in concurrent.futures.as_completed(future_to_directory):
            directory = future_to_directory[future]
            try:
                response = future.result()
                if response and response.status_code == 200:
                    message = f"Found: {base_url}/{directory}"
                    log_result(message)
            except Exception as e:
                log_result(f"Error with {base_url}/{directory}: {e}")

if __name__ == "__main__":
    args = CLI()
    setup_logging(args.logfile)
    if args.wordlist:
        wordlist = load_wordlist(args.wordlist)
    elif args.local_wordlist:
        wordlist = ['admin', 'login', 'test']
    check_directory(args.url, wordlist)

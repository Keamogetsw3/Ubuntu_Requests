import requests
import os
import hashlib
from urllib.parse import urlparse

# Directory to save downloaded images
SAVE_DIR = "Fetched_Images"

def create_save_directory():
    """Create the directory for storing images if it doesn't exist."""
    os.makedirs(SAVE_DIR, exist_ok=True)

def get_filename_from_url(url):
    """Extracts the filename from a URL, defaults to a hash if missing."""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If URL doesn't contain a filename, generate one using a hash
    if not filename:
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
    return filename

def file_already_exists(filepath):
    """Check if a file already exists to avoid duplicates."""
    return os.path.exists(filepath)

def validate_response_headers(response):
    """
    Validate HTTP headers to ensure the file is safe and appropriate to download.
    - Content-Type must be an image
    - Content-Length should not exceed a reasonable limit
    """
    content_type = response.headers.get('Content-Type', '').lower()
    if not content_type.startswith('image/'):
        raise ValueError("Invalid file type. Only image files are allowed.")

    # Optional: Limit file size to 10 MB for safety
    content_length = response.headers.get('Content-Length')
    if content_length and int(content_length) > 10 * 1024 * 1024:
        raise ValueError("File is too large (limit is 10MB).")

def download_image(url):
    """Fetch and save an image from a given URL with safety checks."""
    try:
        # Fetch the image
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()

        # Validate headers before saving
        validate_response_headers(response)

        # Determine filename and path
        filename = get_filename_from_url(url)
        filepath = os.path.join(SAVE_DIR, filename)

        # Check for duplicates
        if file_already_exists(filepath):
            print(f"⚠ Skipping duplicate: {filename}")
            return

        # Save the image in chunks
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except ValueError as e:
        print(f"✗ Skipping {url}: {e}")
    except Exception as e:
        print(f"✗ Unexpected error for {url}: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    # Get multiple URLs from user
    urls_input = input("Please enter image URLs separated by commas:\n")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    if not urls:
        print("✗ No valid URLs provided. Exiting.")
        return

    # Create save directory
    create_save_directory()

    # Process each URL
    print("\nFetching images...\n")
    for url in urls:
        download_image(url)

    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()

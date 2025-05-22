import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import mimetypes
import datetime # Added for timestamping

LOG_BASE_DIR = "scraper_logs" # Directory for all log files
SUCCESS_LOG_FILE = "successful_downloads.log"
FAILED_LOG_FILE = "failed_downloads.log"

# Global path variables for logs, to be initialized by setup_log_paths()
_SUCCESS_LOG_PATH = None
_FAILED_LOG_PATH = None

# Global set to keep track of URLs that have been processed (queued, downloaded, or failed)
# This prevents redundant downloads and crawling loops.
PROCESSED_URLS = set()
DOWNLOADED_FILES_LOG = set() # To log actual file paths saved

def setup_log_paths():
    """Creates the log directory and sets global paths for log files."""
    global _SUCCESS_LOG_PATH, _FAILED_LOG_PATH

    # LOG_BASE_DIR will be created relative to the script's current working directory.
    # In GitHub Actions, this is typically the repository root.
    log_dir_path = LOG_BASE_DIR
    if not os.path.exists(log_dir_path):
        try:
            os.makedirs(log_dir_path, exist_ok=True)
            print(f"Created log directory: {os.path.abspath(log_dir_path)}")
        except OSError as e:
            print(f"Error creating log directory {log_dir_path}: {e}")
            # If directory creation fails, log paths will remain None, and logging will be skipped.
            return

    _SUCCESS_LOG_PATH = os.path.join(log_dir_path, SUCCESS_LOG_FILE)
    _FAILED_LOG_PATH = os.path.join(log_dir_path, FAILED_LOG_FILE)
    print(f"Success logs will be saved to: {os.path.abspath(_SUCCESS_LOG_PATH)}")
    print(f"Failed logs will be saved to: {os.path.abspath(_FAILED_LOG_PATH)}")

def log_message(log_type, message):
    """Appends a timestamped message to the appropriate log file (success or failed)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_file_to_use = None
    if log_type == "success":
        log_file_to_use = _SUCCESS_LOG_PATH
    elif log_type == "failed":
        log_file_to_use = _FAILED_LOG_PATH

    if not log_file_to_use:
        # This might happen if setup_log_paths() failed to create the directory
        # print(f"Warning: Log path for type '{log_type}' not configured. Message: {message}")
        return

    try:
        with open(log_file_to_use, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    except IOError as e:
        print(f"Error writing to log file {log_file_to_use}: {e}")

def ensure_dir_for_file(file_path):
    """Ensures the directory for a given file_path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            # print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            raise

def scrape_website(start_url, download_folder="scraped_site_output"):
    """
    Scrapes a website starting from start_url, downloading HTML pages and media resources
    from the same domain into the download_folder.
    """
    setup_log_paths() # Initialize log directory and paths

    if not os.path.exists(download_folder):
        try:
            os.makedirs(download_folder)
        except OSError as e:
            print(f"Error creating root download folder {download_folder}: {e}")
            return

    parsed_start_url = urlparse(start_url)
    target_domain = parsed_start_url.netloc

    urls_to_visit_queue = [start_url]

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    PROCESSED_URLS.clear()
    DOWNLOADED_FILES_LOG.clear()

    while urls_to_visit_queue:
        current_url = urls_to_visit_queue.pop(0)

        if current_url in PROCESSED_URLS:
            continue

        PROCESSED_URLS.add(current_url)
        print(f"Processing URL: {current_url}")

        try:
            response = session.get(current_url, timeout=20, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            is_html = 'text/html' in content_type

            # Determine local save path and filename
            url_path_obj = urlparse(current_url)
            path_segments = [s for s in url_path_obj.path.split('/') if s] # clean segments, e.g. ['path', 'to', 'file.html'] or ['dir', 'subdir']

            current_save_dir = download_folder
            filename_base = ""

            if not path_segments: # Root URL (e.g., http://domain.com)
                filename_base = "index"
            else: # Has path segments
                last_segment = path_segments[-1]
                # If path ends with '/' or the last segment has no extension (and it's not an API-like path)
                if url_path_obj.path.endswith('/') or (not os.path.splitext(last_segment)[1] and is_html):
                    # Treat as directory, filename will be index or derived for HTML
                    current_save_dir = os.path.join(download_folder, *path_segments)
                    filename_base = "index"
                else: # Treat as file (e.g. /foo/bar.jpg or /foo/page (if not html, could be resource))
                    if len(path_segments) > 1:
                        current_save_dir = os.path.join(download_folder, *path_segments[:-1])
                    filename_base = last_segment

            # Finalize filename with extension
            actual_filename = filename_base
            if is_html and not actual_filename.lower().endswith((".html", ".htm")):
                actual_filename += ".html"
            elif not os.path.splitext(actual_filename)[1]: # No extension, and not HTML (or HTML already handled)
                guessed_ext = mimetypes.guess_extension(content_type.split(';')[0].strip()) # Get extension from MIME type
                if guessed_ext:
                    actual_filename += guessed_ext

            # Ensure filename is somewhat safe
            actual_filename = "".join(c for c in actual_filename if c.isalnum() or c in ('.', '-', '_'))
            if not actual_filename: actual_filename = "untitled"


            ensure_dir_for_file(os.path.join(current_save_dir, "dummy.txt")) # ensure dir path exists
            local_save_path = os.path.join(current_save_dir, actual_filename)

            # Download the content
            print(f"Downloading {current_url} to {local_save_path}...")
            downloaded_content_for_parsing = None

            if local_save_path in DOWNLOADED_FILES_LOG:
                print(f"Skipping download, file already exists: {local_save_path}")
                if is_html: # If HTML and exists, need to read it for parsing
                    try:
                        with open(local_save_path, 'rb') as f_existing:
                            downloaded_content_for_parsing = f_existing.read()
                    except IOError as e:
                        print(f"Could not read existing HTML file {local_save_path}: {e}")
            else:
                with open(local_save_path, 'wb') as f:
                    html_content_bytes = b""
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        if is_html:
                            html_content_bytes += chunk
                    if is_html:
                        downloaded_content_for_parsing = html_content_bytes
                DOWNLOADED_FILES_LOG.add(local_save_path)
                print(f"Saved {current_url} to {local_save_path}")
                log_message("success", f"SUCCESS: {current_url} -> {local_save_path}")


            if is_html and downloaded_content_for_parsing:
                try:
                    # Use 'lxml' for speed if available, otherwise 'html.parser'
                    try:
                        soup = BeautifulSoup(downloaded_content_for_parsing, 'lxml')
                    except: # BeautifulSoup can raise FeatureNotFound if lxml is not installed
                        soup = BeautifulSoup(downloaded_content_for_parsing, 'html.parser')


                    # Find and queue other HTML pages or resources linked via <a>
                    for link_tag in soup.find_all('a', href=True):
                        href = link_tag['href']
                        absolute_url = urljoin(current_url, href)
                        parsed_abs_url = urlparse(absolute_url)

                        if parsed_abs_url.scheme in ['http', 'https'] and \
                           parsed_abs_url.netloc == target_domain and \
                           absolute_url not in PROCESSED_URLS and \
                           absolute_url not in urls_to_visit_queue:
                            print(f"Queueing linked URL: {absolute_url}")
                            urls_to_visit_queue.append(absolute_url)

                    # Find and queue media/other resources (images, CSS, JS)
                    resource_selectors = {
                        'img': 'src', 'link': 'href', 'script': 'src',
                        'source': 'src', 'video': 'src', 'audio': 'src',
                        'embed': 'src', 'object': 'data'
                    }
                    for tag_name, attr_name in resource_selectors.items():
                        # Special handling for <link> tags to get stylesheets
                        if tag_name == 'link':
                            elements = soup.find_all(tag_name, rel='stylesheet', href=True)
                        else:
                            elements = soup.find_all(tag_name, **{attr_name: True})

                        for tag in elements:
                            resource_url_rel = tag.get(attr_name)
                            if not resource_url_rel or resource_url_rel.startswith(('data:', 'javascript:', '#')):
                                continue

                            absolute_resource_url = urljoin(current_url, resource_url_rel)
                            parsed_resource_url = urlparse(absolute_resource_url)

                            if parsed_resource_url.scheme in ['http', 'https'] and \
                               parsed_resource_url.netloc == target_domain and \
                               absolute_resource_url not in PROCESSED_URLS and \
                               absolute_resource_url not in urls_to_visit_queue:
                                print(f"Queueing resource ({tag_name}): {absolute_resource_url}")
                                urls_to_visit_queue.append(absolute_resource_url)
                except Exception as e_parse:
                    print(f"Error parsing HTML from {current_url}: {e_parse}")


        except requests.RequestException as e:
            print(f"Failed to process {current_url}: {e}")
            log_message("failed", f"FAILED (RequestException): {current_url} - Error: {e}")
        except Exception as e: # Catch any other unexpected errors during processing a URL
            print(f"An unexpected error occurred while processing {current_url}: {e}")
            log_message("failed", f"FAILED (Exception): {current_url} - Error: {e}")

        time.sleep(0.25) # Politeness delay

    print("\\nScraping finished.")
    print(f"Processed {len(PROCESSED_URLS)} unique URLs.")
    print(f"Attempted to download files to {len(DOWNLOADED_FILES_LOG)} unique local paths.")

if __name__ == "__main__":
    # Get site and folder from user or use defaults
    default_site = "https://www.bucketheadpikes.com"
    # Try to get from environment variables first
    site_to_scrape = os.environ.get("SCRAPE_URL") or input(f"Enter the full URL of the site to scrape (default: {default_site}): ") or default_site

    default_folder_name_base = urlparse(site_to_scrape).netloc.replace('.', '_')
    if not default_folder_name_base: # Handle cases where URL parsing might fail or netloc is empty
        default_folder_name_base = "default_site"
    default_folder_name = default_folder_name_base + "_scraped"

    output_directory = os.environ.get("OUTPUT_DIR") or input(f"Enter the name for the download folder (default: {default_folder_name}): ") or default_folder_name

    print(f"Starting scrape for: {site_to_scrape}")
    print(f"Content will be saved to: {output_directory}")

    scrape_website(site_to_scrape, output_directory)

    print(f"\\nAll discoverable content from {site_to_scrape} (within the same domain) "
          f"has been attempted to be downloaded to '{output_directory}'.")
    print("Please check the console for any errors during the process.")

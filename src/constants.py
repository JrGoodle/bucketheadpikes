from pathlib import Path
import os

REPO_DIR = current_file_path = Path(__file__).parent.parent
STATIC_CRAWL_DIR = REPO_DIR / 'static_site'
BUILD_DIR = REPO_DIR / 'build'

os.makedirs(os.path.dirname(STATIC_CRAWL_DIR), exist_ok=True)
os.makedirs(os.path.dirname(BUILD_DIR), exist_ok=True)

import os
import re
import requests
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class SecurityFileDownloader:
    def __init__(self, output_dir="temp", timeout=30):
        self.output_dir = output_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded_files = []
        
        # Security-relevant file extensions (excluding CSS files)
        self.security_extensions = {
            '.js', '.jsx', '.ts', '.tsx',  # JavaScript/TypeScript
            '.json', '.xml', '.yaml', '.yml',  # Configuration files
            '.txt', '.md', '.env', '.config',  # Text and config files
            '.php', '.py', '.rb', '.java', '.go', '.cs',  # Server-side scripts
            '.sql', '.db',  # Database files
            '.pem', '.key', '.crt', '.p12',  # Certificate files
            '.properties', '.ini', '.conf'  # Configuration files
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_driver(self):
        """Setup Chrome WebDriver for dynamic content."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def download_file(self, url, filename):
        """Download a single file from URL."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.downloaded_files.append(filepath)
            self.logger.info(f"Downloaded: {filename} from {url}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {str(e)}")
            return None
    
    def extract_security_files_from_html(self, html_content, base_url):
        """Extract security-relevant files and inline scripts from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        file_sources = []
        
        # Find external script files
        script_tags = soup.find_all('script', src=True)
        for script in script_tags:
            src = script.get('src')
            if src:
                full_url = urljoin(base_url, src)
                file_sources.append(('external', full_url, src))
        
        # Find other linked resources (excluding CSS)
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag.get('href')
            if href and self.is_security_relevant_file(href):
                full_url = urljoin(base_url, href)
                file_sources.append(('external', full_url, href))
        
        # Find inline scripts
        inline_scripts = soup.find_all('script', src=False)
        for i, script in enumerate(inline_scripts):
            if script.string and script.string.strip():
                file_sources.append(('inline', script.string, f'inline_{i}.js'))
        
        return file_sources
    
    def is_security_relevant_file(self, url_or_path):
        """Check if a file is security-relevant based on its extension."""
        try:
            parsed = urlparse(url_or_path)
            path = parsed.path.lower()
            
            # Check file extension
            for ext in self.security_extensions:
                if path.endswith(ext):
                    return True
            
            # Check for common security-related filenames
            security_filenames = {
                'robots.txt', 'sitemap.xml', 'crossdomain.xml',
                'security.txt', '.htaccess', 'web.config',
                'package.json', 'composer.json', 'requirements.txt',
                'dockerfile', 'docker-compose.yml'
            }
            
            filename = os.path.basename(path)
            return filename in security_filenames
            
        except Exception:
            return False
    
    def download_from_url(self, url):
        """Download all security-relevant files from a given URL."""
        self.logger.info(f"Starting security file download from: {url}")
        
        try:
            # First, try to get the page with requests
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            html_content = response.text
            
            # Extract security-relevant sources from static HTML
            file_sources = self.extract_security_files_from_html(html_content, url)
            
            # Also try with Selenium for dynamic content
            try:
                driver = self.setup_driver()
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get dynamic content
                dynamic_html = driver.page_source
                dynamic_file_sources = self.extract_security_files_from_html(dynamic_html, url)
                
                # Merge sources (avoid duplicates)
                all_sources = file_sources + [
                    src for src in dynamic_file_sources 
                    if src not in file_sources
                ]
                
                driver.quit()
                
            except Exception as e:
                self.logger.warning(f"Selenium failed, using static content only: {str(e)}")
                all_sources = file_sources
            
            # Download all security-relevant files
            downloaded_count = 0
            for file_type, content_or_url, filename in all_sources:
                if file_type == 'external':
                    # Download external file
                    safe_filename = self.sanitize_filename(filename)
                    if self.download_file(content_or_url, safe_filename):
                        downloaded_count += 1
                        
                elif file_type == 'inline':
                    # Save inline content
                    filepath = os.path.join(self.output_dir, filename)
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content_or_url)
                        self.downloaded_files.append(filepath)
                        downloaded_count += 1
                        self.logger.info(f"Saved inline content: {filename}")
                    except Exception as e:
                        self.logger.error(f"Failed to save inline content: {str(e)}")
            
            self.logger.info(f"Downloaded {downloaded_count} security-relevant files")
            return self.downloaded_files
            
        except Exception as e:
            self.logger.error(f"Failed to process URL {url}: {str(e)}")
            return []
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe file system usage."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Extract file extension
        parsed_url = urlparse(filename)
        path = parsed_url.path
        
        # Get the actual filename from the path
        actual_filename = os.path.basename(path)
        
        # If no extension, try to determine from URL parameters or default to .txt
        if '.' not in actual_filename:
            # Check URL parameters for hints
            if 'js' in filename.lower() or 'javascript' in filename.lower():
                actual_filename += '.js'
            elif 'css' in filename.lower() or 'style' in filename.lower():
                actual_filename += '.css'
            elif 'json' in filename.lower():
                actual_filename += '.json'
            elif 'xml' in filename.lower():
                actual_filename += '.xml'
            else:
                actual_filename += '.txt'
        
        # Limit length
        if len(actual_filename) > 100:
            name, ext = os.path.splitext(actual_filename)
            actual_filename = name[:96] + ext
        
        return actual_filename
    
    def cleanup(self):
        """Clean up downloaded files."""
        for filepath in self.downloaded_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                self.logger.error(f"Failed to cleanup {filepath}: {str(e)}")
        
        self.downloaded_files.clear()
    
    def get_downloaded_files(self):
        """Get list of downloaded files."""
        return self.downloaded_files.copy()
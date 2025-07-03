#!/usr/bin/env python3
"""
Source Code Scanner
Command-line interface for scanning security-relevant files from URLs
"""

import os
import sys
import click
import logging
import tempfile
import shutil
from datetime import datetime
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

# Load environment variables
load_dotenv()

# Add scanner module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner.downloader import SecurityFileDownloader
from scanner.semgrep_scan import SemgrepScanner
from scanner.grype_scan import GrypeScanner
from scanner.trufflehog_scan import TruffleHogScanner
from scanner.report_generator import ReportGenerator

class SourceCodeScanner:
    def __init__(self, output_dir="output", temp_dir="temp", verbose=False):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.verbose = verbose
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.downloader = SecurityFileDownloader(output_dir=temp_dir)
        self.semgrep_scanner = SemgrepScanner()
        self.grype_scanner = GrypeScanner()
        self.trufflehog_scanner = TruffleHogScanner()
        self.report_generator = ReportGenerator(output_dir=output_dir)
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File handler
        log_file = os.getenv('LOG_FILE', 'scanner.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        
        # Setup root logger
        logging.basicConfig(
            level=log_level,
            handlers=[console_handler, file_handler]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def print_banner(self):
        """Print application banner."""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    Source Code Scanner                     ║
║                                                              ║
║  Tools: Semgrep | Grype | TruffleHog                       ║
║  Version: 1.0.0                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    def print_status(self, message, status="INFO"):
        """Print colored status message."""
        colors = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }
        color = colors.get(status, Fore.WHITE)
        print(f"{color}[{status}]{Style.RESET_ALL} {message}")
    
    def scan_url(self, url):
        """Main scanning function."""
        self.print_status(f"Starting scan for: {url}")
        
        scan_results = {
            "target_url": url,
            "scan_timestamp": datetime.now().isoformat(),
            "downloaded_files": [],
            "semgrep": {},
            "grype": {},
            "trufflehog": {}
        }
        
        try:
            # Step 1: Download security-relevant files
            self.print_status("Downloading security-relevant files...", "INFO")
            downloaded_files = self.downloader.download_from_url(url)
            
            if not downloaded_files:
                self.print_status("No security-relevant files found to scan", "WARNING")
                return scan_results
            
            scan_results["downloaded_files"] = downloaded_files
            self.print_status(f"Downloaded {len(downloaded_files)} security-relevant files", "SUCCESS")
            
            # Step 2: Run Semgrep scan
            self.print_status("Running static code analysis (Semgrep)...", "INFO")
            semgrep_results = self.semgrep_scanner.scan_files(downloaded_files)
            scan_results["semgrep"] = semgrep_results
            
            if "error" in semgrep_results:
                self.print_status(f"Semgrep scan failed: {semgrep_results['error']}", "WARNING")
            else:
                findings = len(semgrep_results.get("results", []))
                self.print_status(f"Semgrep found {findings} potential security issues", "SUCCESS")
            
            # Step 3: Run Grype scan (look for dependency files)
            self.print_status("Scanning for dependency vulnerabilities (Grype)...", "INFO")
            search_paths = [self.temp_dir] + downloaded_files
            grype_results = self.grype_scanner.scan_dependencies(search_paths)
            scan_results["grype"] = grype_results
            
            if "error" in grype_results:
                self.print_status(f"Grype scan failed: {grype_results['error']}", "WARNING")
            else:
                vulns = len(grype_results.get("results", []))
                self.print_status(f"Grype found {vulns} dependency vulnerabilities", "SUCCESS")
            
            # Step 4: Run TruffleHog scan
            self.print_status("Scanning for secrets (TruffleHog)...", "INFO")
            trufflehog_results = self.trufflehog_scanner.scan_files(downloaded_files)
            scan_results["trufflehog"] = trufflehog_results
            
            secrets = len(trufflehog_results.get("results", []))
            self.print_status(f"TruffleHog found {secrets} potential secrets", "SUCCESS")
            
            # Step 5: Generate reports
            self.print_status("Generating reports...", "INFO")
            report_paths = self.report_generator.generate_reports(scan_results, url)
            
            self.print_status(f"JSON report: {report_paths['json_report']}", "SUCCESS")
            self.print_status(f"PDF report: {report_paths['pdf_report']}", "SUCCESS")
            
            # Print summary
            self.print_scan_summary(scan_results)
            
            return scan_results
            
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            self.print_status(f"Scan failed: {str(e)}", "ERROR")
            raise
        
        finally:
            # Cleanup temporary files
            self.cleanup_temp_files()
    
    def print_scan_summary(self, scan_results):
        """Print scan summary."""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}                    SCAN SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # Files scanned
        files_count = len(scan_results.get("downloaded_files", []))
        print(f"Files Scanned: {files_count}")
        
        # Semgrep results
        semgrep_summary = scan_results.get("semgrep", {}).get("summary", {})
        semgrep_total = semgrep_summary.get("total_findings", 0)
        semgrep_high = semgrep_summary.get("high_severity", 0)
        semgrep_medium = semgrep_summary.get("medium_severity", 0)
        semgrep_low = semgrep_summary.get("low_severity", 0)
        
        print(f"\n{Fore.YELLOW}Static Code Analysis (Semgrep):{Style.RESET_ALL}")
        print(f"  Total Issues: {semgrep_total}")
        if semgrep_high > 0:
            print(f"  {Fore.RED}High Severity: {semgrep_high}{Style.RESET_ALL}")
        if semgrep_medium > 0:
            print(f"  {Fore.YELLOW}Medium Severity: {semgrep_medium}{Style.RESET_ALL}")
        if semgrep_low > 0:
            print(f"  Low Severity: {semgrep_low}")
        
        # Grype results
        grype_summary = scan_results.get("grype", {}).get("summary", {})
        grype_total = grype_summary.get("total_vulnerabilities", 0)
        grype_critical = grype_summary.get("critical_severity", 0)
        grype_high = grype_summary.get("high_severity", 0)
        grype_medium = grype_summary.get("medium_severity", 0)
        
        print(f"\n{Fore.YELLOW}Dependency Vulnerabilities (Grype):{Style.RESET_ALL}")
        print(f"  Total Vulnerabilities: {grype_total}")
        if grype_critical > 0:
            print(f"  {Fore.RED}Critical: {grype_critical}{Style.RESET_ALL}")
        if grype_high > 0:
            print(f"  {Fore.RED}High: {grype_high}{Style.RESET_ALL}")
        if grype_medium > 0:
            print(f"  {Fore.YELLOW}Medium: {grype_medium}{Style.RESET_ALL}")
        
        # TruffleHog results
        trufflehog_summary = scan_results.get("trufflehog", {}).get("summary", {})
        secrets_total = trufflehog_summary.get("total_secrets", 0)
        secrets_high = trufflehog_summary.get("high_confidence", 0)
        secrets_medium = trufflehog_summary.get("medium_confidence", 0)
        
        print(f"\n{Fore.YELLOW}Secret Detection (TruffleHog):{Style.RESET_ALL}")
        print(f"  Total Secrets: {secrets_total}")
        if secrets_high > 0:
            print(f"  {Fore.RED}High Confidence: {secrets_high}{Style.RESET_ALL}")
        if secrets_medium > 0:
            print(f"  {Fore.YELLOW}Medium Confidence: {secrets_medium}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
            self.logger.info("Temporary files cleaned up")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup temp files: {str(e)}")

@click.command()
@click.option('-u', '--url', required=True, help='Target URL to scan for security-relevant files')
@click.option('-o', '--output', default='output', help='Output directory for reports (default: output)')
@click.option('-t', '--temp', default='temp', help='Temporary directory for downloaded files (default: temp)')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
def main(url, output, temp, verbose):
    """Source Code Scanner
    
    Scans security-relevant files from a given URL for:
    - Security vulnerabilities (using Semgrep)
    - Dependency vulnerabilities (using Grype)
    - Secrets and API keys (using TruffleHog)
    
    Supported file types: .js, .ts, .json, .txt, .xml, .yml, .yaml, .env, .config, .ini, .properties, .sql, .py, .php, .rb, .go, .java, .cs, .cpp, .c, .h, .sh, .bat, .ps1, .dockerfile, .pem, .key, .crt, .cer
    
    Example:
        python run.py -u https://example.com
        python run.py -u https://example.com -o reports -v
    """
    
    scanner = SourceCodeScanner(output_dir=output, temp_dir=temp, verbose=verbose)
    scanner.print_banner()
    
    try:
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Run scan
        results = scanner.scan_url(url)
        
        scanner.print_status("Scan completed successfully!", "SUCCESS")
        return 0
        
    except KeyboardInterrupt:
        scanner.print_status("Scan interrupted by user", "WARNING")
        return 1
    except Exception as e:
        scanner.print_status(f"Scan failed: {str(e)}", "ERROR")
        return 1

if __name__ == '__main__':
    sys.exit(main())
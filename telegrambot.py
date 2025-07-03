#!/usr/bin/env python3
"""
Telegram Bot for Source Code Scanner
Allows users to scan URLs through Telegram interface
"""

import os
import sys
import asyncio
import logging
import tempfile
import shutil
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram bot imports
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Add scanner module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanner.downloader import SecurityFileDownloader
from scanner.semgrep_scan import SemgrepScanner
from scanner.grype_scan import GrypeScanner
from scanner.trufflehog_scan import TruffleHogScanner
from scanner.report_generator import ReportGenerator

class TelegramSecurityScanner:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Setup logging
        self.setup_logging()
        
        # Initialize scanner components
        self.output_dir = "bot_output"
        self.temp_dir = "bot_temp"
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.downloader = SecurityFileDownloader(output_dir=self.temp_dir)
        self.semgrep_scanner = SemgrepScanner()
        self.grype_scanner = GrypeScanner()
        self.trufflehog_scanner = TruffleHogScanner()
        self.report_generator = ReportGenerator(output_dir=self.output_dir)
        
        # Active scans tracking
        self.active_scans = {}
    
    def setup_logging(self):
        """Setup logging for the bot."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO,
            handlers=[
                logging.FileHandler('telegram_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🔍 **Source Code Scanner Bot**

I can help you scan security-relevant files from any URL for:
• 🛡️ Security vulnerabilities (Semgrep)
• 📦 Dependency vulnerabilities (Grype)
• 🔑 Secrets and API keys (TruffleHog)

**Supported file types:**
• JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
• Configuration files (.json, .xml, .yaml, .yml)
• Text files (.txt, .md, .env)
• Server-side scripts (.php, .py, .rb, .java)
• Database files (.sql, .db)
• Certificate files (.pem, .key, .crt)

**How to use:**
1. Use `/scan <URL>` command
2. Wait for the scan to complete
3. Receive detailed results in text + PDF and JSON reports

**Commands:**
/start - Show this help message
/help - Show detailed help
/status - Check if any scan is running
/scan <URL> - Scan a specific URL

**Examples:**
• `/scan https://example.com`
• `/scan example.com`
• `/scan github.com/user/repo`

⚠️ **Note:** Scanning may take a few minutes depending on the website size.
"""
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 **Detailed Help**

**What this bot does:**
• Downloads all JavaScript files from a given URL
• Scans for security vulnerabilities using Semgrep
• Checks dependencies for known vulnerabilities using Grype
• Searches for hardcoded secrets using TruffleHog
• Generates comprehensive PDF and JSON reports

**Supported URLs:**
• Any public website (http/https)
• The bot will automatically find and download JS files
• Both inline and external JavaScript files are analyzed

**Report Contents:**
• **PDF Report:** Human-readable summary with recommendations
• **JSON Report:** Structured data for further processing

**Security Tools Used:**
• **Semgrep:** Static analysis for code vulnerabilities
• **Grype:** Dependency vulnerability scanning
• **TruffleHog:** Secret and credential detection

**Limitations:**
• Only scans publicly accessible websites
• Maximum scan time: 10 minutes
• Large websites may take longer to process

**Privacy:**
• Scanned files are automatically deleted after processing
• Reports are only sent to you and then removed from server
"""
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id
        
        if user_id in self.active_scans:
            scan_info = self.active_scans[user_id]
            status_message = f"""
🔄 **Scan Status**

**URL:** {scan_info['url']}
**Started:** {scan_info['start_time']}
**Current Step:** {scan_info['current_step']}

Please wait for the scan to complete...
"""
        else:
            status_message = "✅ No active scans. Send me a URL to start scanning!"
        
        await update.message.reply_text(
            status_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan <URL> command."""
        user_id = update.effective_user.id
        
        # Check if user already has an active scan
        if user_id in self.active_scans:
            await update.message.reply_text(
                "⚠️ You already have an active scan running. Please wait for it to complete."
            )
            return
        
        # Check if URL is provided
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a URL to scan.\n\n**Usage:** `/scan <URL>`\n\n**Examples:**\n• `/scan https://example.com`\n• `/scan example.com`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get URL from command arguments
        url_text = ' '.join(context.args)
        
        # Validate URL
        url = self.validate_url(url_text)
        if not url:
            await update.message.reply_text(
                "❌ Invalid URL. Please provide a valid URL.\n\n**Examples:**\n• `/scan https://example.com`\n• `/scan example.com`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # CLI notification
        self.logger.info(f"New scan request from user {user_id} for URL: {url}")
        print(f"🔍 Starting security scan for: {url}")
        
        # Start scanning
        await self.start_scan(update, url)
    
    async def handle_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL messages and start scanning."""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Check if user already has an active scan
        if user_id in self.active_scans:
            await update.message.reply_text(
                "⚠️ You already have an active scan running. Please wait for it to complete."
            )
            return
        
        # Validate URL
        url = self.validate_url(message_text)
        if not url:
            await update.message.reply_text(
                "❌ Invalid URL. Please send a valid URL starting with http:// or https://"
            )
            return
        
        # CLI notification
        self.logger.info(f"New scan request from user {user_id} for URL: {url}")
        print(f"🔍 Starting security scan for: {url}")
        
        # Start scanning process
        await self.start_scan(update, url)
    
    def validate_url(self, text: str) -> str:
        """Validate and normalize URL."""
        try:
            # Add https if no protocol specified
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            
            # Parse URL to validate
            parsed = urlparse(text)
            if parsed.netloc and parsed.scheme in ['http', 'https']:
                return text
            
            return None
        except:
            return None
    
    async def start_scan(self, update: Update, url: str):
        """Start the scanning process."""
        user_id = update.effective_user.id
        
        # Track active scan
        self.active_scans[user_id] = {
            'url': url,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_step': 'Initializing'
        }
        
        # Send initial message
        status_message = await update.message.reply_text(
            f"🚀 **Starting scan for:** `{url}`\n\n⏳ Initializing scanner...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Create unique temp directory for this scan
            scan_temp_dir = os.path.join(self.temp_dir, f"scan_{user_id}_{int(datetime.now().timestamp())}")
            os.makedirs(scan_temp_dir, exist_ok=True)
            
            # Initialize components for this scan
            downloader = SecurityFileDownloader(output_dir=scan_temp_dir)
            
            scan_results = {
                "target_url": url,
                "scan_timestamp": datetime.now().isoformat(),
                "downloaded_files": [],
                "semgrep": {},
                "grype": {},
                "trufflehog": {}
            }
            
            # Step 1: Download security-relevant files
            self.active_scans[user_id]['current_step'] = 'Downloading security-relevant files'
            await status_message.edit_text(
                f"🚀 **Scanning:** `{url}`\n\n📥 Downloading security-relevant files...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # CLI notification
            print(f"📥 Downloading security-relevant files from {url}...")
            self.logger.info(f"Starting file download for {url}")
            
            downloaded_files = downloader.download_from_url(url)
            scan_results["downloaded_files"] = downloaded_files
            
            if not downloaded_files:
                print(f"❌ No security-relevant files found at {url}")
                self.logger.warning(f"No files downloaded from {url}")
                await status_message.edit_text(
                    f"⚠️ **Scan completed with warnings**\n\n❌ No security-relevant files found at `{url}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            print(f"✅ Downloaded {len(downloaded_files)} security-relevant files")
            self.logger.info(f"Downloaded {len(downloaded_files)} files from {url}")
            
            # Step 2: Semgrep scan
            self.active_scans[user_id]['current_step'] = 'Running static code analysis'
            await status_message.edit_text(
                f"🚀 **Scanning:** `{url}`\n\n🔍 Running static code analysis ({len(downloaded_files)} files)...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # CLI notification
            print(f"🔍 Running Semgrep static code analysis on {len(downloaded_files)} files...")
            self.logger.info(f"Starting Semgrep scan with ruleset: p/security-audit")
            
            semgrep_results = self.semgrep_scanner.scan_files(downloaded_files)
            scan_results["semgrep"] = semgrep_results
            
            semgrep_count = semgrep_results.get('summary', {}).get('total_findings', 0)
            print(f"✅ Semgrep scan completed - Found {semgrep_count} security issues")
            self.logger.info(f"Semgrep scan completed - Found {semgrep_count} issues")
            
            # Step 3: Grype scan
            self.active_scans[user_id]['current_step'] = 'Scanning dependencies'
            await status_message.edit_text(
                f"🚀 **Scanning:** `{url}`\n\n📦 Scanning for dependency vulnerabilities...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # CLI notification
            print(f"📦 Running Grype dependency vulnerability scan...")
            self.logger.info(f"Starting Grype dependency scan")
            
            search_paths = [scan_temp_dir] + downloaded_files
            grype_results = self.grype_scanner.scan_dependencies(search_paths)
            scan_results["grype"] = grype_results
            
            grype_count = grype_results.get('summary', {}).get('total_vulnerabilities', 0)
            print(f"✅ Grype scan completed - Found {grype_count} dependency vulnerabilities")
            self.logger.info(f"Grype scan completed - Found {grype_count} vulnerabilities")
            
            # Step 4: TruffleHog scan
            self.active_scans[user_id]['current_step'] = 'Detecting secrets'
            await status_message.edit_text(
                f"🚀 **Scanning:** `{url}`\n\n🔑 Scanning for secrets and API keys...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # CLI notification
            print(f"🔑 Running TruffleHog secret detection scan...")
            self.logger.info(f"Starting TruffleHog secret detection scan")
            
            trufflehog_results = self.trufflehog_scanner.scan_files(downloaded_files)
            scan_results["trufflehog"] = trufflehog_results
            
            secrets_count = trufflehog_results.get('summary', {}).get('total_secrets', 0)
            print(f"✅ TruffleHog scan completed - Found {secrets_count} potential secrets")
            self.logger.info(f"TruffleHog scan completed - Found {secrets_count} potential secrets")
            
            # Step 5: Generate reports
            self.active_scans[user_id]['current_step'] = 'Generating reports'
            await status_message.edit_text(
                f"🚀 **Scanning:** `{url}`\n\n📄 Generating reports...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # CLI notification
            print(f"📄 Generating PDF and JSON reports...")
            self.logger.info(f"Generating security reports for {url}")
            
            report_paths = self.report_generator.generate_reports(scan_results, url)
            
            print(f"✅ Reports generated successfully")
            self.logger.info(f"Reports generated: {report_paths}")
            
            # Send results
            print(f"📤 Sending reports to user {user_id}...")
            self.logger.info(f"Sending scan results to user {user_id}")
            await self.send_results(update, scan_results, report_paths, status_message)
            
        except Exception as e:
            print(f"❌ Scan failed for {url}: {str(e)}")
            self.logger.error(f"Scan failed for user {user_id}: {str(e)}")
            await status_message.edit_text(
                f"❌ **Scan failed**\n\n🚫 Error: {str(e)[:200]}...",
                parse_mode=ParseMode.MARKDOWN
            )
        
        finally:
            # Cleanup
            if user_id in self.active_scans:
                del self.active_scans[user_id]
            
            # Clean up temporary files
            try:
                if 'scan_temp_dir' in locals() and os.path.exists(scan_temp_dir):
                    shutil.rmtree(scan_temp_dir)
                    print(f"🧹 Cleaned up temporary files for scan")
                    self.logger.info(f"Cleaned up temporary files for user {user_id}")
            except Exception as e:
                print(f"⚠️ Failed to cleanup temp files: {str(e)}")
                self.logger.warning(f"Failed to cleanup temp files: {str(e)}")
    
    async def send_results(self, update: Update, scan_results: dict, report_paths: dict, status_message):
        """Send scan results to user."""
        try:
            # Generate summary
            summary = self.generate_summary_text(scan_results)
            
            # Update status message with summary
            await status_message.edit_text(
                f"✅ **Scan completed successfully!**\n\n{summary}\n\n📎 Sending reports...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send simple message based on findings
            semgrep_total = scan_results.get("semgrep", {}).get("summary", {}).get("total_findings", 0)
            grype_total = scan_results.get("grype", {}).get("summary", {}).get("total_vulnerabilities", 0)
            secrets_total = scan_results.get("trufflehog", {}).get("summary", {}).get("total_secrets", 0)
            
            if semgrep_total == 0 and grype_total == 0 and secrets_total == 0:
                await update.message.reply_text(
                    "✅ **No security issues found!**\n\n🎉 Your scanned files appear to be clean from common security vulnerabilities, dependency issues, and exposed secrets.",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    "⚠️ **Security issues detected!**\n\n📄 Please check the detailed reports for more information.",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Send PDF report
            if os.path.exists(report_paths['pdf_report']):
                print(f"📄 Sending PDF report to user...")
                with open(report_paths['pdf_report'], 'rb') as pdf_file:
                    await update.message.reply_document(
                        document=pdf_file,
                        filename=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        caption="📄 **PDF Report** - Human-readable security analysis"
                    )
            
            # Send JSON report
            if os.path.exists(report_paths['json_report']):
                print(f"📊 Sending JSON report to user...")
                with open(report_paths['json_report'], 'rb') as json_file:
                    await update.message.reply_document(
                        document=json_file,
                        filename=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        caption="📊 **JSON Report** - Structured data for further processing"
                    )
            
            print(f"✅ All reports sent successfully to user")
            self.logger.info(f"Reports sent successfully to user")
            
            # Clean up report files
            for report_path in report_paths.values():
                try:
                    if os.path.exists(report_path):
                        os.remove(report_path)
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup report file {report_path}: {str(e)}")
            
        except Exception as e:
            print(f"❌ Failed to send reports: {str(e)}")
            self.logger.error(f"Failed to send results: {str(e)}")
            await update.message.reply_text(
                "❌ Failed to send reports. Please try again later."
            )
    
    def generate_summary_text(self, scan_results: dict) -> str:
        """Generate summary text for Telegram message."""
        files_count = len(scan_results.get("downloaded_files", []))
        
        # Semgrep summary
        semgrep_summary = scan_results.get("semgrep", {}).get("summary", {})
        semgrep_total = semgrep_summary.get("total_findings", 0)
        semgrep_high = semgrep_summary.get("high_severity", 0)
        
        # Grype summary
        grype_summary = scan_results.get("grype", {}).get("summary", {})
        grype_total = grype_summary.get("total_vulnerabilities", 0)
        grype_critical = grype_summary.get("critical_severity", 0)
        grype_high = grype_summary.get("high_severity", 0)
        
        # TruffleHog summary
        trufflehog_summary = scan_results.get("trufflehog", {}).get("summary", {})
        secrets_total = trufflehog_summary.get("total_secrets", 0)
        secrets_high = trufflehog_summary.get("high_confidence", 0)
        
        summary = f"📊 **Scan Summary:**\n"
        summary += f"• Files scanned: {files_count}\n"
        summary += f"• Security issues: {semgrep_total}"
        if semgrep_high > 0:
            summary += f" ({semgrep_high} high severity)"
        summary += "\n"
        
        summary += f"• Dependency vulnerabilities: {grype_total}"
        if grype_critical > 0 or grype_high > 0:
            summary += f" ({grype_critical + grype_high} critical/high)"
        summary += "\n"
        
        summary += f"• Secrets found: {secrets_total}"
        if secrets_high > 0:
            summary += f" ({secrets_high} high confidence)"
        
        return summary
    
    def generate_detailed_findings(self, scan_results: dict) -> str:
        """Generate detailed findings text for Telegram message."""
        detailed_text = ""
        
        # Semgrep findings
        semgrep_results = scan_results.get("semgrep", {})
        semgrep_findings = semgrep_results.get("findings", [])
        if semgrep_findings:
            detailed_text += "🛡️ **Security Issues (Semgrep):**\n"
            for i, finding in enumerate(semgrep_findings[:10]):  # Limit to first 10
                severity = finding.get('severity', 'unknown').upper()
                rule_id = finding.get('rule_id', 'unknown')
                message = finding.get('message', 'No description')
                file_path = finding.get('path', 'unknown')
                line = finding.get('line', 'unknown')
                
                severity_emoji = "🔴" if severity in ['HIGH', 'CRITICAL'] else "🟡" if severity == 'MEDIUM' else "🟢"
                
                detailed_text += f"{i+1}. {severity_emoji} **{severity}** - {rule_id}\n"
                detailed_text += f"   📄 File: `{file_path}:{line}`\n"
                detailed_text += f"   💬 {message[:100]}{'...' if len(message) > 100 else ''}\n\n"
            
            if len(semgrep_findings) > 10:
                detailed_text += f"   ⚠️ ... and {len(semgrep_findings) - 10} more issues (see PDF report)\n\n"
        
        # Grype findings
        grype_results = scan_results.get("grype", {})
        grype_findings = grype_results.get("matches", [])
        if grype_findings:
            detailed_text += "📦 **Dependency Vulnerabilities (Grype):**\n"
            for i, finding in enumerate(grype_findings[:10]):  # Limit to first 10
                vulnerability = finding.get('vulnerability', {})
                artifact = finding.get('artifact', {})
                
                cve_id = vulnerability.get('id', 'unknown')
                severity = vulnerability.get('severity', 'unknown').upper()
                package_name = artifact.get('name', 'unknown')
                package_version = artifact.get('version', 'unknown')
                description = vulnerability.get('description', 'No description')
                
                severity_emoji = "🔴" if severity in ['HIGH', 'CRITICAL'] else "🟡" if severity == 'MEDIUM' else "🟢"
                
                detailed_text += f"{i+1}. {severity_emoji} **{cve_id}** ({severity})\n"
                detailed_text += f"   📦 Package: `{package_name}@{package_version}`\n"
                detailed_text += f"   💬 {description[:100]}{'...' if len(description) > 100 else ''}\n\n"
            
            if len(grype_findings) > 10:
                detailed_text += f"   ⚠️ ... and {len(grype_findings) - 10} more vulnerabilities (see PDF report)\n\n"
        
        # TruffleHog findings
        trufflehog_results = scan_results.get("trufflehog", {})
        trufflehog_findings = trufflehog_results.get("results", [])
        if trufflehog_findings:
            detailed_text += "🔑 **Secrets Found (TruffleHog):**\n"
            for i, finding in enumerate(trufflehog_findings[:10]):  # Limit to first 10
                detector_name = finding.get('DetectorName', 'unknown')
                source_name = finding.get('SourceName', 'unknown')
                verified = finding.get('Verified', False)
                file_path = finding.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', 'unknown')
                line = finding.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('line', 'unknown')
                
                confidence_emoji = "🔴" if verified else "🟡"
                confidence_text = "HIGH (Verified)" if verified else "MEDIUM (Unverified)"
                
                detailed_text += f"{i+1}. {confidence_emoji} **{detector_name}** ({confidence_text})\n"
                detailed_text += f"   📄 File: `{file_path}:{line}`\n"
                detailed_text += f"   🔍 Source: {source_name}\n\n"
            
            if len(trufflehog_findings) > 10:
                detailed_text += f"   ⚠️ ... and {len(trufflehog_findings) - 10} more secrets (see PDF report)\n\n"
        
        return detailed_text.strip()
    
    def split_message(self, text: str, max_length: int) -> list:
        """Split long message into chunks for Telegram."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        lines = text.split('\n')
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def handle_unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown messages."""
        await update.message.reply_text(
            "🤔 I don't understand that message.\n\n"
            "Please send me a URL to scan, or use /help for more information."
        )
    
    def run(self):
        """Run the Telegram bot."""
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("scan", self.scan_command))  # New scan command
        
        # URL handler (matches URLs)
        url_filter = filters.Regex(r'https?://[^\s]+') | filters.Regex(r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}.*')
        application.add_handler(MessageHandler(url_filter, self.handle_url))
        
        # Unknown message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unknown))
        
        # Start bot
        self.logger.info("Starting Telegram bot...")
        print("🤖 Telegram bot is starting...")
        print("📱 Send /start to your bot to begin!")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the Telegram bot."""
    try:
        bot = TelegramSecurityScanner()
        bot.run()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please set TELEGRAM_BOT_TOKEN in your .env file")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
import os
import json
import subprocess
import logging
import re
from typing import List, Dict, Any

class TruffleHogScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.secret_patterns = {
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "AWS Secret Key": r"[0-9a-zA-Z/+]{40}",
            "GitHub Token": r"ghp_[0-9a-zA-Z]{36}",
            "GitHub App Token": r"ghs_[0-9a-zA-Z]{36}",
            "GitHub Refresh Token": r"ghr_[0-9a-zA-Z]{76}",
            "Google API Key": r"AIza[0-9A-Za-z\-_]{35}",
            "Slack Token": r"xox[baprs]-([0-9a-zA-Z]{10,48})",
            "Discord Token": r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}",
            "Stripe API Key": r"sk_live_[0-9a-zA-Z]{24}",
            "PayPal Client ID": r"A[0-9A-Z]{80}",
            "JWT Token": r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
            "Private Key": r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
            "API Key Generic": r"[aA][pP][iI][_]?[kK][eE][yY][\s]*[=:][\s]*['\"][0-9a-zA-Z]{16,}['\"]?",
            "Password": r"[pP][aA][sS][sS][wW][oO][rR][dD][\s]*[=:][\s]*['\"][^'\"\s]{8,}['\"]?",
            "Secret": r"[sS][eE][cC][rR][eE][tT][\s]*[=:][\s]*['\"][0-9a-zA-Z]{16,}['\"]?",
            "Token": r"[tT][oO][kK][eE][nN][\s]*[=:][\s]*['\"][0-9a-zA-Z]{16,}['\"]?"
        }
    
    def check_trufflehog_installed(self):
        """Check if TruffleHog is installed and accessible."""
        try:
            result = subprocess.run(
                ["trufflehog", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info(f"TruffleHog version: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("TruffleHog not found or not working properly")
                return False
        except Exception as e:
            self.logger.error(f"Failed to check TruffleHog installation: {str(e)}")
            return False
    
    def scan_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Scan JavaScript files for secrets using TruffleHog and custom patterns."""
        trufflehog_available = self.check_trufflehog_installed()
        
        all_results = []
        
        # Use TruffleHog if available
        if trufflehog_available:
            trufflehog_results = self.scan_with_trufflehog(file_paths)
            all_results.extend(trufflehog_results)
        
        # Always run custom pattern matching as backup/supplement
        custom_results = self.scan_with_custom_patterns(file_paths)
        all_results.extend(custom_results)
        
        # Remove duplicates and process results
        processed_results = self.process_results(all_results)
        
        return {
            "results": processed_results,
            "summary": self.generate_summary(processed_results, len(file_paths)),
            "trufflehog_available": trufflehog_available
        }
    
    def scan_with_trufflehog(self, file_paths: List[str]) -> List[Dict]:
        """Scan files using TruffleHog."""
        results = []
        
        for file_path in file_paths:
            try:
                self.logger.info(f"Scanning {file_path} with TruffleHog")
                
                cmd = [
                    "trufflehog",
                    "filesystem",
                    file_path,
                    "--json",
                    "--no-update"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.stdout:
                    # TruffleHog outputs one JSON object per line
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            try:
                                finding = json.loads(line)
                                finding["source_file"] = file_path
                                finding["scanner"] = "trufflehog"
                                results.append(finding)
                            except json.JSONDecodeError:
                                continue
                
                if result.stderr:
                    self.logger.warning(f"TruffleHog stderr for {file_path}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"TruffleHog timeout for file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to scan {file_path} with TruffleHog: {str(e)}")
        
        return results
    
    def scan_with_custom_patterns(self, file_paths: List[str]) -> List[Dict]:
        """Scan files using custom regex patterns."""
        results = []
        
        for file_path in file_paths:
            try:
                self.logger.info(f"Scanning {file_path} with custom patterns")
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for secret_type, pattern in self.secret_patterns.items():
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        
                        for match in matches:
                            # Skip if it looks like a comment or example
                            if self.is_likely_false_positive(line, match.group()):
                                continue
                            
                            result = {
                                "source_file": file_path,
                                "scanner": "custom_regex",
                                "secret_type": secret_type,
                                "line_number": line_num,
                                "column_start": match.start(),
                                "column_end": match.end(),
                                "raw_secret": match.group(),
                                "masked_secret": self.mask_secret(match.group()),
                                "line_content": line.strip(),
                                "confidence": self.calculate_confidence(secret_type, match.group(), line)
                            }
                            
                            results.append(result)
                            
            except Exception as e:
                self.logger.error(f"Failed to scan {file_path} with custom patterns: {str(e)}")
        
        return results
    
    def is_likely_false_positive(self, line: str, secret: str) -> bool:
        """Check if the found secret is likely a false positive."""
        line_lower = line.lower().strip()
        
        # Skip comments
        if line_lower.startswith('//') or line_lower.startswith('#') or line_lower.startswith('*'):
            return True
        
        # Skip obvious examples or placeholders
        false_positive_indicators = [
            'example', 'placeholder', 'dummy', 'test', 'fake', 'sample',
            'your_', 'insert_', 'replace_', 'todo', 'fixme', 'xxx',
            'aaaa', 'bbbb', 'cccc', '1111', '2222', '0000'
        ]
        
        secret_lower = secret.lower()
        for indicator in false_positive_indicators:
            if indicator in secret_lower or indicator in line_lower:
                return True
        
        # Skip if secret is too short for its type
        if len(secret) < 8:
            return True
        
        # Skip if secret contains only repeated characters
        if len(set(secret)) < 3:
            return True
        
        return False
    
    def mask_secret(self, secret: str) -> str:
        """Mask the secret for safe display."""
        if len(secret) <= 8:
            return '*' * len(secret)
        
        visible_chars = 4
        masked_length = len(secret) - (visible_chars * 2)
        
        return secret[:visible_chars] + '*' * masked_length + secret[-visible_chars:]
    
    def calculate_confidence(self, secret_type: str, secret: str, line: str) -> str:
        """Calculate confidence level for the finding."""
        confidence_score = 0
        
        # Base confidence by secret type
        high_confidence_types = ["AWS Access Key", "GitHub Token", "Google API Key"]
        if secret_type in high_confidence_types:
            confidence_score += 3
        else:
            confidence_score += 1
        
        # Length factor
        if len(secret) >= 32:
            confidence_score += 2
        elif len(secret) >= 16:
            confidence_score += 1
        
        # Context factor
        context_keywords = ['api', 'key', 'token', 'secret', 'password', 'auth']
        line_lower = line.lower()
        for keyword in context_keywords:
            if keyword in line_lower:
                confidence_score += 1
                break
        
        # Entropy factor (simple check)
        unique_chars = len(set(secret))
        if unique_chars >= len(secret) * 0.7:
            confidence_score += 1
        
        # Convert to confidence level
        if confidence_score >= 5:
            return "HIGH"
        elif confidence_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def process_results(self, raw_results: List[Dict]) -> List[Dict]:
        """Process and deduplicate results from different scanners."""
        processed = []
        seen_secrets = set()
        
        for result in raw_results:
            try:
                if result.get("scanner") == "trufflehog":
                    processed_result = self.process_trufflehog_result(result)
                else:
                    processed_result = self.process_custom_result(result)
                
                # Create unique identifier for deduplication
                secret_id = f"{processed_result['file_path']}:{processed_result['line_number']}:{processed_result['secret_type']}"
                
                if secret_id not in seen_secrets:
                    seen_secrets.add(secret_id)
                    processed.append(processed_result)
                    
            except Exception as e:
                self.logger.error(f"Failed to process secret result: {str(e)}")
        
        return processed
    
    def process_trufflehog_result(self, result: Dict) -> Dict:
        """Process TruffleHog result format."""
        source_metadata = result.get("SourceMetadata", {})
        
        return {
            "secret_type": result.get("DetectorName", "Unknown"),
            "file_path": result.get("source_file", "unknown"),
            "line_number": source_metadata.get("line", 0),
            "raw_secret": result.get("Raw", ""),
            "masked_secret": self.mask_secret(result.get("Raw", "")),
            "confidence": "HIGH" if result.get("Verified", False) else "MEDIUM",
            "verified": result.get("Verified", False),
            "scanner": "TruffleHog",
            "detector_name": result.get("DetectorName", "Unknown")
        }
    
    def process_custom_result(self, result: Dict) -> Dict:
        """Process custom scanner result format."""
        return {
            "secret_type": result.get("secret_type", "Unknown"),
            "file_path": result.get("source_file", "unknown"),
            "line_number": result.get("line_number", 0),
            "raw_secret": result.get("raw_secret", ""),
            "masked_secret": result.get("masked_secret", ""),
            "confidence": result.get("confidence", "LOW"),
            "verified": False,
            "scanner": "Custom Regex",
            "line_content": result.get("line_content", "")
        }
    
    def generate_summary(self, results: List[Dict], total_files: int) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "total_files": total_files,
            "total_secrets": len(results),
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "verified_secrets": 0,
            "secret_types": {},
            "files_with_secrets": set(),
            "scanners_used": set()
        }
        
        for result in results:
            confidence = result.get("confidence", "LOW")
            secret_type = result.get("secret_type", "Unknown")
            file_path = result.get("file_path", "unknown")
            scanner = result.get("scanner", "Unknown")
            verified = result.get("verified", False)
            
            # Count by confidence
            if confidence == "HIGH":
                summary["high_confidence"] += 1
            elif confidence == "MEDIUM":
                summary["medium_confidence"] += 1
            else:
                summary["low_confidence"] += 1
            
            # Count verified secrets
            if verified:
                summary["verified_secrets"] += 1
            
            # Count by secret type
            summary["secret_types"][secret_type] = summary["secret_types"].get(secret_type, 0) + 1
            
            # Track files with secrets
            summary["files_with_secrets"].add(file_path)
            
            # Track scanners used
            summary["scanners_used"].add(scanner)
        
        # Convert sets to counts
        summary["files_with_secrets"] = len(summary["files_with_secrets"])
        summary["scanners_used"] = list(summary["scanners_used"])
        
        return summary
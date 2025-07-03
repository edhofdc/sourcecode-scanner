import os
import json
import subprocess
import logging
from typing import List, Dict, Any

class SemgrepScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = [
            "p/javascript",
            "p/security-audit",
            "p/owasp-top-ten",
            "p/xss",
            "p/sql-injection",
            "p/command-injection"
        ]
    
    def check_semgrep_installed(self):
        """Check if Semgrep is installed and accessible."""
        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info(f"Semgrep version: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("Semgrep not found or not working properly")
                return False
        except Exception as e:
            self.logger.error(f"Failed to check Semgrep installation: {str(e)}")
            return False
    
    def scan_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Scan JavaScript files using Semgrep."""
        if not self.check_semgrep_installed():
            return {
                "error": "Semgrep not installed or not accessible",
                "results": [],
                "summary": {
                    "total_files": len(file_paths),
                    "total_findings": 0,
                    "high_severity": 0,
                    "medium_severity": 0,
                    "low_severity": 0
                }
            }
        
        if not file_paths:
            return {
                "results": [],
                "summary": {
                    "total_files": 0,
                    "total_findings": 0,
                    "high_severity": 0,
                    "medium_severity": 0,
                    "low_severity": 0
                }
            }
        
        all_results = []
        
        for rule_set in self.rules:
            try:
                self.logger.info(f"Running Semgrep with ruleset: {rule_set}")
                
                # Build command
                cmd = [
                    "semgrep",
                    "--config", rule_set,
                    "--json",
                    "--no-git-ignore",
                    "--timeout", "60"
                ] + file_paths
                
                # Run Semgrep
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.stdout:
                    try:
                        output = json.loads(result.stdout)
                        if "results" in output:
                            all_results.extend(output["results"])
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse Semgrep output for {rule_set}: {str(e)}")
                
                if result.stderr:
                    self.logger.warning(f"Semgrep stderr for {rule_set}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"Semgrep timeout for ruleset: {rule_set}")
            except Exception as e:
                self.logger.error(f"Failed to run Semgrep with {rule_set}: {str(e)}")
        
        # Process and categorize results
        processed_results = self.process_results(all_results)
        
        return {
            "results": processed_results,
            "summary": self.generate_summary(processed_results, len(file_paths))
        }
    
    def process_results(self, raw_results: List[Dict]) -> List[Dict]:
        """Process and enhance Semgrep results."""
        processed = []
        seen_findings = set()
        
        for result in raw_results:
            try:
                # Create unique identifier to avoid duplicates
                finding_id = f"{result.get('path', '')}:{result.get('start', {}).get('line', 0)}:{result.get('check_id', '')}"
                
                if finding_id in seen_findings:
                    continue
                
                seen_findings.add(finding_id)
                
                processed_result = {
                    "rule_id": result.get("check_id", "unknown"),
                    "message": result.get("message", "No message"),
                    "severity": self.map_severity(result.get("extra", {}).get("severity", "INFO")),
                    "file_path": result.get("path", "unknown"),
                    "line_number": result.get("start", {}).get("line", 0),
                    "column_number": result.get("start", {}).get("col", 0),
                    "code_snippet": result.get("extra", {}).get("lines", ""),
                    "category": self.categorize_finding(result.get("check_id", "")),
                    "cwe": self.extract_cwe(result.get("extra", {})),
                    "owasp": self.extract_owasp(result.get("extra", {})),
                    "confidence": result.get("extra", {}).get("metadata", {}).get("confidence", "MEDIUM")
                }
                
                processed.append(processed_result)
                
            except Exception as e:
                self.logger.error(f"Failed to process Semgrep result: {str(e)}")
        
        return processed
    
    def map_severity(self, severity: str) -> str:
        """Map Semgrep severity to standard levels."""
        severity_map = {
            "ERROR": "HIGH",
            "WARNING": "MEDIUM",
            "INFO": "LOW"
        }
        return severity_map.get(severity.upper(), "LOW")
    
    def categorize_finding(self, rule_id: str) -> str:
        """Categorize finding based on rule ID."""
        rule_id_lower = rule_id.lower()
        
        if any(keyword in rule_id_lower for keyword in ["xss", "cross-site"]):
            return "Cross-Site Scripting (XSS)"
        elif any(keyword in rule_id_lower for keyword in ["sql", "injection"]):
            return "SQL Injection"
        elif any(keyword in rule_id_lower for keyword in ["command", "exec"]):
            return "Command Injection"
        elif any(keyword in rule_id_lower for keyword in ["auth", "session"]):
            return "Authentication/Authorization"
        elif any(keyword in rule_id_lower for keyword in ["crypto", "hash", "encrypt"]):
            return "Cryptographic Issues"
        elif any(keyword in rule_id_lower for keyword in ["path", "traversal"]):
            return "Path Traversal"
        elif any(keyword in rule_id_lower for keyword in ["prototype", "pollution"]):
            return "Prototype Pollution"
        elif any(keyword in rule_id_lower for keyword in ["regex", "redos"]):
            return "Regular Expression DoS"
        else:
            return "Security Misconfiguration"
    
    def extract_cwe(self, extra_data: Dict) -> str:
        """Extract CWE information from Semgrep metadata."""
        metadata = extra_data.get("metadata", {})
        cwe = metadata.get("cwe", [])
        if isinstance(cwe, list) and cwe:
            return f"CWE-{cwe[0]}"
        elif isinstance(cwe, str):
            return cwe
        return "N/A"
    
    def extract_owasp(self, extra_data: Dict) -> str:
        """Extract OWASP information from Semgrep metadata."""
        metadata = extra_data.get("metadata", {})
        owasp = metadata.get("owasp", [])
        if isinstance(owasp, list) and owasp:
            return owasp[0]
        elif isinstance(owasp, str):
            return owasp
        return "N/A"
    
    def generate_summary(self, results: List[Dict], total_files: int) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "total_files": total_files,
            "total_findings": len(results),
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "categories": {},
            "top_rules": {}
        }
        
        for result in results:
            severity = result.get("severity", "LOW")
            category = result.get("category", "Unknown")
            rule_id = result.get("rule_id", "unknown")
            
            # Count by severity
            if severity == "HIGH":
                summary["high_severity"] += 1
            elif severity == "MEDIUM":
                summary["medium_severity"] += 1
            else:
                summary["low_severity"] += 1
            
            # Count by category
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            # Count by rule
            summary["top_rules"][rule_id] = summary["top_rules"].get(rule_id, 0) + 1
        
        return summary
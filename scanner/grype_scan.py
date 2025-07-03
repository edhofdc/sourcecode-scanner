import os
import json
import subprocess
import logging
from typing import List, Dict, Any

class GrypeScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_files = [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "npm-shrinkwrap.json",
            "bower.json"
        ]
    
    def check_grype_installed(self):
        """Check if Grype is installed and accessible."""
        try:
            result = subprocess.run(
                ["grype", "version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info(f"Grype version info: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("Grype not found or not working properly")
                return False
        except Exception as e:
            self.logger.error(f"Failed to check Grype installation: {str(e)}")
            return False
    
    def find_dependency_files(self, search_dirs: List[str]) -> List[str]:
        """Find dependency files in the given directories."""
        dependency_files = []
        
        for search_dir in search_dirs:
            if os.path.isfile(search_dir):
                # If it's a file, check if it's a dependency file
                filename = os.path.basename(search_dir)
                if filename in self.supported_files:
                    dependency_files.append(search_dir)
            elif os.path.isdir(search_dir):
                # If it's a directory, search for dependency files
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        if file in self.supported_files:
                            dependency_files.append(os.path.join(root, file))
        
        return dependency_files
    
    def scan_dependencies(self, search_paths: List[str]) -> Dict[str, Any]:
        """Scan for vulnerabilities in JavaScript dependencies."""
        if not self.check_grype_installed():
            return {
                "error": "Grype not installed or not accessible",
                "results": [],
                "summary": {
                    "total_dependencies": 0,
                    "total_vulnerabilities": 0,
                    "critical_severity": 0,
                    "high_severity": 0,
                    "medium_severity": 0,
                    "low_severity": 0,
                    "negligible_severity": 0
                }
            }
        
        # Find dependency files
        dependency_files = self.find_dependency_files(search_paths)
        
        if not dependency_files:
            self.logger.info("No dependency files found")
            return {
                "results": [],
                "summary": {
                    "total_dependencies": 0,
                    "total_vulnerabilities": 0,
                    "critical_severity": 0,
                    "high_severity": 0,
                    "medium_severity": 0,
                    "low_severity": 0,
                    "negligible_severity": 0
                }
            }
        
        all_results = []
        
        for dep_file in dependency_files:
            try:
                self.logger.info(f"Scanning dependency file: {dep_file}")
                
                # Run Grype scan
                cmd = [
                    "grype",
                    dep_file,
                    "-o", "json",
                    "--quiet"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                
                if result.stdout:
                    try:
                        output = json.loads(result.stdout)
                        if "matches" in output:
                            # Add source file info to each match
                            for match in output["matches"]:
                                match["source_file"] = dep_file
                            all_results.extend(output["matches"])
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse Grype output for {dep_file}: {str(e)}")
                
                if result.stderr:
                    self.logger.warning(f"Grype stderr for {dep_file}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.logger.error(f"Grype timeout for file: {dep_file}")
            except Exception as e:
                self.logger.error(f"Failed to scan {dep_file} with Grype: {str(e)}")
        
        # Process results
        processed_results = self.process_results(all_results)
        
        return {
            "results": processed_results,
            "summary": self.generate_summary(processed_results)
        }
    
    def process_results(self, raw_results: List[Dict]) -> List[Dict]:
        """Process and enhance Grype results."""
        processed = []
        seen_vulnerabilities = set()
        
        for result in raw_results:
            try:
                vulnerability = result.get("vulnerability", {})
                artifact = result.get("artifact", {})
                
                # Create unique identifier
                vuln_id = f"{vulnerability.get('id', '')}:{artifact.get('name', '')}:{artifact.get('version', '')}"
                
                if vuln_id in seen_vulnerabilities:
                    continue
                
                seen_vulnerabilities.add(vuln_id)
                
                processed_result = {
                    "vulnerability_id": vulnerability.get("id", "unknown"),
                    "package_name": artifact.get("name", "unknown"),
                    "package_version": artifact.get("version", "unknown"),
                    "package_type": artifact.get("type", "unknown"),
                    "severity": vulnerability.get("severity", "Unknown").upper(),
                    "description": vulnerability.get("description", "No description available"),
                    "cvss_score": self.extract_cvss_score(vulnerability),
                    "cve_id": self.extract_cve_id(vulnerability),
                    "fixed_version": self.extract_fixed_version(result),
                    "source_file": result.get("source_file", "unknown"),
                    "references": vulnerability.get("dataSource", ""),
                    "published_date": vulnerability.get("publishedDate", ""),
                    "last_modified": vulnerability.get("lastModifiedDate", "")
                }
                
                processed.append(processed_result)
                
            except Exception as e:
                self.logger.error(f"Failed to process Grype result: {str(e)}")
        
        return processed
    
    def extract_cvss_score(self, vulnerability: Dict) -> float:
        """Extract CVSS score from vulnerability data."""
        try:
            # Try different possible locations for CVSS score
            cvss_data = vulnerability.get("cvss", [])
            if isinstance(cvss_data, list) and cvss_data:
                for cvss in cvss_data:
                    if isinstance(cvss, dict) and "metrics" in cvss:
                        metrics = cvss["metrics"]
                        if "baseScore" in metrics:
                            return float(metrics["baseScore"])
            
            # Alternative location
            if "severity" in vulnerability:
                severity_map = {
                    "CRITICAL": 9.0,
                    "HIGH": 7.0,
                    "MEDIUM": 5.0,
                    "LOW": 3.0,
                    "NEGLIGIBLE": 1.0
                }
                return severity_map.get(vulnerability["severity"].upper(), 0.0)
            
            return 0.0
        except:
            return 0.0
    
    def extract_cve_id(self, vulnerability: Dict) -> str:
        """Extract CVE ID from vulnerability data."""
        vuln_id = vulnerability.get("id", "")
        if vuln_id.startswith("CVE-"):
            return vuln_id
        
        # Check in related vulnerabilities
        related = vulnerability.get("relatedVulnerabilities", [])
        for rel in related:
            if isinstance(rel, dict) and rel.get("id", "").startswith("CVE-"):
                return rel["id"]
        
        return "N/A"
    
    def extract_fixed_version(self, result: Dict) -> str:
        """Extract fixed version information."""
        try:
            match_details = result.get("matchDetails", [])
            for detail in match_details:
                if isinstance(detail, dict) and "found" in detail:
                    found = detail["found"]
                    if "fixState" in found and found["fixState"] == "fixed":
                        return found.get("versionConstraint", "Available")
            
            return "Not specified"
        except:
            return "Unknown"
    
    def generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "total_dependencies": len(set(f"{r['package_name']}:{r['package_version']}" for r in results)),
            "total_vulnerabilities": len(results),
            "critical_severity": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "negligible_severity": 0,
            "packages_with_vulnerabilities": {},
            "top_vulnerabilities": {},
            "average_cvss_score": 0.0
        }
        
        total_cvss = 0.0
        cvss_count = 0
        
        for result in results:
            severity = result.get("severity", "UNKNOWN")
            package_name = result.get("package_name", "unknown")
            vuln_id = result.get("vulnerability_id", "unknown")
            cvss_score = result.get("cvss_score", 0.0)
            
            # Count by severity
            if severity == "CRITICAL":
                summary["critical_severity"] += 1
            elif severity == "HIGH":
                summary["high_severity"] += 1
            elif severity == "MEDIUM":
                summary["medium_severity"] += 1
            elif severity == "LOW":
                summary["low_severity"] += 1
            else:
                summary["negligible_severity"] += 1
            
            # Count by package
            summary["packages_with_vulnerabilities"][package_name] = \
                summary["packages_with_vulnerabilities"].get(package_name, 0) + 1
            
            # Count by vulnerability
            summary["top_vulnerabilities"][vuln_id] = \
                summary["top_vulnerabilities"].get(vuln_id, 0) + 1
            
            # Calculate average CVSS
            if cvss_score > 0:
                total_cvss += cvss_score
                cvss_count += 1
        
        if cvss_count > 0:
            summary["average_cvss_score"] = round(total_cvss / cvss_count, 2)
        
        return summary
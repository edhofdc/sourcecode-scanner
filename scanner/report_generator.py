import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, red, orange, yellow, green
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class ReportGenerator:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2E86AB'),
            alignment=TA_CENTER
        ))
        
        # Heading styles
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=HexColor('#A23B72'),
            borderWidth=1,
            borderColor=HexColor('#A23B72'),
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=HexColor('#F18F01')
        ))
        
        # Alert styles
        self.styles.add(ParagraphStyle(
            name='HighAlert',
            parent=self.styles['Normal'],
            textColor=red,
            fontSize=12,
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='MediumAlert',
            parent=self.styles['Normal'],
            textColor=orange,
            fontSize=12,
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='LowAlert',
            parent=self.styles['Normal'],
            textColor=HexColor('#FFA500'),
            fontSize=12,
            leftIndent=20
        ))
    
    def generate_reports(self, scan_results: Dict[str, Any], target_url: str) -> Dict[str, str]:
        """Generate both PDF and JSON reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate JSON report
        json_path = os.path.join(self.output_dir, f"result_{timestamp}.json")
        self.generate_json_report(scan_results, target_url, json_path)
        
        # Generate PDF report
        pdf_path = os.path.join(self.output_dir, f"report_{timestamp}.pdf")
        self.generate_pdf_report(scan_results, target_url, pdf_path)
        
        return {
            "json_report": json_path,
            "pdf_report": pdf_path
        }
    
    def generate_json_report(self, scan_results: Dict[str, Any], target_url: str, output_path: str):
        """Generate structured JSON report."""
        try:
            report_data = {
                "scan_metadata": {
                    "target_url": target_url,
                    "scan_timestamp": datetime.now().isoformat(),
                    "scanner_version": "1.0.0",
                    "total_files_scanned": len(scan_results.get("downloaded_files", []))
                },
                "semgrep_results": scan_results.get("semgrep", {}),
                "grype_results": scan_results.get("grype", {}),
                "trufflehog_results": scan_results.get("trufflehog", {}),
                "downloaded_files": scan_results.get("downloaded_files", []),
                "overall_summary": self.generate_overall_summary(scan_results)
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {str(e)}")
            raise
    
    def generate_pdf_report(self, scan_results: Dict[str, Any], target_url: str, output_path: str):
        """Generate human-readable PDF report."""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Title page
            story.extend(self.create_title_page(target_url))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self.create_executive_summary(scan_results))
            story.append(PageBreak())
            
            # Semgrep results
            if scan_results.get("semgrep", {}).get("results"):
                story.extend(self.create_semgrep_section(scan_results["semgrep"]))
                story.append(PageBreak())
            
            # Grype results
            if scan_results.get("grype", {}).get("results"):
                story.extend(self.create_grype_section(scan_results["grype"]))
                story.append(PageBreak())
            
            # TruffleHog results
            if scan_results.get("trufflehog", {}).get("results"):
                story.extend(self.create_trufflehog_section(scan_results["trufflehog"]))
                story.append(PageBreak())
            
            # Recommendations
            story.extend(self.create_recommendations_section(scan_results))
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate PDF report: {str(e)}")
            raise
    
    def create_title_page(self, target_url: str) -> List:
        """Create title page for PDF report."""
        story = []
        
        # Title
        story.append(Paragraph("Security Vulnerability & Secret Scan Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Target info
        story.append(Paragraph(f"<b>Target URL:</b> {target_url}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Scan info
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"<b>Scan Date:</b> {scan_time}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("<b>Scanner Tools & Capabilities:</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("• <b>Semgrep</b> - Static code analysis to identify bugs, security vulnerabilities, and malicious code patterns", self.styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph("• <b>Grype</b> - Vulnerability scanning for dependencies based on CVE/NVD databases", self.styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph("• <b>TruffleHog</b> - Detection of secrets and credentials accidentally exposed in code", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # File types scanned
        story.append(Paragraph("<b>Supported File Types:</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("JavaScript (.js, .ts), Configuration (.json, .xml, .yml, .yaml, .env, .config, .ini, .properties), Text (.txt), Server-side (.py, .php, .rb, .go, .java, .cs, .cpp, .c, .h), Scripts (.sh, .bat, .ps1), Database (.sql), Containers (.dockerfile), Certificates (.pem, .key, .crt, .cer)", self.styles['Normal']))
        
        return story
    
    def create_executive_summary(self, scan_results: Dict[str, Any]) -> List:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading1']))
        
        # Overall statistics
        overall_summary = self.generate_overall_summary(scan_results)
        
        summary_data = [
            ['Metric', 'Count'],
            ['Files Scanned', str(overall_summary['total_files'])],
            ['', ''],
            ['Semgrep - Code Analysis Issues', str(overall_summary['total_issues'])],
            ['  • High Severity', str(overall_summary['high_severity'])],
            ['  • Medium Severity', str(overall_summary['medium_severity'])],
            ['  • Low Severity', str(overall_summary['low_severity'])],
            ['', ''],
            ['Grype - Dependency Vulnerabilities', str(overall_summary['total_vulnerabilities'])],
            ['TruffleHog - Secrets/Credentials', str(overall_summary['total_secrets'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk assessment
        risk_level = self.calculate_risk_level(overall_summary)
        risk_color = self.get_risk_color(risk_level)
        
        story.append(Paragraph("Risk Assessment", self.styles['CustomHeading2']))
        story.append(Paragraph(f"<b>Overall Risk Level: <font color='{risk_color}'>{risk_level}</font></b>", self.styles['Normal']))
        
        return story
    
    def create_semgrep_section(self, semgrep_results: Dict[str, Any]) -> List:
        """Create Semgrep results section."""
        story = []
        
        story.append(Paragraph("Static Code Analysis (Semgrep)", self.styles['CustomHeading1']))
        
        summary = semgrep_results.get('summary', {})
        results = semgrep_results.get('results', [])
        
        # Summary
        story.append(Paragraph(f"Semgrep identified {len(results)} potential security issues through static code analysis. This tool detects bugs, security vulnerabilities, and malicious code patterns based on configured rules.", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Group by severity
        high_issues = [r for r in results if r.get('severity') == 'HIGH']
        medium_issues = [r for r in results if r.get('severity') == 'MEDIUM']
        low_issues = [r for r in results if r.get('severity') == 'LOW']
        
        # High severity issues
        if high_issues:
            story.append(Paragraph("High Severity Issues", self.styles['CustomHeading2']))
            for issue in high_issues[:10]:  # Limit to top 10
                story.append(self.create_issue_paragraph(issue, 'HighAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        # Medium severity issues
        if medium_issues:
            story.append(Paragraph("Medium Severity Issues", self.styles['CustomHeading2']))
            for issue in medium_issues[:10]:  # Limit to top 10
                story.append(self.create_issue_paragraph(issue, 'MediumAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        # Low severity issues summary
        if low_issues:
            story.append(Paragraph(f"Low Severity Issues: {len(low_issues)} found", self.styles['CustomHeading2']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def create_grype_section(self, grype_results: Dict[str, Any]) -> List:
        """Create Grype results section."""
        story = []
        
        story.append(Paragraph("Dependency Vulnerabilities (Grype)", self.styles['CustomHeading1']))
        
        results = grype_results.get('results', [])
        summary = grype_results.get('summary', {})
        
        story.append(Paragraph(f"Grype identified {len(results)} vulnerabilities in dependencies. This tool scans application packages to find CVE (Common Vulnerabilities and Exposures) based on databases such as NVD (National Vulnerability Database).", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Group by severity
        critical_vulns = [r for r in results if r.get('severity') == 'CRITICAL']
        high_vulns = [r for r in results if r.get('severity') == 'HIGH']
        medium_vulns = [r for r in results if r.get('severity') == 'MEDIUM']
        
        # Critical vulnerabilities
        if critical_vulns:
            story.append(Paragraph("Critical Vulnerabilities", self.styles['CustomHeading2']))
            for vuln in critical_vulns[:10]:
                story.append(self.create_vulnerability_paragraph(vuln, 'HighAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        # High vulnerabilities
        if high_vulns:
            story.append(Paragraph("High Severity Vulnerabilities", self.styles['CustomHeading2']))
            for vuln in high_vulns[:10]:
                story.append(self.create_vulnerability_paragraph(vuln, 'HighAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        # Medium vulnerabilities summary
        if medium_vulns:
            story.append(Paragraph(f"Medium Severity Vulnerabilities: {len(medium_vulns)} found", self.styles['CustomHeading2']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def create_trufflehog_section(self, trufflehog_results: Dict[str, Any]) -> List:
        """Create TruffleHog results section."""
        story = []
        
        story.append(Paragraph("Secret Detection (TruffleHog)", self.styles['CustomHeading1']))
        
        results = trufflehog_results.get('results', [])
        summary = trufflehog_results.get('summary', {})
        
        story.append(Paragraph(f"TruffleHog identified {len(results)} potential secrets in the code. This tool searches for credentials such as API keys, tokens, passwords, and other sensitive information that may have been accidentally included in code or repositories.", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Group by confidence
        high_conf = [r for r in results if r.get('confidence') == 'HIGH']
        medium_conf = [r for r in results if r.get('confidence') == 'MEDIUM']
        
        # High confidence secrets
        if high_conf:
            story.append(Paragraph("High Confidence Secrets", self.styles['CustomHeading2']))
            for secret in high_conf:
                story.append(self.create_secret_paragraph(secret, 'HighAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        # Medium confidence secrets
        if medium_conf:
            story.append(Paragraph("Medium Confidence Secrets", self.styles['CustomHeading2']))
            for secret in medium_conf[:10]:
                story.append(self.create_secret_paragraph(secret, 'MediumAlert'))
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def create_recommendations_section(self, scan_results: Dict[str, Any]) -> List:
        """Create recommendations section."""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomHeading1']))
        
        recommendations = self.generate_recommendations(scan_results)
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def create_issue_paragraph(self, issue: Dict, style_name: str) -> Paragraph:
        """Create paragraph for a security issue."""
        text = f"<b>{issue.get('category', 'Unknown')}:</b> {issue.get('message', 'No message')}<br/>"
        text += f"File: {os.path.basename(issue.get('file_path', 'unknown'))} (Line {issue.get('line_number', 0)})<br/>"
        text += f"Rule: {issue.get('rule_id', 'unknown')}"
        
        return Paragraph(text, self.styles[style_name])
    
    def create_vulnerability_paragraph(self, vuln: Dict, style_name: str) -> Paragraph:
        """Create paragraph for a vulnerability."""
        text = f"<b>{vuln.get('vulnerability_id', 'Unknown')}:</b> {vuln.get('package_name', 'unknown')} v{vuln.get('package_version', 'unknown')}<br/>"
        text += f"CVSS Score: {vuln.get('cvss_score', 'N/A')}<br/>"
        text += f"Description: {vuln.get('description', 'No description')[:100]}..."
        
        return Paragraph(text, self.styles[style_name])
    
    def create_secret_paragraph(self, secret: Dict, style_name: str) -> Paragraph:
        """Create paragraph for a secret."""
        text = f"<b>{secret.get('secret_type', 'Unknown')}:</b> {secret.get('masked_secret', 'N/A')}<br/>"
        text += f"File: {os.path.basename(secret.get('file_path', 'unknown'))} (Line {secret.get('line_number', 0)})<br/>"
        text += f"Scanner: {secret.get('scanner', 'Unknown')}"
        
        return Paragraph(text, self.styles[style_name])
    
    def generate_overall_summary(self, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """Generate overall summary statistics."""
        semgrep_summary = scan_results.get('semgrep', {}).get('summary', {})
        grype_summary = scan_results.get('grype', {}).get('summary', {})
        trufflehog_summary = scan_results.get('trufflehog', {}).get('summary', {})
        
        return {
            'total_files': len(scan_results.get('downloaded_files', [])),
            'total_issues': semgrep_summary.get('total_findings', 0),
            'high_severity': semgrep_summary.get('high_severity', 0),
            'medium_severity': semgrep_summary.get('medium_severity', 0),
            'low_severity': semgrep_summary.get('low_severity', 0),
            'total_secrets': trufflehog_summary.get('total_secrets', 0),
            'total_vulnerabilities': grype_summary.get('total_vulnerabilities', 0)
        }
    
    def calculate_risk_level(self, summary: Dict[str, int]) -> str:
        """Calculate overall risk level."""
        high_issues = summary.get('high_severity', 0)
        secrets = summary.get('total_secrets', 0)
        vulnerabilities = summary.get('total_vulnerabilities', 0)
        
        if high_issues > 5 or secrets > 3 or vulnerabilities > 10:
            return "CRITICAL"
        elif high_issues > 2 or secrets > 1 or vulnerabilities > 5:
            return "HIGH"
        elif high_issues > 0 or secrets > 0 or vulnerabilities > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level."""
        colors = {
            "CRITICAL": "#FF0000",
            "HIGH": "#FF6600",
            "MEDIUM": "#FFA500",
            "LOW": "#00AA00"
        }
        return colors.get(risk_level, "#000000")
    
    def generate_recommendations(self, scan_results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        # General recommendations
        recommendations.append("Implement secure code review processes before deploying code.")
        recommendations.append("Use Content Security Policy (CSP) headers to prevent XSS attacks.")
        recommendations.append("Regularly update all dependencies to the latest secure versions.")
        
        # Specific recommendations based on findings
        semgrep_results = scan_results.get('semgrep', {}).get('results', [])
        if semgrep_results:
            recommendations.append("[Semgrep] Fix security issues identified through static code analysis.")
            if any(r.get('category') == 'Cross-Site Scripting (XSS)' for r in semgrep_results):
                recommendations.append("[Semgrep] Implement proper input validation and output encoding to prevent XSS.")
            
            if any(r.get('category') == 'SQL Injection' for r in semgrep_results):
                recommendations.append("[Semgrep] Use parameterized queries and avoid dynamic SQL construction.")
        
        trufflehog_results = scan_results.get('trufflehog', {}).get('results', [])
        if trufflehog_results:
            recommendations.append("[TruffleHog] Remove all hardcoded secrets and use environment variables or secure secret management systems.")
            recommendations.append("[TruffleHog] Implement pre-commit hooks to prevent secrets from being committed to version control.")
            recommendations.append("[TruffleHog] Conduct a comprehensive audit of the repository to ensure no credentials are exposed.")
        
        grype_results = scan_results.get('grype', {}).get('results', [])
        if grype_results:
            recommendations.append("[Grype] Set up automated dependency vulnerability scanning in CI/CD pipeline.")
            recommendations.append("[Grype] Create a process to promptly update vulnerable dependencies.")
            recommendations.append("[Grype] Monitor CVE databases regularly for dependencies in use.")
        
        return recommendations
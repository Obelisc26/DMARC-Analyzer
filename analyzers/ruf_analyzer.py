"""
RUF Analyzer Module - PARTE 3b
Analyzes DMARC forensic/failure (RUF) reports from both XML and HTML formats
RUF reports contain detailed information about individual authentication failures
"""

import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup
import re


class RUFAnalyzer:
    """
    Analyzer for DMARC RUF (forensic/failure) reports
    Supports both XML and HTML formats
    """

    def __init__(self):
        """Initialize the RUF analyzer"""
        self.reports_data = []

    def add_report(self, file_path: str) -> None:
        """
        Add a DMARC RUF report from XML or HTML file

        Args:
            file_path: Path to the report file (XML or HTML)
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            print(f"⚠️  Warning: File not found: {file_path}")
            return

        file_ext = file_path_obj.suffix.lower()

        try:
            if file_ext == '.xml':
                self._process_xml_report(file_path_obj)
            elif file_ext in ['.html', '.htm']:
                self._process_html_report(file_path_obj)
            else:
                print(f"⚠️  Warning: Unsupported file format: {file_ext}")
                return

            print(f"✓ Processed RUF: {file_path_obj.name}")

        except Exception as e:
            print(f"❌ Error processing {file_path_obj.name}: {str(e)}")

    def _process_xml_report(self, xml_path: Path) -> None:
        """Process XML format RUF report"""
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extract forensic report data
        report_data = {
            'Report_ID': self._safe_find(root, './/report_id', 'Unknown'),
            'Feedback_Type': self._safe_find(root, './/feedback_type', 'auth-failure'),
            'User_Agent': self._safe_find(root, './/user_agent', 'Unknown'),
            'Version': self._safe_find(root, './/version', 'Unknown'),
            'Source_IP': self._safe_find(root, './/source_ip', 'Unknown'),
            'Authentication_Results': self._safe_find(root, './/auth_results', ''),
            'Delivery_Result': self._safe_find(root, './/delivery_result', 'Unknown'),
            'Auth_Failure': self._safe_find(root, './/auth_failure', 'Unknown'),
            'Reported_Domain': self._safe_find(root, './/reported_domain', 'Unknown'),
            'Arrival_Date': self._safe_find(root, './/arrival_date', 'Unknown'),
        }

        # Extract original message headers
        report_data.update(self._extract_headers_xml(root))

        # Extract policy information
        report_data['DMARC_Policy'] = self._safe_find(root, './/policy_evaluated', 'Unknown')

        # Determine what failed
        auth_failure = report_data['Auth_Failure'].lower()
        report_data['SPF_Failed'] = 'spf' in auth_failure
        report_data['DKIM_Failed'] = 'dkim' in auth_failure

        # Add timestamp
        report_data['Processed_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.reports_data.append(report_data)

    def _process_html_report(self, html_path: Path) -> None:
        """Process HTML format RUF report"""
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        # Initialize report data
        report_data = {
            'Report_ID': html_path.stem,
            'Feedback_Type': 'auth-failure',
            'User_Agent': 'Unknown',
            'Version': 'Unknown',
            'Source_IP': 'Unknown',
            'Authentication_Results': '',
            'Delivery_Result': 'Unknown',
            'Auth_Failure': 'Unknown',
            'Reported_Domain': 'Unknown',
            'Arrival_Date': 'Unknown',
            'SPF_Failed': False,
            'DKIM_Failed': False,
            'Processed_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Extract source IP
        ip_match = re.search(r'(?:source[_\s]*ip|from[_\s]*ip)[:\s]*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text, re.IGNORECASE)
        if ip_match:
            report_data['Source_IP'] = ip_match.group(1)

        # Extract authentication results
        auth_results_match = re.search(r'authentication[_\s-]*results?[:\s]*([^\n]+)', text, re.IGNORECASE)
        if auth_results_match:
            report_data['Authentication_Results'] = auth_results_match.group(1).strip()

        # Extract reported domain
        domain_match = re.search(r'(?:reported[_\s]*domain|header[_\s]*from)[:\s]*(?:@)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.IGNORECASE)
        if domain_match:
            report_data['Reported_Domain'] = domain_match.group(1)

        # Extract arrival/delivery date
        date_match = re.search(r'(?:arrival|date|received)[:\s]*([^\n]+(?:\d{4}|[A-Z]{3}\s+\d{4}))', text, re.IGNORECASE)
        if date_match:
            report_data['Arrival_Date'] = date_match.group(1).strip()

        # Extract auth failure type
        if 'spf' in text.lower() and ('fail' in text.lower() or 'failed' in text.lower()):
            report_data['SPF_Failed'] = True
            report_data['Auth_Failure'] = 'SPF' if not report_data['Auth_Failure'] else report_data['Auth_Failure'] + ', SPF'

        if 'dkim' in text.lower() and ('fail' in text.lower() or 'failed' in text.lower()):
            report_data['DKIM_Failed'] = True
            if 'Auth_Failure' in report_data and report_data['Auth_Failure'] != 'Unknown':
                report_data['Auth_Failure'] += ', DKIM'
            else:
                report_data['Auth_Failure'] = 'DKIM'

        # Extract message headers
        report_data.update(self._extract_headers_html(soup, text))

        # Extract delivery result
        delivery_match = re.search(r'delivery[_\s-]*result[:\s]*([^\n]+)', text, re.IGNORECASE)
        if delivery_match:
            report_data['Delivery_Result'] = delivery_match.group(1).strip()

        # Extract DMARC policy
        policy_match = re.search(r'dmarc[_\s-]*policy[:\s]*(none|quarantine|reject)', text, re.IGNORECASE)
        if policy_match:
            report_data['DMARC_Policy'] = policy_match.group(1).lower()
        else:
            report_data['DMARC_Policy'] = 'Unknown'

        self.reports_data.append(report_data)

    def _extract_headers_xml(self, root: ET.Element) -> Dict[str, str]:
        """Extract message headers from XML"""
        headers = {
            'From': self._safe_find(root, './/from', 'Unknown'),
            'To': self._safe_find(root, './/to', 'Unknown'),
            'Subject': self._safe_find(root, './/subject', 'Unknown'),
            'Date': self._safe_find(root, './/date', 'Unknown'),
            'Message_ID': self._safe_find(root, './/message_id', 'Unknown'),
        }

        # Try to find in original_message section
        original_msg = root.find('.//original_message')
        if original_msg is not None:
            headers_text = original_msg.text or ''
            if headers_text:
                # Parse headers from text
                from_match = re.search(r'From:\s*([^\n]+)', headers_text, re.IGNORECASE)
                if from_match:
                    headers['From'] = from_match.group(1).strip()

                to_match = re.search(r'To:\s*([^\n]+)', headers_text, re.IGNORECASE)
                if to_match:
                    headers['To'] = to_match.group(1).strip()

                subject_match = re.search(r'Subject:\s*([^\n]+)', headers_text, re.IGNORECASE)
                if subject_match:
                    headers['Subject'] = subject_match.group(1).strip()

        return headers

    def _extract_headers_html(self, soup: BeautifulSoup, text: str) -> Dict[str, str]:
        """Extract message headers from HTML"""
        headers = {
            'From': 'Unknown',
            'To': 'Unknown',
            'Subject': 'Unknown',
            'Date': 'Unknown',
            'Message_ID': 'Unknown',
        }

        # Try to find headers using regex
        from_match = re.search(r'From:\s*([^\n<]+)', text, re.IGNORECASE)
        if from_match:
            headers['From'] = from_match.group(1).strip()

        to_match = re.search(r'To:\s*([^\n<]+)', text, re.IGNORECASE)
        if to_match:
            headers['To'] = to_match.group(1).strip()

        subject_match = re.search(r'Subject:\s*([^\n<]+)', text, re.IGNORECASE)
        if subject_match:
            headers['Subject'] = subject_match.group(1).strip()

        date_match = re.search(r'Date:\s*([^\n<]+)', text, re.IGNORECASE)
        if date_match:
            headers['Date'] = date_match.group(1).strip()

        message_id_match = re.search(r'Message-ID:\s*([^\n<]+)', text, re.IGNORECASE)
        if message_id_match:
            headers['Message_ID'] = message_id_match.group(1).strip()

        return headers

    def _safe_find(self, element: ET.Element, path: str, default: str = '') -> str:
        """Safely find and return element text"""
        if element is None:
            return default

        found = element.find(path)
        if found is not None:
            return found.text if found.text else default
        return default

    def generate_report(self, output_file: str = 'ruf_analysis.xlsx') -> None:
        """
        Generate Excel report with RUF analysis results

        Args:
            output_file: Name of the output Excel file
        """
        if not self.reports_data:
            print("❌ No data to generate report. Add reports first using add_report()")
            return

        # Create DataFrame
        df = pd.DataFrame(self.reports_data)

        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary(writer, df)

            # All forensic reports
            df.to_excel(writer, sheet_name='All Forensic Reports', index=False)

            # SPF failures only
            df_spf = df[df['SPF_Failed'] == True]
            if not df_spf.empty:
                df_spf.to_excel(writer, sheet_name='SPF Failures', index=False)

            # DKIM failures only
            df_dkim = df[df['DKIM_Failed'] == True]
            if not df_dkim.empty:
                df_dkim.to_excel(writer, sheet_name='DKIM Failures', index=False)

            # By source IP
            if not df.empty and 'Source_IP' in df.columns:
                df_ip_stats = df.groupby('Source_IP').size().reset_index(name='Failure_Count')
                df_ip_stats = df_ip_stats.sort_values('Failure_Count', ascending=False)
                df_ip_stats.to_excel(writer, sheet_name='Failures by IP', index=False)

            # By domain
            if not df.empty and 'Reported_Domain' in df.columns:
                df_domain_stats = df.groupby('Reported_Domain').size().reset_index(name='Failure_Count')
                df_domain_stats = df_domain_stats.sort_values('Failure_Count', ascending=False)
                df_domain_stats.to_excel(writer, sheet_name='Failures by Domain', index=False)

        print(f"\n✅ RUF Report generated: {output_file}")
        self._print_summary(df)

    def _write_summary(self, writer, df: pd.DataFrame) -> None:
        """Write summary sheet"""
        spf_failures = df['SPF_Failed'].sum() if 'SPF_Failed' in df.columns else 0
        dkim_failures = df['DKIM_Failed'].sum() if 'DKIM_Failed' in df.columns else 0

        summary_data = {
            'Metric': [
                'Total Forensic Reports',
                'Unique Source IPs',
                'Unique Domains',
                'SPF Failures',
                'DKIM Failures',
                'Both SPF and DKIM Failed',
                'Date Range Start',
                'Date Range End'
            ],
            'Value': [
                len(df),
                df['Source_IP'].nunique() if 'Source_IP' in df.columns else 0,
                df['Reported_Domain'].nunique() if 'Reported_Domain' in df.columns else 0,
                int(spf_failures),
                int(dkim_failures),
                int(df[(df['SPF_Failed'] == True) & (df['DKIM_Failed'] == True)].shape[0]) if 'SPF_Failed' in df.columns else 0,
                df['Arrival_Date'].min() if 'Arrival_Date' in df.columns else 'Unknown',
                df['Arrival_Date'].max() if 'Arrival_Date' in df.columns else 'Unknown'
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

    def _print_summary(self, df: pd.DataFrame) -> None:
        """Print summary to console"""
        spf_failures = df['SPF_Failed'].sum() if 'SPF_Failed' in df.columns else 0
        dkim_failures = df['DKIM_Failed'].sum() if 'DKIM_Failed' in df.columns else 0

        print("\n" + "=" * 50)
        print("RUF ANALYSIS SUMMARY (Forensic Reports)")
        print("=" * 50)
        print(f"Total Forensic Reports: {len(df)}")
        print(f"Unique Source IPs: {df['Source_IP'].nunique() if 'Source_IP' in df.columns else 0}")
        print(f"Unique Domains: {df['Reported_Domain'].nunique() if 'Reported_Domain' in df.columns else 0}")
        print(f"SPF Failures: {int(spf_failures)}")
        print(f"DKIM Failures: {int(dkim_failures)}")
        if 'SPF_Failed' in df.columns:
            both_failed = df[(df['SPF_Failed'] == True) & (df['DKIM_Failed'] == True)].shape[0]
            print(f"Both Failed: {both_failed}")
        print("=" * 50)


if __name__ == "__main__":
    print("RUF Analyzer - PARTE 3b")
    print("Usage: from analyzers import RUFAnalyzer")

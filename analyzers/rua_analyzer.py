"""
RUA Analyzer Module - PARTE 3a
Analyzes DMARC aggregate (RUA) reports from both XML and HTML formats
Enhanced version of the original dmarc_analyzer.py with HTML support
"""

import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup
import re


class RUAAnalyzer:
    """
    Analyzer for DMARC RUA (aggregate) reports
    Supports both XML and HTML formats
    """

    def __init__(self):
        """Initialize the RUA analyzer"""
        self.reports_data = []
        self.failed_records = []

    def add_report(self, file_path: str) -> None:
        """
        Add a DMARC RUA report from XML or HTML file

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

            print(f"✓ Processed RUA: {file_path_obj.name}")

        except Exception as e:
            print(f"❌ Error processing {file_path_obj.name}: {str(e)}")

    def _process_xml_report(self, xml_path: Path) -> None:
        """Process XML format RUA report (original format)"""
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Extract report metadata
        metadata = self._extract_metadata_xml(root)

        # Extract policy information
        policy = self._extract_policy_xml(root)

        # Process records
        for record in root.findall('.//record'):
            record_data = self._process_record_xml(record, metadata, policy)
            self.reports_data.append(record_data)

            # Track failed authentications
            if not record_data['SPF_Pass'] or not record_data['DKIM_Pass']:
                self.failed_records.append(record_data)

    def _extract_metadata_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Extract report metadata from XML"""
        metadata = root.find('.//report_metadata')
        if metadata is None:
            return {}

        return {
            'org_name': self._safe_find_xml(metadata, 'org_name'),
            'email': self._safe_find_xml(metadata, 'email'),
            'report_id': self._safe_find_xml(metadata, 'report_id'),
            'date_begin': self._safe_find_xml(metadata, 'date_range/begin'),
            'date_end': self._safe_find_xml(metadata, 'date_range/end')
        }

    def _extract_policy_xml(self, root: ET.Element) -> Dict[str, str]:
        """Extract policy information from XML"""
        policy = root.find('.//policy_published')
        if policy is None:
            return {}

        return {
            'domain': self._safe_find_xml(policy, 'domain'),
            'adkim': self._safe_find_xml(policy, 'adkim', 'r'),
            'aspf': self._safe_find_xml(policy, 'aspf', 'r'),
            'p': self._safe_find_xml(policy, 'p', 'none'),
            'sp': self._safe_find_xml(policy, 'sp', 'none'),
            'pct': self._safe_find_xml(policy, 'pct', '100')
        }

    def _process_record_xml(self, record: ET.Element, metadata: Dict, policy: Dict) -> Dict[str, Any]:
        """Process a single DMARC record from XML"""
        row = record.find('.//row')
        identifiers = record.find('.//identifiers')
        auth_results = record.find('.//auth_results')

        # Source IP information
        source_ip = self._safe_find_xml(row, 'source_ip')
        count = int(self._safe_find_xml(row, 'count', '0'))

        # Policy evaluation
        policy_evaluated = row.find('.//policy_evaluated')
        disposition = self._safe_find_xml(policy_evaluated, 'disposition', 'none')
        dkim_result = self._safe_find_xml(policy_evaluated, 'dkim', 'fail')
        spf_result = self._safe_find_xml(policy_evaluated, 'spf', 'fail')

        # Identifiers
        header_from = self._safe_find_xml(identifiers, 'header_from')
        envelope_from = self._safe_find_xml(identifiers, 'envelope_from')

        # Authentication results
        dkim_pass = self._check_dkim_xml(auth_results)
        spf_pass = self._check_spf_xml(auth_results)

        return {
            'Report_ID': metadata.get('report_id', 'Unknown'),
            'Provider': metadata.get('org_name', 'Unknown'),
            'Date_Begin': self._format_timestamp(metadata.get('date_begin')),
            'Date_End': self._format_timestamp(metadata.get('date_end')),
            'Domain': policy.get('domain', 'Unknown'),
            'Source_IP': source_ip,
            'Count': count,
            'Disposition': disposition,
            'DKIM_Result': dkim_result,
            'SPF_Result': spf_result,
            'DKIM_Pass': dkim_pass,
            'SPF_Pass': spf_pass,
            'Header_From': header_from,
            'Envelope_From': envelope_from,
            'Policy_P': policy.get('p', 'none'),
            'Policy_SP': policy.get('sp', 'none')
        }

    def _process_html_report(self, html_path: Path) -> None:
        """Process HTML format RUA report"""
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Extract metadata from HTML
        metadata = self._extract_metadata_html(soup)

        # Extract policy from HTML
        policy = self._extract_policy_html(soup)

        # Find and process data tables
        tables = soup.find_all('table')

        for table in tables:
            # Try to identify if this table contains record data
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]

            # Check if this looks like a records table
            if any(keyword in ' '.join(headers) for keyword in ['ip', 'source', 'count', 'dkim', 'spf']):
                self._process_html_table(table, headers, metadata, policy)

    def _extract_metadata_html(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract report metadata from HTML"""
        metadata = {
            'org_name': 'Unknown',
            'email': 'Unknown',
            'report_id': 'Unknown',
            'date_begin': '',
            'date_end': ''
        }

        # Try to find metadata in common patterns
        text = soup.get_text()

        # Look for report ID
        report_id_match = re.search(r'report[_\s]*id[:\s]*([^\s\n<]+)', text, re.IGNORECASE)
        if report_id_match:
            metadata['report_id'] = report_id_match.group(1)

        # Look for organization name
        org_match = re.search(r'organization[:\s]*([^\n<]+)', text, re.IGNORECASE)
        if org_match:
            metadata['org_name'] = org_match.group(1).strip()

        # Look for email
        email_match = re.search(r'email[:\s]*([^\s\n<]+@[^\s\n<]+)', text, re.IGNORECASE)
        if email_match:
            metadata['email'] = email_match.group(1)

        # Look for date range
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})[^\d]+(\d{4}-\d{2}-\d{2})', text)
        if date_match:
            metadata['date_begin'] = date_match.group(1)
            metadata['date_end'] = date_match.group(2)

        return metadata

    def _extract_policy_html(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract policy information from HTML"""
        policy = {
            'domain': 'Unknown',
            'adkim': 'r',
            'aspf': 'r',
            'p': 'none',
            'sp': 'none',
            'pct': '100'
        }

        text = soup.get_text()

        # Look for domain
        domain_match = re.search(r'domain[:\s]*([^\s\n<]+\.[^\s\n<]+)', text, re.IGNORECASE)
        if domain_match:
            policy['domain'] = domain_match.group(1).strip()

        # Look for policy
        policy_match = re.search(r'policy[:\s]*(none|quarantine|reject)', text, re.IGNORECASE)
        if policy_match:
            policy['p'] = policy_match.group(1).lower()

        return policy

    def _process_html_table(self, table, headers: List[str], metadata: Dict, policy: Dict) -> None:
        """Process an HTML table containing record data"""
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # Need at least a few cells
                continue

            # Extract cell values
            cell_values = [cell.get_text(strip=True) for cell in cells]

            # Try to map values to fields
            record_data = self._parse_html_row(headers, cell_values, metadata, policy)

            if record_data:
                self.reports_data.append(record_data)

                # Track failed authentications
                if not record_data['SPF_Pass'] or not record_data['DKIM_Pass']:
                    self.failed_records.append(record_data)

    def _parse_html_row(self, headers: List[str], values: List[str], metadata: Dict, policy: Dict) -> Dict[str, Any]:
        """Parse a single HTML table row into a record"""
        record = {
            'Report_ID': metadata.get('report_id', 'Unknown'),
            'Provider': metadata.get('org_name', 'Unknown'),
            'Date_Begin': metadata.get('date_begin', 'Unknown'),
            'Date_End': metadata.get('date_end', 'Unknown'),
            'Domain': policy.get('domain', 'Unknown'),
            'Source_IP': 'Unknown',
            'Count': 0,
            'Disposition': 'none',
            'DKIM_Result': 'unknown',
            'SPF_Result': 'unknown',
            'DKIM_Pass': False,
            'SPF_Pass': False,
            'Header_From': 'Unknown',
            'Envelope_From': 'Unknown',
            'Policy_P': policy.get('p', 'none'),
            'Policy_SP': policy.get('sp', 'none')
        }

        # Map headers to values
        for i, header in enumerate(headers):
            if i >= len(values):
                break

            value = values[i]
            header_lower = header.lower()

            if 'ip' in header_lower or 'source' in header_lower:
                record['Source_IP'] = value
            elif 'count' in header_lower or 'messages' in header_lower:
                try:
                    record['Count'] = int(value.replace(',', ''))
                except:
                    record['Count'] = 0
            elif 'dkim' in header_lower:
                record['DKIM_Result'] = value.lower()
                record['DKIM_Pass'] = 'pass' in value.lower()
            elif 'spf' in header_lower:
                record['SPF_Result'] = value.lower()
                record['SPF_Pass'] = 'pass' in value.lower()
            elif 'disposition' in header_lower or 'action' in header_lower:
                record['Disposition'] = value.lower()
            elif 'from' in header_lower:
                if 'header' in header_lower:
                    record['Header_From'] = value
                elif 'envelope' in header_lower:
                    record['Envelope_From'] = value
                else:
                    record['Header_From'] = value

        return record

    def _check_dkim_xml(self, auth_results: ET.Element) -> bool:
        """Check if DKIM authentication passed in XML"""
        if auth_results is None:
            return False

        for dkim in auth_results.findall('.//dkim'):
            result = self._safe_find_xml(dkim, 'result')
            if result == 'pass':
                return True
        return False

    def _check_spf_xml(self, auth_results: ET.Element) -> bool:
        """Check if SPF authentication passed in XML"""
        if auth_results is None:
            return False

        spf = auth_results.find('.//spf')
        if spf is not None:
            result = self._safe_find_xml(spf, 'result')
            return result == 'pass'
        return False

    def _safe_find_xml(self, element: ET.Element, path: str, default: str = '') -> str:
        """Safely find and return element text from XML"""
        if element is None:
            return default

        found = element.find(path)
        return found.text if found is not None and found.text else default

    def _format_timestamp(self, timestamp: str) -> str:
        """Format Unix timestamp to readable date"""
        if not timestamp:
            return 'Unknown'
        try:
            # Try as Unix timestamp
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        except:
            # Already formatted or invalid
            return timestamp

    def generate_report(self, output_file: str = 'rua_analysis.xlsx') -> None:
        """
        Generate Excel report with RUA analysis results

        Args:
            output_file: Name of the output Excel file
        """
        if not self.reports_data:
            print("❌ No data to generate report. Add reports first using add_report()")
            return

        # Create DataFrames
        df_all = pd.DataFrame(self.reports_data)
        df_failed = pd.DataFrame(self.failed_records)

        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary(writer, df_all, df_failed)

            # All records
            df_all.to_excel(writer, sheet_name='All Records', index=False)

            # Failed authentications
            if not df_failed.empty:
                df_failed.to_excel(writer, sheet_name='Failed Auth', index=False)

                # SPF failures
                df_spf_fail = df_failed[~df_failed['SPF_Pass']]
                if not df_spf_fail.empty:
                    df_spf_fail.to_excel(writer, sheet_name='SPF Failures', index=False)

                # DKIM failures
                df_dkim_fail = df_failed[~df_failed['DKIM_Pass']]
                if not df_dkim_fail.empty:
                    df_dkim_fail.to_excel(writer, sheet_name='DKIM Failures', index=False)

            # Statistics by source IP
            if not df_all.empty:
                df_stats = df_all.groupby('Source_IP').agg({
                    'Count': 'sum',
                    'DKIM_Pass': lambda x: sum(x),
                    'SPF_Pass': lambda x: sum(x)
                }).reset_index()
                df_stats.columns = ['Source_IP', 'Total_Messages', 'DKIM_Pass_Count', 'SPF_Pass_Count']
                df_stats.to_excel(writer, sheet_name='IP Statistics', index=False)

        print(f"\n✅ RUA Report generated: {output_file}")
        self._print_summary(df_all, df_failed)

    def _write_summary(self, writer, df_all: pd.DataFrame, df_failed: pd.DataFrame) -> None:
        """Write summary sheet"""
        summary_data = {
            'Metric': [
                'Total Reports Processed',
                'Total Message Count',
                'Unique Source IPs',
                'Providers',
                'Failed Authentications',
                'SPF Failures',
                'DKIM Failures',
                'Pass Rate (%)'
            ],
            'Value': [
                df_all['Report_ID'].nunique(),
                df_all['Count'].sum(),
                df_all['Source_IP'].nunique(),
                df_all['Provider'].nunique(),
                len(df_failed),
                len(df_failed[~df_failed['SPF_Pass']]) if not df_failed.empty else 0,
                len(df_failed[~df_failed['DKIM_Pass']]) if not df_failed.empty else 0,
                round((1 - len(df_failed) / len(df_all)) * 100, 2) if len(df_all) > 0 else 0
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

    def _print_summary(self, df_all: pd.DataFrame, df_failed: pd.DataFrame) -> None:
        """Print summary to console"""
        print("\n" + "=" * 50)
        print("RUA ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Total Reports: {df_all['Report_ID'].nunique()}")
        print(f"Total Messages: {df_all['Count'].sum():,}")
        print(f"Unique IPs: {df_all['Source_IP'].nunique()}")
        print(f"Failed Auth: {len(df_failed)}")
        if len(df_all) > 0:
            print(f"Pass Rate: {round((1 - len(df_failed) / len(df_all)) * 100, 2)}%")
        print("=" * 50)


if __name__ == "__main__":
    print("RUA Analyzer - PARTE 3a")
    print("Usage: from analyzers import RUAAnalyzer")

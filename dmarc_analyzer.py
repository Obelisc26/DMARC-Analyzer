"""
DMARC Report Analyzer
A tool to analyze DMARC aggregate reports from multiple email providers
"""

import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import os


class DMARCAnalyzer:
    """
    Main class for analyzing DMARC aggregate reports
    """
    
    def __init__(self):
        """Initialize the DMARC analyzer"""
        self.reports_data = []
        self.failed_records = []
        
    def add_report(self, xml_file: str) -> None:
        """
        Add a DMARC report from an XML file
        
        Args:
            xml_file: Path to the XML report file
        """
        if not os.path.exists(xml_file):
            print(f"Warning: File not found: {xml_file}")
            return
            
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Extract report metadata
            metadata = self._extract_metadata(root)
            
            # Extract policy information
            policy = self._extract_policy(root)
            
            # Process records
            for record in root.findall('.//record'):
                record_data = self._process_record(record, metadata, policy)
                self.reports_data.append(record_data)
                
                # Track failed authentications
                if not record_data['SPF_Pass'] or not record_data['DKIM_Pass']:
                    self.failed_records.append(record_data)
                    
            print(f"✓ Processed: {xml_file}")
            
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")
    
    def _extract_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """Extract report metadata"""
        metadata = root.find('.//report_metadata')
        if metadata is None:
            return {}
            
        return {
            'org_name': self._safe_find(metadata, 'org_name'),
            'email': self._safe_find(metadata, 'email'),
            'report_id': self._safe_find(metadata, 'report_id'),
            'date_begin': self._safe_find(metadata, 'date_range/begin'),
            'date_end': self._safe_find(metadata, 'date_range/end')
        }
    
    def _extract_policy(self, root: ET.Element) -> Dict[str, str]:
        """Extract policy information"""
        policy = root.find('.//policy_published')
        if policy is None:
            return {}
            
        return {
            'domain': self._safe_find(policy, 'domain'),
            'adkim': self._safe_find(policy, 'adkim', 'r'),
            'aspf': self._safe_find(policy, 'aspf', 'r'),
            'p': self._safe_find(policy, 'p', 'none'),
            'sp': self._safe_find(policy, 'sp', 'none'),
            'pct': self._safe_find(policy, 'pct', '100')
        }
    
    def _process_record(self, record: ET.Element, metadata: Dict, policy: Dict) -> Dict[str, Any]:
        """Process a single DMARC record"""
        row = record.find('.//row')
        identifiers = record.find('.//identifiers')
        auth_results = record.find('.//auth_results')
        
        # Source IP information
        source_ip = self._safe_find(row, 'source_ip')
        count = int(self._safe_find(row, 'count', '0'))
        
        # Policy evaluation
        policy_evaluated = row.find('.//policy_evaluated')
        disposition = self._safe_find(policy_evaluated, 'disposition', 'none')
        dkim_result = self._safe_find(policy_evaluated, 'dkim', 'fail')
        spf_result = self._safe_find(policy_evaluated, 'spf', 'fail')
        
        # Identifiers
        header_from = self._safe_find(identifiers, 'header_from')
        envelope_from = self._safe_find(identifiers, 'envelope_from')
        
        # Authentication results
        dkim_pass = self._check_dkim(auth_results)
        spf_pass = self._check_spf(auth_results)
        
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
    
    def _check_dkim(self, auth_results: ET.Element) -> bool:
        """Check if DKIM authentication passed"""
        if auth_results is None:
            return False
            
        for dkim in auth_results.findall('.//dkim'):
            result = self._safe_find(dkim, 'result')
            if result == 'pass':
                return True
        return False
    
    def _check_spf(self, auth_results: ET.Element) -> bool:
        """Check if SPF authentication passed"""
        if auth_results is None:
            return False
            
        spf = auth_results.find('.//spf')
        if spf is not None:
            result = self._safe_find(spf, 'result')
            return result == 'pass'
        return False
    
    def _safe_find(self, element: ET.Element, path: str, default: str = '') -> str:
        """Safely find and return element text"""
        if element is None:
            return default
            
        found = element.find(path)
        return found.text if found is not None and found.text else default
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format Unix timestamp to readable date"""
        if not timestamp:
            return 'Unknown'
        try:
            return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    
    def generate_report(self, output_file: str = 'dmarc_analysis.xlsx') -> None:
        """
        Generate Excel report with analysis results
        
        Args:
            output_file: Name of the output Excel file
        """
        if not self.reports_data:
            print("No data to generate report. Add reports first using add_report()")
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
        
        print(f"\n✓ Report generated: {output_file}")
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
                len(df_failed[~df_failed['SPF_Pass']]),
                len(df_failed[~df_failed['DKIM_Pass']]),
                round((1 - len(df_failed) / len(df_all)) * 100, 2) if len(df_all) > 0 else 0
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    def _print_summary(self, df_all: pd.DataFrame, df_failed: pd.DataFrame) -> None:
        """Print summary to console"""
        print("\n" + "="*50)
        print("DMARC ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total Reports: {df_all['Report_ID'].nunique()}")
        print(f"Total Messages: {df_all['Count'].sum():,}")
        print(f"Unique IPs: {df_all['Source_IP'].nunique()}")
        print(f"Failed Auth: {len(df_failed)}")
        print(f"Pass Rate: {round((1 - len(df_failed) / len(df_all)) * 100, 2)}%")
        print("="*50)


if __name__ == "__main__":
    print("DMARC Analyzer - Import this module to use")
    print("Example: from dmarc_analyzer import DMARCAnalyzer")

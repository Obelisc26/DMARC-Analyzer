"""
Example: Analyze DMARC reports from multiple email providers
"""

from dmarc_analyzer import DMARCAnalyzer
import os

def main():
    """
    Example of analyzing DMARC reports from multiple providers
    (Microsoft 365, Google Workspace, and others)
    """
    print("=" * 60)
    print("DMARC Analysis - Multi-Provider Reports")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DMARCAnalyzer()
    
    # Path to reports directory
    reports_dir = '../reports'
    
    # Add all XML files from reports directory
    # The analyzer automatically detects the provider from each report
    if os.path.exists(reports_dir):
        xml_files = [f for f in os.listdir(reports_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print("\nNo XML files found in reports directory.")
            print("Place your DMARC reports (XML format) from any provider in the 'reports' folder.")
            print("\nSupported providers:")
            print("  - Microsoft 365")
            print("  - Google Workspace")
            print("  - Any provider that sends standard DMARC aggregate reports")
            return
        
        print(f"\nFound {len(xml_files)} XML report(s)")
        print("\nProcessing reports from all providers...")
        
        for xml_file in xml_files:
            file_path = os.path.join(reports_dir, xml_file)
            analyzer.add_report(file_path)
    else:
        print(f"\nReports directory not found: {reports_dir}")
        print("Please create the directory and add your XML reports.")
        return
    
    # Generate comprehensive Excel report
    output_file = 'multi_provider_dmarc_analysis.xlsx'
    analyzer.generate_report(output_file)
    
    print(f"\n✓ Analysis complete! Check: {output_file}")
    print("\nThe report includes data from all providers combined.")


if __name__ == "__main__":
    main()

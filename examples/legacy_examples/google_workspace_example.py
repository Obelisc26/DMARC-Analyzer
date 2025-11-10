"""
Example: Analyze DMARC reports from Google Workspace
"""

from dmarc_analyzer import DMARCAnalyzer
import os

def main():
    """
    Example of analyzing DMARC reports from Google Workspace only
    """
    print("=" * 60)
    print("DMARC Analysis - Google Workspace Reports")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DMARCAnalyzer()
    
    # Path to reports directory
    reports_dir = '../reports'
    
    # Add all XML files from reports directory
    # In this example, we assume all reports are from Google Workspace
    if os.path.exists(reports_dir):
        xml_files = [f for f in os.listdir(reports_dir) if f.endswith('.xml')]
        
        if not xml_files:
            print("\nNo XML files found in reports directory.")
            print("Place your Google Workspace DMARC reports (XML format) in the 'reports' folder.")
            return
        
        print(f"\nFound {len(xml_files)} XML report(s)")
        print("\nProcessing reports...")
        
        for xml_file in xml_files:
            file_path = os.path.join(reports_dir, xml_file)
            analyzer.add_report(file_path)
    else:
        print(f"\nReports directory not found: {reports_dir}")
        print("Please create the directory and add your XML reports.")
        return
    
    # Generate Excel report
    output_file = 'google_workspace_dmarc_analysis.xlsx'
    analyzer.generate_report(output_file)
    
    print(f"\n✓ Analysis complete! Check: {output_file}")


if __name__ == "__main__":
    main()

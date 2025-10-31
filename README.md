# DMARC Report Analyzer

A Python tool to analyze DMARC (Domain-based Message Authentication, Reporting & Conformance) aggregate reports from multiple email providers.

## 🎯 Features

- **Multi-Provider Support**: Works with Microsoft 365, Google Workspace, and other email providers
- **XML Report Parsing**: Automatically processes DMARC aggregate reports in XML format
- **Detailed Analysis**: Identifies SPF and DKIM authentication failures
- **Multiple Report Types**: Supports both single provider and multi-provider analysis
- **Excel Export**: Generates comprehensive reports in Excel format

## 📋 Requirements

- Python 3.7+
- Required libraries:
  - pandas
  - openpyxl
  - xml.etree.ElementTree (built-in)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/Obelisc26/An-lisis-Informes-SPF.git
cd An-lisis-Informes-SPF

# Install dependencies
pip install pandas openpyxl
```

## 📁 Project Structure

```
dmarc-analyzer/
├── README.md
├── requirements.txt
├── dmarc_analyzer.py           # Main analyzer class
├── examples/
│   ├── microsoft365_example.py # Single provider (Microsoft 365)
│   ├── google_workspace_example.py # Single provider (Google Workspace)
│   └── multi_provider_example.py   # Multiple providers
└── reports/                    # Place your XML reports here
    └── .gitkeep
```

## 💡 Usage

### Example 1: Analyze Microsoft 365 Reports

```python
from dmarc_analyzer import DMARCAnalyzer

# Initialize analyzer
analyzer = DMARCAnalyzer()

# Add XML reports
analyzer.add_report('reports/microsoft365_report1.xml')
analyzer.add_report('reports/microsoft365_report2.xml')

# Generate Excel report
analyzer.generate_report('microsoft365_dmarc_analysis.xlsx')
```

### Example 2: Analyze Google Workspace Reports

```python
from dmarc_analyzer import DMARCAnalyzer

analyzer = DMARCAnalyzer()
analyzer.add_report('reports/google_workspace_report1.xml')
analyzer.add_report('reports/google_workspace_report2.xml')
analyzer.generate_report('google_workspace_dmarc_analysis.xlsx')
```

### Example 3: Multi-Provider Analysis

```python
from dmarc_analyzer import DMARCAnalyzer

analyzer = DMARCAnalyzer()

# Add reports from different providers
analyzer.add_report('reports/microsoft365_report.xml')
analyzer.add_report('reports/google_workspace_report.xml')
analyzer.add_report('reports/other_provider_report.xml')

# Generate combined analysis
analyzer.generate_report('multi_provider_dmarc_analysis.xlsx')
```

## 📊 Report Output

The generated Excel file contains:

1. **Summary Sheet**: Overview of all analyzed reports
2. **Failed Messages**: Detailed list of authentication failures
3. **SPF Failures**: Messages that failed SPF checks
4. **DKIM Failures**: Messages that failed DKIM checks
5. **Statistics**: Aggregated data by source IP and sender

## 🔍 Understanding DMARC Reports

DMARC reports contain information about:
- **SPF (Sender Policy Framework)**: Validates the sending server
- **DKIM (DomainKeys Identified Mail)**: Validates email integrity
- **DMARC Policy**: How to handle authentication failures

## 📝 DMARC Report Format

The tool expects XML reports in standard DMARC aggregate format:

```xml
<?xml version="1.0"?>
<feedback>
  <report_metadata>...</report_metadata>
  <policy_published>...</policy_published>
  <record>...</record>
</feedback>
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for analyzing DMARC reports only. Always ensure you have permission to analyze email authentication data.

## 🐛 Troubleshooting

### Common Issues

1. **XML Parsing Errors**: Ensure your XML files are valid DMARC aggregate reports
2. **Missing Data**: Some providers may omit certain fields - the tool handles this gracefully
3. **Large Files**: For very large reports, consider processing them in batches

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🔗 Resources

- [DMARC.org](https://dmarc.org/)
- [RFC 7489 - DMARC Specification](https://tools.ietf.org/html/rfc7489)
- [Understanding DMARC Reports](https://dmarc.org/resources/data-sources/)

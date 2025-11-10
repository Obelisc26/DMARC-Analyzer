# DMARC Report Analyzer

A comprehensive Python tool to analyze DMARC (Domain-based Message Authentication, Reporting & Conformance) reports, supporting both **RUA (aggregate reports)** and **RUF (forensic/failure reports)** from multiple email providers.

## 🎯 Features

### Complete 3-Part Pipeline

1. **🔧 PARTE 1: File Extraction**
   - Extracts HTML/XML files from various compressed formats (ZIP, GZ, TAR)
   - Processes EML files with nested attachments
   - Handles complex nested structures (ZIP within EML, etc.)
   - Automatically detects file types

2. **🔧 PARTE 2: Report Classification**
   - Intelligently classifies reports as RUA or RUF
   - Analyzes both XML and HTML content
   - Uses keyword matching and heuristics
   - Organizes reports into separate directories

3. **🔧 PARTE 3: Analysis & Reporting**
   - **RUA Analysis**: Aggregate reports with IP statistics and authentication metrics
   - **RUF Analysis**: Forensic reports with detailed failure information
   - Generates comprehensive Excel reports with multiple sheets
   - Provides summary statistics and visualizations

### Additional Features

- **Multi-Format Support**: XML and HTML report formats
- **Multi-Provider Support**: Microsoft 365, Google Workspace, and all DMARC-compliant providers
- **Flexible Execution**: Run complete pipeline or individual steps
- **Command-Line Interface**: Easy-to-use CLI with multiple modes
- **Excel Export**: Professional multi-sheet reports with statistics

## 📋 Requirements

- Python 3.7+
- Required libraries:
  - pandas
  - openpyxl
  - beautifulsoup4
  - Built-in: xml.etree.ElementTree, zipfile, gzip, tarfile, email

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/Obelisc26/DMARC-Analyzer.git
cd DMARC-Analyzer

# Install dependencies
pip install -r requirements.txt
```

## 📁 Project Structure

```
DMARC-Analyzer/
├── main.py                      # Main script - integrates all 3 parts
├── dmarc_analyzer.py            # Legacy analyzer (for backward compatibility)
├── requirements.txt
├── README.md
│
├── extractors/                  # PARTE 1: File extraction
│   ├── __init__.py
│   └── file_extractor.py
│
├── classifiers/                 # PARTE 2: Report classification
│   ├── __init__.py
│   └── report_classifier.py
│
├── analyzers/                   # PARTE 3: Analysis
│   ├── __init__.py
│   ├── rua_analyzer.py         # RUA (aggregate) reports
│   └── ruf_analyzer.py         # RUF (forensic) reports
│
├── examples/                    # Usage examples
│   ├── complete_pipeline_example.py
│   ├── step_by_step_example.py
│   └── legacy_examples/
│
└── reports/
    ├── raw/                    # Place your files here (ZIP, EML, GZ, etc.)
    ├── extracted/              # Extracted HTML/XML files
    ├── rua/                    # Classified RUA reports
    └── ruf/                    # Classified RUF reports
```

## 💡 Usage

### Quick Start: Complete Pipeline

The easiest way to analyze DMARC reports:

```bash
# Place your files (ZIP, EML, GZ, etc.) in reports/raw/
# Then run:
python main.py --input reports/raw
```

This will:
1. Extract all HTML/XML files from compressed archives
2. Classify reports as RUA or RUF
3. Analyze both types and generate Excel reports

**Output:**
- `rua_analysis.xlsx` - Aggregate report analysis
- `ruf_analysis.xlsx` - Forensic report analysis

### Advanced Usage

#### Run Individual Steps

```bash
# PARTE 1: Extract files only
python main.py --extract --input reports/raw

# PARTE 2: Classify files only (after extraction)
python main.py --classify --input reports/extracted

# PARTE 3: Analyze RUA reports only
python main.py --analyze rua --input reports/rua --output my_rua.xlsx

# PARTE 3: Analyze RUF reports only
python main.py --analyze ruf --input reports/ruf --output my_ruf.xlsx
```

#### Custom Output Files

```bash
python main.py --input reports/raw \
  --output-rua custom_rua_report.xlsx \
  --output-ruf custom_ruf_report.xlsx
```

#### Skip Extraction (if files already extracted)

```bash
python main.py --input reports/extracted --skip-extraction
```

### Python API Usage

#### Complete Pipeline

```python
from extractors import FileExtractor
from classifiers import ReportClassifier
from analyzers import RUAAnalyzer, RUFAnalyzer

# PARTE 1: Extract files
extractor = FileExtractor(output_dir='reports/extracted')
extracted_files = extractor.extract_all('reports/raw')

# PARTE 2: Classify reports
classifier = ReportClassifier(rua_dir='reports/rua', ruf_dir='reports/ruf')
classified = classifier.classify_all('reports/extracted')

# PARTE 3a: Analyze RUA reports
rua_analyzer = RUAAnalyzer()
for rua_file in classified['rua']:
    rua_analyzer.add_report(rua_file)
rua_analyzer.generate_report('rua_analysis.xlsx')

# PARTE 3b: Analyze RUF reports
ruf_analyzer = RUFAnalyzer()
for ruf_file in classified['ruf']:
    ruf_analyzer.add_report(ruf_file)
ruf_analyzer.generate_report('ruf_analysis.xlsx')
```

#### Individual Components

```python
# Use only the extractor
from extractors import FileExtractor

extractor = FileExtractor(output_dir='output')
files = extractor.extract_all('input_directory')
stats = extractor.get_statistics()

# Use only the classifier
from classifiers import ReportClassifier

classifier = ReportClassifier()
results = classifier.classify_all('reports/extracted')

# Use only RUA analyzer
from analyzers import RUAAnalyzer

analyzer = RUAAnalyzer()
analyzer.add_report('report1.xml')
analyzer.add_report('report2.html')
analyzer.generate_report('output.xlsx')
```

## 📊 Report Output

### RUA Analysis (Aggregate Reports)

The Excel file contains:

1. **Summary Sheet**: Overview statistics
   - Total reports processed
   - Total message count
   - Unique source IPs
   - Failed authentications
   - Pass rate percentage

2. **All Records**: Complete dataset of all records
3. **Failed Auth**: Records where SPF or DKIM failed
4. **SPF Failures**: Specific SPF failures
5. **DKIM Failures**: Specific DKIM failures
6. **IP Statistics**: Aggregated data by source IP

### RUF Analysis (Forensic Reports)

The Excel file contains:

1. **Summary Sheet**: Overview statistics
   - Total forensic reports
   - Unique source IPs
   - Unique domains
   - SPF/DKIM failure counts

2. **All Forensic Reports**: Complete dataset with:
   - Source IP
   - Authentication results
   - Original message headers (From, To, Subject)
   - Delivery results
   - Failure types

3. **SPF Failures**: Reports where SPF failed
4. **DKIM Failures**: Reports where DKIM failed
5. **Failures by IP**: Aggregated by source IP
6. **Failures by Domain**: Aggregated by domain

## 🔍 Understanding DMARC Reports

### RUA (Aggregate Reports)
- **Purpose**: Statistical overview of email authentication results
- **Content**: Aggregated data from multiple messages
- **Frequency**: Typically sent daily
- **Contains**: IP addresses, message counts, SPF/DKIM results

### RUF (Forensic/Failure Reports)
- **Purpose**: Detailed information about individual authentication failures
- **Content**: Complete message headers and authentication details
- **Frequency**: Sent per failure (real-time)
- **Contains**: Original message headers, specific failure reasons

### Authentication Methods

- **SPF (Sender Policy Framework)**: Validates the sending server's IP
- **DKIM (DomainKeys Identified Mail)**: Validates email integrity via cryptographic signature
- **DMARC Policy**: Defines how to handle authentication failures (none, quarantine, reject)

## 🎯 Use Cases

### 1. Email Deliverability Analysis
Identify why emails are failing authentication and fix configuration issues.

### 2. Security Monitoring
Detect unauthorized use of your domain (spoofing, phishing attempts).

### 3. Compliance Reporting
Generate reports for security audits and compliance requirements.

### 4. Multi-Domain Management
Analyze reports from multiple domains and email providers in one place.

## 🐛 Troubleshooting

### Common Issues

1. **No files extracted**
   - Verify files are in the correct input directory
   - Check file formats are supported (ZIP, GZ, EML, HTML, XML)
   - Ensure files are not corrupted

2. **Files not classified**
   - Check if HTML/XML files contain DMARC report data
   - Verify files have proper structure
   - Some files may be marked as "unclassified" if they don't match RUA or RUF patterns

3. **Analysis errors**
   - Ensure files are properly classified before analysis
   - Check for malformed HTML or XML
   - Verify report format matches DMARC standards

4. **Import errors**
   - Run: `pip install -r requirements.txt`
   - Ensure Python 3.7+ is installed

## 📚 Examples

See the `examples/` directory for:
- `complete_pipeline_example.py` - Full pipeline usage
- `step_by_step_example.py` - Individual step execution
- Legacy examples for backward compatibility

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for analyzing DMARC reports only. Always ensure you have permission to analyze email authentication data and handle email headers responsibly.

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🔗 Resources

- [DMARC.org](https://dmarc.org/)
- [RFC 7489 - DMARC Specification](https://tools.ietf.org/html/rfc7489)
- [RFC 7960 - DMARC Feedback Reports](https://tools.ietf.org/html/rfc7960)
- [Understanding DMARC Reports](https://dmarc.org/resources/data-sources/)

## 🆕 What's New

### Version 2.0
- ✅ Complete support for both RUA and RUF reports
- ✅ Automatic file extraction from multiple formats
- ✅ Intelligent report classification
- ✅ HTML report support in addition to XML
- ✅ Modular architecture with 3 distinct parts
- ✅ Command-line interface for easy usage
- ✅ Backward compatibility with legacy analyzer

## 🚀 Roadmap

- [ ] Web interface for report upload and analysis
- [ ] Real-time monitoring dashboard
- [ ] Email alerts for critical failures
- [ ] Integration with popular email platforms
- [ ] Machine learning for threat detection

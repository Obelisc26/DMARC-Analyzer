"""
Report Classifier Module - PARTE 2
Classifies extracted files into RUA (aggregate reports) and RUF (forensic/failure reports)
"""

import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
from bs4 import BeautifulSoup


class ReportClassifier:
    """
    Classifier for DMARC reports
    Separates RUA (aggregate) and RUF (forensic/failure) reports
    """

    def __init__(self, rua_dir: str = 'reports/rua', ruf_dir: str = 'reports/ruf'):
        """
        Initialize the report classifier

        Args:
            rua_dir: Directory for RUA (aggregate) reports
            ruf_dir: Directory for RUF (forensic) reports
        """
        self.rua_dir = Path(rua_dir)
        self.ruf_dir = Path(ruf_dir)

        # Create directories if they don't exist
        self.rua_dir.mkdir(parents=True, exist_ok=True)
        self.ruf_dir.mkdir(parents=True, exist_ok=True)

        self.rua_files: List[str] = []
        self.ruf_files: List[str] = []
        self.unclassified_files: List[str] = []

    def classify_all(self, input_dir: str) -> Dict[str, List[str]]:
        """
        Classify all files in the input directory

        Args:
            input_dir: Directory containing extracted files (HTML/XML)

        Returns:
            Dictionary with lists of classified files
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Error: Input directory not found: {input_dir}")
            return {'rua': [], 'ruf': [], 'unclassified': []}

        print(f"🔍 Classifying reports from: {input_dir}")

        # Process all files
        for file_path in input_path.glob('*'):
            if file_path.is_file():
                self._classify_file(file_path)

        print(f"\n✅ Classification complete!")
        print(f"   RUA reports: {len(self.rua_files)}")
        print(f"   RUF reports: {len(self.ruf_files)}")
        print(f"   Unclassified: {len(self.unclassified_files)}")

        return {
            'rua': self.rua_files,
            'ruf': self.ruf_files,
            'unclassified': self.unclassified_files
        }

    def _classify_file(self, file_path: Path) -> None:
        """
        Classify a single file as RUA or RUF

        Args:
            file_path: Path to the file to classify
        """
        file_ext = file_path.suffix.lower()

        try:
            if file_ext == '.xml':
                report_type = self._classify_xml(file_path)
            elif file_ext in ['.html', '.htm']:
                report_type = self._classify_html(file_path)
            else:
                report_type = 'unclassified'

            # Move file to appropriate directory
            self._move_file(file_path, report_type)

        except Exception as e:
            print(f"⚠️  Warning: Could not classify {file_path.name}: {str(e)}")
            self.unclassified_files.append(str(file_path))

    def _classify_xml(self, xml_path: Path) -> str:
        """
        Classify XML file as RUA or RUF

        Args:
            xml_path: Path to XML file

        Returns:
            'rua', 'ruf', or 'unclassified'
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Check for RUA indicators (aggregate report structure)
            if root.find('.//report_metadata') is not None:
                if root.find('.//record') is not None:
                    # Has multiple records - typical of RUA
                    return 'rua'

            # Check for RUF indicators (forensic report structure)
            if root.find('.//auth_failure') is not None:
                return 'ruf'

            # Check for feedback element (common in both)
            if root.tag == 'feedback':
                # If has policy_published and records, it's RUA
                if root.find('.//policy_published') is not None and root.find('.//record') is not None:
                    return 'rua'
                # If has auth_failure or original message, it's RUF
                if root.find('.//auth_failure') is not None or root.find('.//original_message') is not None:
                    return 'ruf'

            # Default to unclassified
            return 'unclassified'

        except Exception as e:
            print(f"⚠️  Warning: Error parsing XML {xml_path.name}: {str(e)}")
            return 'unclassified'

    def _classify_html(self, html_path: Path) -> str:
        """
        Classify HTML file as RUA or RUF by analyzing content

        Args:
            html_path: Path to HTML file

        Returns:
            'rua', 'ruf', or 'unclassified'
        """
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text().lower()

            # RUA indicators (aggregate reports)
            rua_keywords = [
                'aggregate report',
                'aggregate feedback',
                'report metadata',
                'policy published',
                'source ip',
                'message count',
                'policy evaluated',
                'dmarc aggregate'
            ]

            # RUF indicators (forensic/failure reports)
            ruf_keywords = [
                'forensic report',
                'failure report',
                'auth failure',
                'authentication failure',
                'original message',
                'message headers',
                'delivery result',
                'authentication-results',
                'forensic feedback',
                'dmarc forensic'
            ]

            # Count keyword matches
            rua_score = sum(1 for keyword in rua_keywords if keyword in text_content)
            ruf_score = sum(1 for keyword in ruf_keywords if keyword in text_content)

            # Additional heuristics for RUA
            # RUA typically has tables with multiple rows (multiple IPs/records)
            tables = soup.find_all('table')
            has_multiple_records = False
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 5:  # More than 5 rows suggests aggregate data
                    has_multiple_records = True
                    break

            if has_multiple_records:
                rua_score += 2

            # Additional heuristics for RUF
            # RUF typically contains email headers
            if 'received:' in text_content and 'from:' in text_content and 'subject:' in text_content:
                ruf_score += 2

            # Classify based on scores
            if rua_score > ruf_score and rua_score > 0:
                return 'rua'
            elif ruf_score > rua_score and ruf_score > 0:
                return 'ruf'
            else:
                # If scores are equal or both zero, try file name heuristics
                filename_lower = html_path.name.lower()
                if 'aggregate' in filename_lower or 'rua' in filename_lower:
                    return 'rua'
                elif 'forensic' in filename_lower or 'ruf' in filename_lower or 'failure' in filename_lower:
                    return 'ruf'

                return 'unclassified'

        except Exception as e:
            print(f"⚠️  Warning: Error parsing HTML {html_path.name}: {str(e)}")
            return 'unclassified'

    def _move_file(self, file_path: Path, report_type: str) -> None:
        """
        Move file to appropriate directory based on classification

        Args:
            file_path: Path to the file
            report_type: 'rua', 'ruf', or 'unclassified'
        """
        # Determine destination directory
        if report_type == 'rua':
            dest_dir = self.rua_dir
            file_list = self.rua_files
            icon = "📊"
        elif report_type == 'ruf':
            dest_dir = self.ruf_dir
            file_list = self.ruf_files
            icon = "⚠️ "
        else:
            # Keep unclassified files in place
            self.unclassified_files.append(str(file_path))
            print(f"❓ Unclassified: {file_path.name}")
            return

        # Generate unique filename in destination
        dest_path = dest_dir / file_path.name
        counter = 1
        while dest_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Copy file to destination
        shutil.copy2(file_path, dest_path)
        file_list.append(str(dest_path))

        print(f"   {icon} {report_type.upper()}: {file_path.name} -> {dest_path.name}")

    def get_statistics(self) -> Dict[str, any]:
        """
        Get classification statistics

        Returns:
            Dictionary with classification statistics
        """
        return {
            'rua_count': len(self.rua_files),
            'ruf_count': len(self.ruf_files),
            'unclassified_count': len(self.unclassified_files),
            'rua_directory': str(self.rua_dir),
            'ruf_directory': str(self.ruf_dir),
            'rua_files': self.rua_files,
            'ruf_files': self.ruf_files
        }


if __name__ == "__main__":
    print("DMARC Report Classifier - PARTE 2")
    print("Usage: from classifiers import ReportClassifier")

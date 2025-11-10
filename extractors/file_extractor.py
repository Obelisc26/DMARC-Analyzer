"""
File Extractor Module - PARTE 1
Extracts HTML files from various compressed formats (ZIP, GZ, EML, etc.)
Handles nested archives (ZIP within EML, etc.)
"""

import os
import zipfile
import gzip
import tarfile
import shutil
import email
from email import policy
from pathlib import Path
from typing import List, Set
import tempfile


class FileExtractor:
    """
    Extractor for DMARC report files from various formats
    Supports: ZIP, GZ, TAR, EML with nested archives
    """

    def __init__(self, output_dir: str = 'reports/extracted'):
        """
        Initialize the file extractor

        Args:
            output_dir: Directory where extracted HTML files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_files: List[str] = []
        self.processed_files: Set[str] = set()

    def extract_all(self, input_dir: str) -> List[str]:
        """
        Extract all HTML files from a directory containing various file types

        Args:
            input_dir: Directory containing raw files (ZIP, EML, GZ, etc.)

        Returns:
            List of paths to extracted HTML files
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Error: Input directory not found: {input_dir}")
            return []

        print(f"🔍 Scanning directory: {input_dir}")

        # Process all files in the input directory
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                self._process_file(file_path)

        print(f"\n✅ Extraction complete!")
        print(f"   Total HTML files extracted: {len(self.extracted_files)}")
        print(f"   Output directory: {self.output_dir}")

        return self.extracted_files

    def _process_file(self, file_path: Path) -> None:
        """
        Process a single file and extract HTML content

        Args:
            file_path: Path to the file to process
        """
        # Avoid processing the same file twice
        if str(file_path) in self.processed_files:
            return

        self.processed_files.add(str(file_path))

        file_ext = file_path.suffix.lower()

        try:
            if file_ext == '.zip':
                self._extract_zip(file_path)
            elif file_ext == '.gz':
                self._extract_gz(file_path)
            elif file_ext in ['.tar', '.tgz']:
                self._extract_tar(file_path)
            elif file_ext == '.eml':
                self._extract_eml(file_path)
            elif file_ext in ['.html', '.htm']:
                self._copy_html(file_path)
            elif file_ext == '.xml':
                self._copy_xml(file_path)
            else:
                # Try to detect file type by content
                self._detect_and_extract(file_path)

        except Exception as e:
            print(f"⚠️  Warning: Could not process {file_path.name}: {str(e)}")

    def _extract_zip(self, zip_path: Path) -> None:
        """Extract contents from ZIP file"""
        print(f"📦 Extracting ZIP: {zip_path.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)

                # Process extracted files recursively
                for extracted_file in temp_path.rglob('*'):
                    if extracted_file.is_file():
                        self._process_file(extracted_file)

            except zipfile.BadZipFile:
                print(f"⚠️  Warning: Invalid ZIP file: {zip_path.name}")

    def _extract_gz(self, gz_path: Path) -> None:
        """Extract contents from GZ file"""
        print(f"📦 Extracting GZ: {gz_path.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Determine output filename (remove .gz extension)
            output_name = gz_path.stem
            output_file = temp_path / output_name

            try:
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(output_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Process the extracted file
                self._process_file(output_file)

            except gzip.BadGzipFile:
                print(f"⚠️  Warning: Invalid GZ file: {gz_path.name}")

    def _extract_tar(self, tar_path: Path) -> None:
        """Extract contents from TAR file"""
        print(f"📦 Extracting TAR: {tar_path.name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                with tarfile.open(tar_path, 'r:*') as tar_ref:
                    tar_ref.extractall(temp_path)

                # Process extracted files recursively
                for extracted_file in temp_path.rglob('*'):
                    if extracted_file.is_file():
                        self._process_file(extracted_file)

            except tarfile.TarError:
                print(f"⚠️  Warning: Invalid TAR file: {tar_path.name}")

    def _extract_eml(self, eml_path: Path) -> None:
        """Extract attachments from EML file"""
        print(f"📧 Processing EML: {eml_path.name}")

        try:
            with open(eml_path, 'rb') as f:
                msg = email.message_from_binary_file(f, policy=policy.default)

            # Process all attachments
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue

                filename = part.get_filename()
                if not filename:
                    continue

                # Save attachment to temp file and process it
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / filename

                    with open(temp_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))

                    # Process the attachment recursively
                    self._process_file(temp_path)

        except Exception as e:
            print(f"⚠️  Warning: Could not parse EML file {eml_path.name}: {str(e)}")

    def _copy_html(self, html_path: Path) -> None:
        """Copy HTML file to output directory"""
        # Generate unique filename
        base_name = html_path.stem
        extension = html_path.suffix
        counter = 1
        output_path = self.output_dir / f"{base_name}{extension}"

        while output_path.exists():
            output_path = self.output_dir / f"{base_name}_{counter}{extension}"
            counter += 1

        shutil.copy2(html_path, output_path)
        self.extracted_files.append(str(output_path))
        print(f"   ✓ HTML extracted: {output_path.name}")

    def _copy_xml(self, xml_path: Path) -> None:
        """Copy XML file to output directory (for legacy RUA reports)"""
        # Generate unique filename
        base_name = xml_path.stem
        extension = xml_path.suffix
        counter = 1
        output_path = self.output_dir / f"{base_name}{extension}"

        while output_path.exists():
            output_path = self.output_dir / f"{base_name}_{counter}{extension}"
            counter += 1

        shutil.copy2(xml_path, output_path)
        self.extracted_files.append(str(output_path))
        print(f"   ✓ XML extracted: {output_path.name}")

    def _detect_and_extract(self, file_path: Path) -> None:
        """
        Try to detect file type by reading content
        Handles files without proper extensions
        """
        try:
            # Try to read as text to check for HTML/XML
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars

                if '<!DOCTYPE html' in content or '<html' in content.lower():
                    # It's an HTML file
                    self._copy_html(file_path)
                elif '<?xml' in content:
                    # It's an XML file
                    self._copy_xml(file_path)

        except:
            # If we can't read it as text, try as binary archive
            try:
                # Try as ZIP
                if zipfile.is_zipfile(file_path):
                    self._extract_zip(file_path)
                # Try as TAR
                elif tarfile.is_tarfile(file_path):
                    self._extract_tar(file_path)
            except:
                pass  # Skip files we can't process

    def get_statistics(self) -> dict:
        """
        Get extraction statistics

        Returns:
            Dictionary with extraction statistics
        """
        html_count = sum(1 for f in self.extracted_files if f.endswith(('.html', '.htm')))
        xml_count = sum(1 for f in self.extracted_files if f.endswith('.xml'))

        return {
            'total_files_processed': len(self.processed_files),
            'total_files_extracted': len(self.extracted_files),
            'html_files': html_count,
            'xml_files': xml_count,
            'output_directory': str(self.output_dir)
        }


if __name__ == "__main__":
    print("DMARC File Extractor - PARTE 1")
    print("Usage: from extractors import FileExtractor")

#!/usr/bin/env python3
"""
Complete Pipeline Example
Demonstrates running the complete DMARC analysis pipeline in one go
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors import FileExtractor
from classifiers import ReportClassifier
from analyzers import RUAAnalyzer, RUFAnalyzer


def main():
    print("=" * 60)
    print("DMARC Analyzer - Complete Pipeline Example")
    print("=" * 60)
    print()

    # Configuration
    raw_files_dir = 'reports/raw'
    extracted_dir = 'reports/extracted'
    rua_dir = 'reports/rua'
    ruf_dir = 'reports/ruf'
    rua_output = 'rua_analysis_example.xlsx'
    ruf_output = 'ruf_analysis_example.xlsx'

    # Check if raw directory exists and has files
    if not os.path.exists(raw_files_dir):
        print(f"⚠️  Directory '{raw_files_dir}' does not exist.")
        print(f"   Please create it and place your DMARC report files there.")
        print()
        print("Example structure:")
        print("  reports/raw/")
        print("    ├── report1.zip")
        print("    ├── report2.eml")
        print("    ├── report3.gz")
        print("    └── report4.xml")
        return

    # PARTE 1: Extract files
    print("\n🔧 PARTE 1: EXTRACCIÓN DE ARCHIVOS")
    print("-" * 60)

    extractor = FileExtractor(output_dir=extracted_dir)
    extracted_files = extractor.extract_all(raw_files_dir)

    if not extracted_files:
        print("❌ No files were extracted. Please add files to reports/raw/")
        return

    stats = extractor.get_statistics()
    print(f"\n📊 Extraction completed:")
    print(f"   Files processed: {stats['total_files_processed']}")
    print(f"   Files extracted: {stats['total_files_extracted']}")
    print(f"   HTML files: {stats['html_files']}")
    print(f"   XML files: {stats['xml_files']}")

    # PARTE 2: Classify reports
    print("\n🔧 PARTE 2: CLASIFICACIÓN DE REPORTES")
    print("-" * 60)

    classifier = ReportClassifier(rua_dir=rua_dir, ruf_dir=ruf_dir)
    classified = classifier.classify_all(extracted_dir)

    stats = classifier.get_statistics()
    print(f"\n📊 Classification completed:")
    print(f"   RUA reports: {stats['rua_count']}")
    print(f"   RUF reports: {stats['ruf_count']}")
    print(f"   Unclassified: {stats['unclassified_count']}")

    # PARTE 3: Analyze reports
    print("\n🔧 PARTE 3: ANÁLISIS Y GENERACIÓN DE REPORTES")
    print("-" * 60)

    # Analyze RUA reports
    if stats['rua_count'] > 0:
        print(f"\n📊 Analyzing {stats['rua_count']} RUA reports...")

        rua_analyzer = RUAAnalyzer()
        for rua_file in stats['rua_files']:
            rua_analyzer.add_report(rua_file)

        rua_analyzer.generate_report(rua_output)
        print(f"✅ RUA analysis saved to: {rua_output}")
    else:
        print("\n⚠️  No RUA reports found")

    # Analyze RUF reports
    if stats['ruf_count'] > 0:
        print(f"\n📊 Analyzing {stats['ruf_count']} RUF reports...")

        ruf_analyzer = RUFAnalyzer()
        for ruf_file in stats['ruf_files']:
            ruf_analyzer.add_report(ruf_file)

        ruf_analyzer.generate_report(ruf_output)
        print(f"✅ RUF analysis saved to: {ruf_output}")
    else:
        print("\n⚠️  No RUF reports found")

    # Summary
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nGenerated files:")
    if stats['rua_count'] > 0:
        print(f"  📊 {rua_output}")
    if stats['ruf_count'] > 0:
        print(f"  ⚠️  {ruf_output}")
    print()


if __name__ == "__main__":
    main()

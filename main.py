#!/usr/bin/env python3
"""
DMARC Analyzer - Main Script
Integrates all 3 parts of the DMARC analysis pipeline:
  PARTE 1: File extraction (ZIP, EML, GZ → HTML/XML)
  PARTE 2: Report classification (RUA vs RUF)
  PARTE 3: Analysis and report generation
"""

import argparse
import sys
from pathlib import Path

from extractors import FileExtractor
from classifiers import ReportClassifier
from analyzers import RUAAnalyzer, RUFAnalyzer


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("  DMARC ANALYZER - Complete Analysis Pipeline")
    print("=" * 60)
    print("  Parte 1: Extracción de archivos")
    print("  Parte 2: Clasificación RUA/RUF")
    print("  Parte 3: Análisis y generación de reportes")
    print("=" * 60)
    print()


def run_full_pipeline(input_dir: str, output_rua: str = None, output_ruf: str = None, skip_extraction: bool = False):
    """
    Run the complete DMARC analysis pipeline
    """
    output_rua = output_rua or 'rua_analysis.xlsx'
    output_ruf = output_ruf or 'ruf_analysis.xlsx'

    extracted_dir = 'reports/extracted'

    # PARTE 1: Extraction
    if not skip_extraction:
        print("\n" + "🔧 PARTE 1: EXTRACCIÓN DE ARCHIVOS")
        print("-" * 60)
        extractor = FileExtractor(output_dir=extracted_dir)
        extracted_files = extractor.extract_all(input_dir)

        # Si stats['total_files'] es 0, no hay nada que hacer
        stats = extractor.get_statistics()
        
        if stats['total_files'] == 0:
            print("\n❌ No XML/HTML files were extracted. Please check your input directory.")
            return

        print(f"\n📊 Extraction Statistics:")
        # CORREGIDO: Usamos las claves correctas que devuelve FileExtractor
        print(f"   Total files extracted: {stats['total_files']}")
        print(f"   HTML files: {stats['html_files']}")
        print(f"   XML files: {stats['xml_files']}")
    else:
        print("\n⏭️  Skipping extraction (using existing files)")

    # PARTE 2: Classification
    print("\n" + "🔧 PARTE 2: CLASIFICACIÓN DE REPORTES")
    print("-" * 60)
    classifier = ReportClassifier(rua_dir='reports/rua', ruf_dir='reports/ruf')
    classified = classifier.classify_all(extracted_dir)

    stats = classifier.get_statistics()
    print(f"\n📊 Classification Statistics:")
    print(f"   RUA reports: {stats['rua_count']}")
    print(f"   RUF reports: {stats['ruf_count']}")
    print(f"   Unclassified: {stats['unclassified_count']}")

    # PARTE 3: Analysis
    print("\n" + "🔧 PARTE 3: ANÁLISIS Y GENERACIÓN DE REPORTES")
    print("-" * 60)

    # Analyze RUA reports
    if stats['rua_count'] > 0:
        print(f"\n📊 Analyzing {stats['rua_count']} RUA reports...")
        rua_analyzer = RUAAnalyzer()

        for rua_file in stats['rua_files']:
            rua_analyzer.add_report(rua_file)

        rua_analyzer.generate_report(output_rua)
    else:
        print("\n⚠️  No RUA reports found to analyze")

    # Analyze RUF reports
    if stats['ruf_count'] > 0:
        print(f"\n📊 Analyzing {stats['ruf_count']} RUF reports...")
        ruf_analyzer = RUFAnalyzer()

        for ruf_file in stats['ruf_files']:
            ruf_analyzer.add_report(ruf_file)

        ruf_analyzer.generate_report(output_ruf)
    else:
        print("\n⚠️  No RUF reports found to analyze")

    # Final summary
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETO")
    print("=" * 60)
    if stats['rua_count'] > 0:
        print(f"   RUA Analysis: {output_rua}")
    if stats['ruf_count'] > 0:
        print(f"   RUF Analysis: {output_ruf}")
    print("=" * 60)
    print()


def run_extraction_only(input_dir: str):
    """Run only the extraction step"""
    print("\n" + "🔧 EXTRACCIÓN DE ARCHIVOS")
    print("-" * 60)

    extractor = FileExtractor(output_dir='reports/extracted')
    extracted_files = extractor.extract_all(input_dir)

    stats = extractor.get_statistics()
    print(f"\n📊 Extraction Statistics:")
    # CORREGIDO: Usamos las claves correctas
    print(f"   Total files extracted: {stats['total_files']}")
    print(f"   HTML files: {stats['html_files']}")
    print(f"   XML files: {stats['xml_files']}")
    print(f"   Output directory: {extractor.output_dir}")


def run_classification_only(input_dir: str):
    """Run only the classification step"""
    print("\n" + "🔧 CLASIFICACIÓN DE REPORTES")
    print("-" * 60)

    classifier = ReportClassifier(rua_dir='reports/rua', ruf_dir='reports/ruf')
    classified = classifier.classify_all(input_dir)

    stats = classifier.get_statistics()
    print(f"\n📊 Classification Statistics:")
    print(f"   RUA reports: {stats['rua_count']}")
    print(f"   RUF reports: {stats['ruf_count']}")
    print(f"   Unclassified: {stats['unclassified_count']}")
    print(f"   RUA directory: {stats['rua_directory']}")
    print(f"   RUF directory: {stats['ruf_directory']}")


def run_analysis_only(report_type: str, input_dir: str, output_file: str = None):
    """Run only the analysis step"""
    print(f"\n🔧 ANÁLISIS DE REPORTES {report_type.upper()}")
    print("-" * 60)

    if report_type.lower() == 'rua':
        analyzer = RUAAnalyzer()
        output_file = output_file or 'rua_analysis.xlsx'

        # Add all RUA reports from directory
        for report_file in Path(input_dir).glob('*'):
            if report_file.is_file():
                analyzer.add_report(str(report_file))

        analyzer.generate_report(output_file)

    elif report_type.lower() == 'ruf':
        analyzer = RUFAnalyzer()
        output_file = output_file or 'ruf_analysis.xlsx'

        # Add all RUF reports from directory
        for report_file in Path(input_dir).glob('*'):
            if report_file.is_file():
                analyzer.add_report(str(report_file))

        analyzer.generate_report(output_file)

    else:
        print(f"❌ Error: Unknown report type '{report_type}'. Use 'rua' or 'ruf'.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DMARC Analyzer - Complete analysis pipeline for RUA and RUF reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  %(prog)s --input reports/raw

  # Run with custom output files
  %(prog)s --input reports/raw --output-rua my_rua.xlsx --output-ruf my_ruf.xlsx

  # Run only extraction
  %(prog)s --extract --input reports/raw
        """
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Input directory containing files')
    parser.add_argument('--output-rua', '-or',
                        help='Output filename for RUA analysis (default: rua_analysis.xlsx)')
    parser.add_argument('--output-ruf', '-of',
                        help='Output filename for RUF analysis (default: ruf_analysis.xlsx)')
    parser.add_argument('--extract', '-e', action='store_true',
                        help='Run only extraction step')
    parser.add_argument('--classify', '-c', action='store_true',
                        help='Run only classification step')
    parser.add_argument('--analyze', '-a', choices=['rua', 'ruf'],
                        help='Run only analysis step (specify rua or ruf)')
    parser.add_argument('--output', '-o',
                        help='Output filename for --analyze mode')
    parser.add_argument('--skip-extraction', '-s', action='store_true',
                        help='Skip extraction step (use existing extracted files)')

    args = parser.parse_args()

    # Validate input directory
    if not Path(args.input).exists():
        print(f"❌ Error: Input directory not found: {args.input}")
        sys.exit(1)

    # Print banner
    print_banner()

    # Run appropriate mode
    if args.extract:
        run_extraction_only(args.input)
    elif args.classify:
        run_classification_only(args.input)
    elif args.analyze:
        run_analysis_only(args.analyze, args.input, args.output)
    else:
        # Run full pipeline
        run_full_pipeline(args.input, args.output_rua, args.output_ruf, args.skip_extraction)


if __name__ == "__main__":
    main()

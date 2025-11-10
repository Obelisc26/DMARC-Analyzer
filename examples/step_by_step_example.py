#!/usr/bin/env python3
"""
Step by Step Example
Demonstrates running each part of the pipeline individually
Useful for debugging or when you want more control over the process
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors import FileExtractor
from classifiers import ReportClassifier
from analyzers import RUAAnalyzer, RUFAnalyzer


def step_1_extract():
    """PARTE 1: Extract files from compressed formats"""
    print("\n" + "=" * 60)
    print("STEP 1: FILE EXTRACTION")
    print("=" * 60)

    raw_dir = 'reports/raw'
    output_dir = 'reports/extracted'

    if not os.path.exists(raw_dir):
        print(f"⚠️  Please create directory '{raw_dir}' and add files")
        return False

    extractor = FileExtractor(output_dir=output_dir)
    files = extractor.extract_all(raw_dir)

    stats = extractor.get_statistics()
    print(f"\n✅ Extraction complete:")
    print(f"   Files extracted: {stats['total_files_extracted']}")
    print(f"   Output directory: {stats['output_directory']}")

    return len(files) > 0


def step_2_classify():
    """PARTE 2: Classify reports into RUA and RUF"""
    print("\n" + "=" * 60)
    print("STEP 2: REPORT CLASSIFICATION")
    print("=" * 60)

    input_dir = 'reports/extracted'
    rua_dir = 'reports/rua'
    ruf_dir = 'reports/ruf'

    if not os.path.exists(input_dir):
        print(f"⚠️  Please run Step 1 first to extract files")
        return False, 0, 0

    classifier = ReportClassifier(rua_dir=rua_dir, ruf_dir=ruf_dir)
    results = classifier.classify_all(input_dir)

    stats = classifier.get_statistics()
    print(f"\n✅ Classification complete:")
    print(f"   RUA reports: {stats['rua_count']}")
    print(f"   RUF reports: {stats['ruf_count']}")
    print(f"   Unclassified: {stats['unclassified_count']}")

    return True, stats['rua_count'], stats['ruf_count']


def step_3a_analyze_rua(rua_dir='reports/rua', output='rua_analysis_step_by_step.xlsx'):
    """PARTE 3a: Analyze RUA reports"""
    print("\n" + "=" * 60)
    print("STEP 3a: ANALYZE RUA REPORTS")
    print("=" * 60)

    if not os.path.exists(rua_dir):
        print(f"⚠️  No RUA reports found in '{rua_dir}'")
        return False

    # Count files in directory
    rua_files = [f for f in os.listdir(rua_dir) if os.path.isfile(os.path.join(rua_dir, f))]

    if not rua_files:
        print(f"⚠️  No RUA reports found")
        return False

    print(f"📊 Found {len(rua_files)} RUA reports")

    # Analyze all RUA reports
    analyzer = RUAAnalyzer()

    for filename in rua_files:
        filepath = os.path.join(rua_dir, filename)
        analyzer.add_report(filepath)

    # Generate report
    analyzer.generate_report(output)

    print(f"\n✅ RUA analysis saved to: {output}")
    return True


def step_3b_analyze_ruf(ruf_dir='reports/ruf', output='ruf_analysis_step_by_step.xlsx'):
    """PARTE 3b: Analyze RUF reports"""
    print("\n" + "=" * 60)
    print("STEP 3b: ANALYZE RUF REPORTS")
    print("=" * 60)

    if not os.path.exists(ruf_dir):
        print(f"⚠️  No RUF reports found in '{ruf_dir}'")
        return False

    # Count files in directory
    ruf_files = [f for f in os.listdir(ruf_dir) if os.path.isfile(os.path.join(ruf_dir, f))]

    if not ruf_files:
        print(f"⚠️  No RUF reports found")
        return False

    print(f"📊 Found {len(ruf_files)} RUF reports")

    # Analyze all RUF reports
    analyzer = RUFAnalyzer()

    for filename in ruf_files:
        filepath = os.path.join(ruf_dir, filename)
        analyzer.add_report(filepath)

    # Generate report
    analyzer.generate_report(output)

    print(f"\n✅ RUF analysis saved to: {output}")
    return True


def main():
    print("=" * 60)
    print("DMARC Analyzer - Step by Step Example")
    print("=" * 60)
    print()
    print("This example runs each part of the pipeline separately,")
    print("giving you full control over each step.")
    print()

    # Ask user what to do
    print("Choose an option:")
    print("  1. Run all steps")
    print("  2. Run step 1 only (Extract)")
    print("  3. Run step 2 only (Classify)")
    print("  4. Run step 3a only (Analyze RUA)")
    print("  5. Run step 3b only (Analyze RUF)")
    print()

    choice = input("Enter your choice (1-5) or press Enter for option 1: ").strip()

    if not choice:
        choice = "1"

    if choice == "1":
        # Run all steps
        if step_1_extract():
            success, rua_count, ruf_count = step_2_classify()
            if success:
                if rua_count > 0:
                    step_3a_analyze_rua()
                if ruf_count > 0:
                    step_3b_analyze_ruf()

    elif choice == "2":
        step_1_extract()

    elif choice == "3":
        step_2_classify()

    elif choice == "4":
        step_3a_analyze_rua()

    elif choice == "5":
        step_3b_analyze_ruf()

    else:
        print("❌ Invalid choice")
        return

    print("\n" + "=" * 60)
    print("✅ DONE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

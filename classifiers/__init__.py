"""
Classifiers package for DMARC Analyzer
Handles classification of reports into RUA and RUF types
"""

from .report_classifier import ReportClassifier

__all__ = ['ReportClassifier']

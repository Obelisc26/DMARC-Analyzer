"""
Analyzers package for DMARC Analyzer
Contains analyzers for RUA (aggregate) and RUF (forensic) reports
"""

from .rua_analyzer import RUAAnalyzer
from .ruf_analyzer import RUFAnalyzer

__all__ = ['RUAAnalyzer', 'RUFAnalyzer']

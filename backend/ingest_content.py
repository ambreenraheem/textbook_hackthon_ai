#!/usr/bin/env python3
"""
Content ingestion CLI script.

Usage:
    python ingest_content.py                    # Ingest with defaults
    python ingest_content.py --rebuild          # Rebuild collection from scratch
    python ingest_content.py --validate         # Validate after ingestion
    python ingest_content.py --input docs/      # Custom input directory
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.ingestion.pipeline import main

if __name__ == '__main__':
    main()

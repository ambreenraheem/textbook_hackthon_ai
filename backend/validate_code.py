#!/usr/bin/env python3
"""
Validate Python code syntax without executing.

Checks all Python files for syntax errors.
"""
import ast
import sys
from pathlib import Path


def validate_file(file_path: Path) -> bool:
    """
    Validate Python file syntax.

    Args:
        file_path: Path to Python file

    Returns:
        True if valid, False if syntax error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        print(f"[OK] {file_path.name}")
        return True
    except SyntaxError as e:
        print(f"[ERR] {file_path.name}: {e}")
        return False
    except Exception as e:
        print(f"[WARN] {file_path.name}: {e}")
        return False


def main():
    """Validate all Python files in src/ingestion."""
    print("Validating ingestion module syntax...\n")

    src_dir = Path(__file__).parent / "src"

    files_to_check = [
        src_dir / "ingestion" / "__init__.py",
        src_dir / "ingestion" / "parser.py",
        src_dir / "ingestion" / "chunker.py",
        src_dir / "ingestion" / "pipeline.py",
        src_dir / "services" / "embeddings.py",
        Path(__file__).parent / "ingest_content.py",
    ]

    results = []
    for file_path in files_to_check:
        if file_path.exists():
            results.append(validate_file(file_path))
        else:
            print(f"? {file_path.name}: File not found")
            results.append(False)

    print(f"\n{'=' * 60}")
    valid_count = sum(results)
    total_count = len(results)
    print(f"Results: {valid_count}/{total_count} files valid")

    if valid_count == total_count:
        print("[SUCCESS] All files have valid Python syntax")
        sys.exit(0)
    else:
        print("[FAILED] Some files have syntax errors")
        sys.exit(1)


if __name__ == '__main__':
    main()

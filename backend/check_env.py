"""
Check if .env file is properly configured with all required credentials.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def check_env():
    print("Checking .env configuration...\n")

    try:
        from src.config.settings import get_settings
        settings = get_settings()

        # Check OpenAI API Key
        if settings.openai_api_key and settings.openai_api_key != "sk-proj-...your-key-here":
            print(f"[OK] OPENAI_API_KEY: {settings.openai_api_key[:20]}...")
        else:
            print("[ERROR] OPENAI_API_KEY: NOT SET - Please add your OpenAI API key to .env")
            return False

        # Check Database URL
        if settings.database_url and "your-cluster" not in settings.database_url:
            print(f"[OK] DATABASE_URL: {settings.database_url[:40]}...")
        else:
            print("[ERROR] DATABASE_URL: NOT SET - Please add your Neon Postgres connection string to .env")
            return False

        # Check Qdrant URL
        if settings.qdrant_url and "your-cluster" not in settings.qdrant_url:
            print(f"[OK] QDRANT_URL: {settings.qdrant_url[:40]}...")
        else:
            print("[ERROR] QDRANT_URL: NOT SET - Please add your Qdrant Cloud URL to .env")
            return False

        # Check Qdrant API Key
        if settings.qdrant_api_key and settings.qdrant_api_key != "your-qdrant-api-key":
            print(f"[OK] QDRANT_API_KEY: {settings.qdrant_api_key[:20]}...")
        else:
            print("[ERROR] QDRANT_API_KEY: NOT SET - Please add your Qdrant API key to .env")
            return False

        print("\n[SUCCESS] All credentials are configured!")
        print("\nNext steps:")
        print("  1. Run database migration: cd backend && alembic upgrade head")
        print("  2. Setup Qdrant collection: cd backend && python src/utils/qdrant_setup.py")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error loading configuration: {e}")
        print("\nMake sure you:")
        print("  1. Created .env file in the project root (E:\\textbook_hackthon_ai\\.env)")
        print("  2. Copied values from .env.example")
        print("  3. Replaced placeholder values with your actual credentials")
        return False


if __name__ == "__main__":
    success = check_env()
    sys.exit(0 if success else 1)

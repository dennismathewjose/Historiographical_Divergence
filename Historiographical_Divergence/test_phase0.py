#!/usr/bin/env python3
"""Test Phase 0 setup."""

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    try:
        import openai
        import anthropic
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import numpy as np
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_project_structure():
    """Test project modules load."""
    print("\nTesting project structure...")
    try:
        from src.utils.logger import get_logger
        from src.utils.data_loader import load_json, save_json
        from config.settings import DATA_DIR, EVENTS
        
        logger = get_logger('test')
        logger.info("Test log message")
        
        print(f"  DATA_DIR: {DATA_DIR}")
        print(f"  Events: {len(EVENTS)}")
        print("✓ Project structure works")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_api_keys():
    """Check API keys."""
    print("\nChecking API keys...")
    try:
        from config.settings import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
        
        keys_set = 0
        if OPENAI_API_KEY:
            print("  ✓ OpenAI key set")
            keys_set += 1
        if ANTHROPIC_API_KEY:
            print("  ✓ Anthropic key set")
            keys_set += 1
        if GOOGLE_API_KEY:
            print("  ✓ Google key set")
            keys_set += 1
        
        if keys_set == 0:
            print("  ⚠ No API keys set - add to .env file")
            return False
        else:
            print(f"✓ {keys_set} API key(s) configured")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 0 VERIFICATION")
    print("=" * 60)
    print()
    
    results = [
        test_imports(),
        test_project_structure(),
        test_api_keys()
    ]
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL {total} TESTS PASSED!")
        print("\nReady for Phase 1A: Gutenberg Scraper")
        return 0
    else:
        print(f"✗ {total - passed}/{total} tests failed")
        print("\nFix issues above before proceeding")
        return 1


if __name__ == "__main__":
    exit(main())
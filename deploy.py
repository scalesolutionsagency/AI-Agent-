#!/usr/bin/env python3
"""Deployment script for Railway and Render platforms."""

import os
import subprocess
from pathlib import Path


def setup_directories():
    """Create required directories."""
    directories = ["./data", "./logs", "./output", "./credentials"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")


def check_env_vars():
    """Check required environment variables."""
    required_vars = [
        "LEAD_SOURCE",
    ]
    
    optional_vars = {
        "apify": ["APIFY_API_TOKEN"],
        "apollo": ["APOLLO_API_KEY"],
        "google_places": ["GOOGLE_PLACES_API_KEY"],
        "google_sheets": ["GOOGLE_SHEETS_CREDENTIALS_PATH", "GOOGLE_SHEET_ID"],
        "notion": ["NOTION_API_TOKEN", "NOTION_DATABASE_ID"],
    }
    
    print("\n=== Checking Environment Variables ===")
    
    # Check required
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"✗ Missing required: {', '.join(missing)}")
        return False
    
    print("✓ Required variables set")
    
    # Check optional
    lead_source = os.getenv("LEAD_SOURCE", "apify")
    if lead_source in optional_vars:
        for var in optional_vars[lead_source]:
            status = "✓" if os.getenv(var) else "✗"
            print(f"{status} {var}")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\n=== Installing Dependencies ===")
    try:
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False


def main():
    """Run deployment setup."""
    print("Lead Scraper Agent - Deployment Setup")
    print("=" * 40)
    
    setup_directories()
    check_env_vars()
    install_dependencies()
    
    print("\n" + "=" * 40)
    print("Setup complete! You can now:")
    print("  - Run manually: python main.py")
    print("  - Run scheduler: python scheduler.py")
    print("=" * 40)


if __name__ == "__main__":
    main()

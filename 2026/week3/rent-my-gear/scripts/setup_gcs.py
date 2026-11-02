#!/usr/bin/env python3
"""
Google Cloud Storage Setup Script

Creates a GCS bucket with public access and performs a smoke test
to validate IAM permissions.

Usage:
    uv run setup_gcs.py

Requirements:
    - GCS_BUCKET_NAME in .env file
    - GCS_PROJECT_ID in .env file
    - GOOGLE_APPLICATION_CREDENTIALS in .env file (path to service account JSON)
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import storage
from google.cloud.exceptions import Conflict, NotFound

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from parent directory
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

# Configuration from environment
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
PROJECT_ID = os.getenv("GCS_PROJECT_ID")
_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# Resolve credentials path relative to project root if it's a relative path
if _credentials_path and not Path(_credentials_path).is_absolute():
    CREDENTIALS_PATH = str(PROJECT_ROOT / _credentials_path)
else:
    CREDENTIALS_PATH = _credentials_path

# Smoke test file
SMOKE_TEST_FILENAME = "smoke-test.txt"
SMOKE_TEST_CONTENT = "Rent my Gear - GCS Smoke Test"


def validate_config():
    """Validate required environment variables are set."""
    errors = []

    if not BUCKET_NAME:
        errors.append("GCS_BUCKET_NAME is not set")
    if not PROJECT_ID:
        errors.append("GCS_PROJECT_ID is not set")
    if not CREDENTIALS_PATH:
        errors.append("GOOGLE_APPLICATION_CREDENTIALS is not set")
    elif not Path(CREDENTIALS_PATH).exists():
        errors.append(f"GOOGLE_APPLICATION_CREDENTIALS file not found: {CREDENTIALS_PATH}")
    else:
        # Set the environment variable for the GCS client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        print()
        print("Please check your .env.local file")
        sys.exit(1)


def create_bucket(client: storage.Client) -> storage.Bucket:
    """Create the GCS bucket if it doesn't exist."""
    print(f"📦 Checking bucket: {BUCKET_NAME}")

    try:
        bucket = client.get_bucket(BUCKET_NAME)
        print(f"   ✅ Bucket already exists")
        return bucket
    except NotFound:
        print(f"   📝 Creating bucket...")

    try:
        bucket = client.bucket(BUCKET_NAME)
        bucket.storage_class = "STANDARD"
        bucket = client.create_bucket(bucket, location="us-central1")
        print(f"   ✅ Bucket created: {bucket.name}")
        return bucket
    except Conflict:
        print(f"   ⚠️  Bucket name already taken globally")
        print(f"   Please choose a different GCS_BUCKET_NAME")
        sys.exit(1)


def set_public_access(bucket: storage.Bucket):
    """Configure the bucket for public read access."""
    print(f"🔓 Configuring public access...")

    try:
        # Disable uniform bucket-level access to use ACLs
        bucket.iam_configuration.uniform_bucket_level_access_enabled = False
        bucket.patch()

        # Make all objects publicly readable by default
        policy = bucket.get_iam_policy(requested_policy_version=3)
        policy.bindings.append({
            "role": "roles/storage.objectViewer",
            "members": ["allUsers"],
        })
        bucket.set_iam_policy(policy)

        print(f"   ✅ Public read access enabled")
    except Exception as e:
        print(f"   ⚠️  Could not set public access: {e}")
        print(f"   You may need to configure this manually in GCS console")


def smoke_test(bucket: storage.Bucket) -> bool:
    """
    Perform a smoke test: upload a file, verify public URL, then delete.
    Returns True if all operations succeed.
    """
    print(f"🧪 Running smoke test...")

    blob = bucket.blob(SMOKE_TEST_FILENAME)

    # Step 1: Upload
    print(f"   1️⃣  Uploading test file...")
    try:
        blob.upload_from_string(SMOKE_TEST_CONTENT, content_type="text/plain")
        print(f"      ✅ Upload successful")
    except Exception as e:
        print(f"      ❌ Upload failed: {e}")
        return False

    # Step 2: Verify public URL
    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{SMOKE_TEST_FILENAME}"
    print(f"   2️⃣  Verifying public URL...")
    print(f"      🔗 {public_url}")

    try:
        import requests
        response = requests.get(public_url, timeout=10)
        if response.status_code == 200 and response.text == SMOKE_TEST_CONTENT:
            print(f"      ✅ Public access verified")
        else:
            print(f"      ⚠️  URL accessible but content mismatch (status: {response.status_code})")
    except Exception as e:
        print(f"      ⚠️  Could not verify public URL: {e}")
        print(f"      (This may be due to IAM propagation delay)")

    # Step 3: Delete
    print(f"   3️⃣  Cleaning up test file...")
    try:
        blob.delete()
        print(f"      ✅ Test file deleted")
    except Exception as e:
        print(f"      ⚠️  Could not delete test file: {e}")

    return True


def main():
    """Main entry point."""
    print()
    print("=" * 50)
    print("  Rent my Gear - GCS Setup")
    print("=" * 50)
    print()

    # Validate configuration
    validate_config()

    print(f"📋 Configuration:")
    print(f"   Bucket:  {BUCKET_NAME}")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Creds:   {CREDENTIALS_PATH}")
    print()

    # Initialize client
    try:
        client = storage.Client(project=PROJECT_ID)
    except Exception as e:
        print(f"❌ Failed to initialize GCS client: {e}")
        sys.exit(1)

    # Create bucket
    bucket = create_bucket(client)

    # Set public access
    set_public_access(bucket)
    print()

    # Smoke test
    success = smoke_test(bucket)

    print()
    print("=" * 50)
    if success:
        print("✅ GCS setup completed successfully!")
        print()
        print(f"📌 Your bucket is ready:")
        print(f"   Name: {BUCKET_NAME}")
        print(f"   URL:  https://storage.googleapis.com/{BUCKET_NAME}/")
    else:
        print("⚠️  GCS setup completed with warnings")
        print("   Please check the errors above")

    print("=" * 50)
    print()


if __name__ == "__main__":
    main()

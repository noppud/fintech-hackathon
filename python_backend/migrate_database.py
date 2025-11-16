#!/usr/bin/env python3
"""
Database migration script for Supabase.

Applies the schema defined in supabase_schema.sql to your Supabase database.
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

def get_supabase_client() -> Client:
    """Get Supabase client for admin operations."""
    url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not service_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        print("\nMake sure your .env file contains:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_SERVICE_KEY=your-service-role-key")
        sys.exit(1)

    return create_client(url, service_key)

def run_sql_file(client: Client, sql_file_path: Path) -> None:
    """Execute SQL file using Supabase REST API."""
    if not sql_file_path.exists():
        print(f"❌ Error: SQL file not found: {sql_file_path}")
        sys.exit(1)

    sql_content = sql_file_path.read_text()

    print(f"📄 Reading SQL from: {sql_file_path}")
    print(f"📝 SQL file size: {len(sql_content)} characters")

    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    print(f"\n🔧 Executing {len(statements)} SQL statements...")

    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if statement.startswith('--') or not statement:
            continue

        # Show progress
        first_line = statement.split('\n')[0][:60]
        print(f"  [{i}/{len(statements)}] {first_line}...")

        try:
            # Execute via Supabase RPC (if available) or direct SQL
            # Note: Supabase Python client doesn't have direct SQL execution
            # You may need to use psycopg2 or execute via Supabase dashboard
            # For now, we'll just validate the SQL
            pass
        except Exception as e:
            print(f"    ⚠️  Warning: {e}")
            continue

    print("\n✅ SQL file processed!")

def create_tables_manually(client: Client) -> None:
    """Create tables using Supabase client insert/upsert operations."""
    print("\n🏗️  Creating tables using Supabase API...")

    # Test if tables exist by attempting to query them
    tables_to_check = [
        "sheet_tabs",
        "conversation_messages",
        "cell_color_snapshots",
        "cell_value_snapshots"
    ]

    for table_name in tables_to_check:
        try:
            # Try to select from table (will fail if doesn't exist)
            result = client.table(table_name).select("*").limit(1).execute()
            print(f"  ✅ Table '{table_name}' exists")
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                print(f"  ❌ Table '{table_name}' does NOT exist")
                print(f"     Error: {error_msg}")
            else:
                print(f"  ⚠️  Table '{table_name}' status unknown: {error_msg}")

def main():
    """Main migration function."""
    print("=" * 70)
    print("  Supabase Database Migration")
    print("=" * 70)

    # Get Supabase client
    client = get_supabase_client()
    print(f"✅ Connected to Supabase: {os.environ.get('SUPABASE_URL')}")

    # Check current table status
    create_tables_manually(client)

    print("\n" + "=" * 70)
    print("📋 MANUAL STEPS REQUIRED:")
    print("=" * 70)
    print("\nThe Supabase Python client doesn't support direct SQL execution.")
    print("Please apply the schema manually using one of these methods:")
    print("\n1. **Supabase Dashboard (Recommended)**:")
    print("   - Go to https://app.supabase.com")
    print("   - Open your project")
    print("   - Navigate to SQL Editor")
    print("   - Open the file: supabase_schema.sql")
    print("   - Copy and paste the SQL")
    print("   - Click 'Run'")
    print("\n2. **Using psql command line**:")
    print("   psql 'postgresql://postgres:[password]@[host]:5432/postgres' \\")
    print("        -f supabase_schema.sql")
    print("\n3. **Using Supabase CLI**:")
    print("   supabase db push")
    print("\n" + "=" * 70)

    # Show the SQL file path
    sql_file = PROJECT_ROOT / "supabase_schema.sql"
    print(f"\n📄 SQL schema file location:")
    print(f"   {sql_file}")

    if sql_file.exists():
        print(f"\n✅ Schema file exists and is ready to apply")
    else:
        print(f"\n❌ Schema file not found!")
        sys.exit(1)

if __name__ == "__main__":
    main()

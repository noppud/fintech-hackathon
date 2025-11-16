#!/usr/bin/env python3
"""
Apply database schema directly to Supabase using psycopg2.
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

def apply_schema():
    """Apply schema using psycopg2 with Supabase connection."""
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 not installed. Installing...")
        os.system("pip install psycopg2-binary")
        import psycopg2

    # Read the schema SQL file
    schema_file = PROJECT_ROOT / "supabase_schema.sql"
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)

    sql_content = schema_file.read_text()

    # Get Supabase connection details
    supabase_url = os.environ.get("SUPABASE_URL")
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env")
        sys.exit(1)

    # Extract project ref from URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")

    # Ask for database password (not the same as service key)
    print("=" * 70)
    print("  Supabase Database Schema Application")
    print("=" * 70)
    print(f"\nProject: {project_ref}")
    print(f"\nTo get your database password:")
    print("1. Go to https://app.supabase.com")
    print("2. Select your project")
    print("3. Go to Settings → Database")
    print("4. Find 'Database Password' (the one you set when creating the project)")
    print("\nNote: This is NOT the same as your service role key!")
    print()

    db_password = input("Enter your Supabase database password: ").strip()

    if not db_password:
        print("❌ Password is required")
        sys.exit(1)

    # Construct connection string (using direct connection, not pooler)
    # Direct: db.PROJECT_REF.supabase.co:5432
    connection_string = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    print(f"\n🔌 Connecting to Supabase...")

    try:
        # Connect to database
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        print("✅ Connected successfully!")
        print(f"\n📝 Executing schema SQL ({len(sql_content)} characters)...")

        # Execute the schema SQL
        cursor.execute(sql_content)

        print("✅ Schema applied successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('sheet_tabs', 'conversation_messages', 'cell_color_snapshots', 'cell_value_snapshots')
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\n✅ Verified {len(tables)} tables:")
        for (table_name,) in tables:
            print(f"   ✓ {table_name}")

        cursor.close()
        conn.close()

        print("\n" + "=" * 70)
        print("  ✅ Database migration completed successfully!")
        print("=" * 70)

    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your database password is correct")
        print("2. Check that your IP is allowed in Supabase (Settings → Database → Connection pooling)")
        print("3. Try using the Session pooler instead (port 6543)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_schema()

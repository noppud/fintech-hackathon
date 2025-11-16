#!/usr/bin/env python3
"""
Create Supabase tables using REST API via SQL RPC endpoint.
"""

import os
import sys
import requests
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

def execute_sql_via_rest(sql: str) -> bool:
    """Execute SQL using Supabase REST API."""
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY required in .env")
        return False

    # Supabase provides a query endpoint in their Management API
    # Try using the PostgREST RPC endpoint
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }

    # First, create an RPC function that can execute DDL
    print("Creating temporary SQL executor function...")

    create_executor_sql = """
    CREATE OR REPLACE FUNCTION execute_sql(sql_query text)
    RETURNS text
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
        EXECUTE sql_query;
        RETURN 'success';
    END;
    $$;
    """

    # We can't execute this directly via REST, so try a different approach
    # Use the Supabase SQL endpoint if available

    # Actually, let's just try making direct table creation via REST
    # This won't work for CREATE TABLE, but let's see

    print("❌ Cannot execute DDL via Supabase REST API")
    print("\nSupabase REST API doesn't support arbitrary SQL execution for security reasons.")
    print("You have two options:")
    print("\n1. **Use Supabase Dashboard (Recommended - 2 minutes)**:")
    print("   - Go to https://app.supabase.com")
    print("   - Select your project")
    print("   - Click SQL Editor → New Query")
    print(f"   - Copy paste the content from: {PROJECT_ROOT}/supabase_schema.sql")
    print("   - Click Run")
    print("\n2. **Use psql with database password**:")
    print("   - Get your database password from Supabase Settings → Database")
    print("   - Run: psql 'postgresql://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres' -f supabase_schema.sql")

    return False

if __name__ == "__main__":
    print("=" * 70)
    print("  Supabase Schema Application via REST API")
    print("=" * 70)

    schema_file = PROJECT_ROOT / "supabase_schema.sql"
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        sys.exit(1)

    sql_content = schema_file.read_text()
    success = execute_sql_via_rest(sql_content)

    if not success:
        print("\n" + "=" * 70)
        print("  Manual Steps Required")
        print("=" * 70)
        sys.exit(1)

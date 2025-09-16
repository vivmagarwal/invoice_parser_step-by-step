import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_UZFS2c7kMeqC@ep-restless-lake-adbnc07i-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
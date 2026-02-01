
import os
import psycopg2

db_url = "postgresql://postgres:6zhUUO3ZKr1A9QUF@db.ztbahzjmycthbjhiqgrd.supabase.co:5432/postgres"

def list_all_tables():
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT schemaname, tablename 
            FROM pg_catalog.pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        """)
        
        tables = cur.fetchall()
        print("--- All Visible Tables ---")
        for schema, table in tables:
            print(f"{schema}.{table}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    list_all_tables()

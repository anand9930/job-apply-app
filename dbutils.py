import psycopg2
from datetime import date

# Database connection parameters
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",  # or your DB host
    "port": 5432
}


# SQL insert query
insert_query = """
INSERT INTO jobapply.job_postings (
    job_id, company_name, job_title, location, job_link, 
    job_description, job_criteria, job_posted_date
) VALUES (
    %(job_id)s, %(company_name)s, %(job_title)s, %(location)s, %(job_link)s,
    %(job_description)s, %(job_criteria)s, %(job_posted_date)s
)
ON CONFLICT (job_id) DO NOTHING;
"""

# Insert function
def insert_job_posting(data):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(insert_query, data)
        conn.commit()
        print("✅ Job inserted successfully.")
    except Exception as e:
        print(f"❌ Error inserting job: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

import sqlite3
import os

def build_financial_db(db_path="data/financials.db"):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to SQLite (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create a table for company financial summaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            revenue_billion REAL,
            net_income_billion REAL,
            total_assets_billion REAL
        )
    ''')
    
    # 2. Insert some realistic data for testing (e.g., Maybank numbers)
    sample_data = [
        ('Maybank', 2023, 'Full Year', 64.4, 9.35, 1000.2),
        ('Maybank', 2024, 'Full Year', 68.1, 9.80, 1045.5),
        ('Maybank', 2025, 'Full Year', 71.5, 10.2, 1090.0)
    ]
    
    cursor.executemany('''
        INSERT INTO company_financials (company_name, fiscal_year, quarter, revenue_billion, net_income_billion, total_assets_billion)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    print(f"Database successfully built and seeded at: {db_path}")
    
    # Quick sanity check print
    cursor.execute("SELECT * FROM company_financials")
    print("Current DB Rows:", cursor.fetchall())
    
    conn.close()

if __name__ == "__main__":
    build_financial_db()
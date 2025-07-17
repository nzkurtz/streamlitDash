import pandas as pd
import sqlite3
from datetime import datetime

def create_database_from_excel(excel_path='output3.xlsx', db_path='funding_data.db'):
    """Create a new SQLite database from Excel file"""
    print(f"Creating new database from {excel_path}")
    
    # Load Excel data
    df = pd.read_excel(excel_path)
    print(f"Loaded {len(df)} records from Excel")
    
    # Connect to SQLite database (creates new file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    # Add metadata columns
    df['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the table
    df.to_sql('funding_rounds', conn, if_exists='replace', index=False)
    
    # Create indexes for better performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_company ON funding_rounds (Company)")
    if 'Date of PR' in df.columns:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON funding_rounds ([Date of PR])")
    
    # Verify creation
    count = conn.execute("SELECT COUNT(*) FROM funding_rounds").fetchone()[0]
    print(f"Database created with {count} records")
    
    conn.close()
    print(f"Database saved to {db_path}")

if __name__ == "__main__":
    create_database_from_excel()
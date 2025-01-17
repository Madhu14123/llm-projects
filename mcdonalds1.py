import sqlite3
import pandas as pd

# Load CSV data
file_path = 'mcdonalds.csv'  # Update with the exact path
data = pd.read_csv(file_path)

# Connect to SQLite database (or create it)
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Create table with columns based on the CSV headers
columns = ', '.join([f"{col} TEXT" for col in data.columns])
create_table_query = f"CREATE TABLE IF NOT EXISTS mcdonalds_data ({columns});"
cursor.execute(create_table_query)

# Insert 50 rows into the table
for _, row in data.head(50).iterrows():
    placeholders = ', '.join(['?'] * len(row))
    insert_query = f"INSERT INTO mcdonalds_data VALUES ({placeholders})"
    cursor.execute(insert_query, tuple(row))

# Commit changes and close the connection
conn.commit()
print("50 rows inserted successfully.")
conn.close()

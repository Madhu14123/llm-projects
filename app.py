from dotenv import load_dotenv
import os
import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure Google Gemini API
api_key = "AIzaSyDxWSomnXk_itGQ0Ansf7aBMZRyAsz2syM"
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config, safety_settings=safety_settings)

# Streamlit App
st.set_page_config(page_title="Gemini SQL Query App")
st.header("Generate and Execute SQL Queries with Google Gemini")

# Function to load CSV file into SQLite database
def load_csv_to_sqlite(csv_file, table_name, db):
    conn = sqlite3.connect(db)
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

# Load CSV file into database (only if the database is empty or needs updating)
db_path = 'example.db'
table_name = 'mcdonalds_data'
csv_file_path = 'mcdonalds.csv'

if not Path(db_path).is_file():
    load_csv_to_sqlite(csv_file_path, table_name, db_path)
    st.write("Database loaded with CSV data.")

# Function to generate SQL from natural language question
def generate_sql_query(question, input_prompt):
    prompt_parts = [input_prompt, question]
    response = model.generate_content(prompt_parts)
    sql_query = response.text.strip()
    return sql_query

# Function to execute SQL query and display results
def execute_sql_query(sql_query, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError as e:
        st.error(f"SQL Error: {e}")
        return None

# Define the prompt template for Gemini to convert natural language to SQL
prompt_template = """
You are an expert in converting English questions to SQL code! The SQL database has a table `mcdonalds_data` with columns: yummy, convenient, spicy, fattening, greasy, fast, cheap, tasty, expensive, healthy, disgusting, Like, Age, VisitFrequency, and Gender.
Examples:  
1. "How many people find McDonald's food tasty?" -> `SELECT COUNT(*) FROM mcdonalds_data WHERE tasty = 'Yes';`
2. "What is the average age of frequent visitors who like healthy food?" -> `SELECT AVG(Age) FROM mcdonalds_data WHERE healthy = 'Yes' AND VisitFrequency = 'frequently';`
Do not include backticks (`) or the word 'sql' in your response.
"""

# Streamlit UI for user input
question = st.text_input("Ask a question about the data:", key="input")

if st.button("Generate and Execute Query"):
    if question:
        sql_query = generate_sql_query(question, prompt_template)
        st.write(f"Generated SQL Query: {sql_query}")

        result = execute_sql_query(sql_query, db_path)
        if result:
            st.write("Query Results:")
            for row in result:
                st.write(row)
        else:
            st.write("No results found or query failed.")
    else:
        st.write("Please enter a question.")

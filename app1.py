from dotenv import load_dotenv
import os
import streamlit as st
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
st.set_page_config(page_title="Gemini Query App with CSV")
st.header("Generate and Execute Queries from CSV with Google Gemini")

# Load CSV file into a Pandas DataFrame
csv_file_path = 'mcdonalds.csv'
if not Path(csv_file_path).is_file():
    st.error(f"CSV file {csv_file_path} not found.")
else:
    df = pd.read_csv(csv_file_path)
    st.write("CSV data loaded successfully.")

# Function to generate SQL-like query from natural language question
def generate_sql_query(question, input_prompt):
    prompt_parts = [input_prompt, question]
    response = model.generate_content(prompt_parts)
    sql_query = response.text.strip()
    return sql_query

# Function to execute the query on the DataFrame
def execute_query_on_dataframe(df, sql_query):
    try:
        # Using Pandas to evaluate the query as a string expression
        result_df = df.query(sql_query)
        return result_df
    except Exception as e:
        st.error(f"Error executing query on CSV data: {e}")
        return None

# Define the prompt template for Gemini to convert natural language to SQL-like syntax compatible with Pandas
prompt_template = """
You are an expert in converting English questions to SQL-like syntax for use with a CSV dataset in Python!
The dataset has columns: yummy, convenient, spicy, fattening, greasy, fast, cheap, tasty, expensive, healthy, disgusting, Like, Age, VisitFrequency, and Gender.
Examples:  
1. "How many people find McDonald's food tasty?" -> `tasty == 'Yes'`
2. "What is the average age of frequent visitors who like healthy food?" -> `healthy == 'Yes' and VisitFrequency == 'frequently'`
Avoid SQL-specific syntax like `SELECT`, and only return conditions compatible with Python Pandas' DataFrame.query() syntax.
"""

# Streamlit UI for user input
question = st.text_input("Ask a question about the data:", key="input")

if st.button("Generate and Execute Query"):
    if question:
        sql_query = generate_sql_query(question, prompt_template)
        st.write(f"Generated Query Conditions: {sql_query}")

        # Apply query conditions directly on DataFrame
        result_df = execute_query_on_dataframe(df, sql_query)
        if result_df is not None and not result_df.empty:
            st.write("Query Results:")
            st.write(result_df)
        else:
            st.write("No results found or query failed.")
    else:
        st.write("Please enter a question.")

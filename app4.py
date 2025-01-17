from transformers import T5Tokenizer, T5ForConditionalGeneration
import sqlite3
import streamlit as st
import pandas as pd

# Load the T5 model and tokenizer
model_name = "mrm8488/t5-base-finetuned-wikiSQL"  # Pre-trained Text-to-SQL T5 model
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Function to generate SQL query using the T5 model
def generate_t5_sql(question):
    # Prepare the input for the Text-to-SQL T5 model
    input_text = "translate English to SQL: " + question
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

    # Generate SQL output
    output = model.generate(**inputs, max_new_tokens=100)
    sql_query = tokenizer.decode(output[0], skip_special_tokens=True)

    # Correct table name and map column names if necessary
    sql_query = sql_query.replace("table", "mcdonalds_data")  # Adjust table name
    return sql_query

# Function to execute SQL query on the SQLite database
def execute_sql_query(sql_query, db_path=":memory:"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        result = cursor.execute(sql_query).fetchall()
        conn.close()
        return result
    except Exception as e:
        return f"Error: {e}"

# Load McDonald's dataset and prepare SQLite database
@st.cache_data
def load_data():
    df = pd.read_csv("mcdonalds.csv")
    conn = sqlite3.connect("test.db")
    df.to_sql("mcdonalds_data", conn, index=False, if_exists="replace")
    conn.close()

# Streamlit App Configuration
st.set_page_config(page_title="T5 SQL Query App")
st.header("T5 SQL Query App for McDonald's Dataset")

# Load data into SQLite
load_data()

# User input for the question
question = st.text_input("Ask a question about the dataset:", key="input")

# Button to submit the question
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    # Generate the SQL query using the T5 model
    sql_query = generate_t5_sql(question)
    st.write(f"Generated SQL Query: {sql_query}")

    # Execute the SQL query on the dataset
    response = execute_sql_query(sql_query, "test.db")

    # Display the query results
    st.subheader("Query Results:")
    if isinstance(response, str) and response.startswith("Error"):
        st.error(response)
    elif response:
        for row in response:
            st.write(row)
    else:
        st.write("No results found.")
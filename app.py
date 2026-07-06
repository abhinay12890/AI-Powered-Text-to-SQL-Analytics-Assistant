import streamlit as st
import pymysql
from schema_extractor import get_schema
import time

from llm_pipeline import run_pipe

st.set_page_config(page_title="Text-to-SQL Assistant", layout="wide")

st.title("🗄️ Text-to-SQL Assistant")

if "conn" not in st.session_state:
    st.session_state.conn = None

if "schema" not in st.session_state:
    st.session_state.schema=""

from dotenv import load_dotenv
import os

load_dotenv()

host=os.getenv("host")
user=os.getenv("user")
password=os.getenv("password")
database=os.getenv("database")
port=os.getenv("port")

if st.session_state.conn is None:
    try:
        conn = pymysql.connect(host=host,user=user,password=password,database=database,port=int(port),connect_timeout=10)
        schema, tbl = get_schema(conn, database)
        st.session_state.conn = conn
        st.session_state.schema = schema
        st.session_state.tables = tbl
    except Exception as e:
        st.error(f"Failed: {e}")
        st.stop()

# Always render the sidebar
st.sidebar.header("Database")
st.sidebar.success("Connected")
st.sidebar.write(f"Database: {database}")
st.sidebar.write(st.session_state.tables)

# =========================
# Query Input
# =========================
st.subheader("Ask a Question")

query = st.text_area(
    "Enter your natural language query",
    placeholder="Example: Show the top 10 customers by total revenue.",
    height=120
)

run_btn = st.button("Get Results")



if run_btn:
    if query:
        start=time.time()
        with st.spinner("Analyzing..."):
            response=run_pipe(query,st.session_state.conn,st.session_state.schema)
        st.success(f"Analysis Completed in {time.time()-start} seconds..!")
        st.write(response)

    else:
        st.warning("Please enter a query.")



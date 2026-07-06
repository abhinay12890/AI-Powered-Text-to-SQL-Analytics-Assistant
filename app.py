import streamlit as st
import pymysql
from schema_extractor import get_schema
import time

from llm_pipeline import run_pipe

st.set_page_config(page_title="Text-to-SQL Assistant", layout="wide")

st.title("🗄️ Text-to-SQL Assistant")

# =========================
# Sidebar - Database Config
# =========================
st.sidebar.header("Database Configuration")

host = st.sidebar.text_input("Host", value="172.24.64.1")
port = st.sidebar.number_input("Port", value=3306, step=1)
user = st.sidebar.text_input("Username", value="abhi")
password = st.sidebar.text_input("Password", value="1289", type="password")
database = st.sidebar.text_input("Database name", value="customers")

connect_btn = st.sidebar.button("Connect")



if "conn" not in st.session_state:
    st.session_state.conn = None

if "schema" not in st.session_state:
    st.session_state.schema=""


if connect_btn:
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            connect_timeout=10
        )
        schema,tbl=get_schema(conn,database)
        if schema:
            st.sidebar.success("✅ Connected successfully and extracted schema!")
            st.session_state.conn=conn
            st.session_state.schema=schema
            st.write("Following Tables are loaded: "+"\n"+tbl)
        

    except Exception as e:
        st.sidebar.error(f"Connection failed:\n{e}")

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
        if st.session_state.conn is None:
            st.warning("Connect to database first..!!")
            st.stop()
        else:
            start=time.time()
            response=run_pipe(query,st.session_state.conn,st.session_state.schema)
            st.success(f"Analysis Completed in {time.time()-start} seconds..!")
            st.write(response)

    else:
        st.warning("Please enter a query.")



from langchain_core.prompts import ChatPromptTemplate

from prompts import generator_prompt
import streamlit as st
from schemas import SQLPlan

def query_generator(query,llm,schema):
    with st.spinner("Generating Queries...!!"):
        structured_llm=llm.with_structured_output(SQLPlan)
        plan_prompt=ChatPromptTemplate.from_template(generator_prompt)
        plan_chain=plan_prompt | structured_llm
        response=plan_chain.invoke({"query":query,"schema":schema})
    return response
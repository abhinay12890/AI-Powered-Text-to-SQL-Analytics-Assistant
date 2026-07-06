from langchain_core.prompts import ChatPromptTemplate

from prompts import validation_prompt
import streamlit as st

from schemas import ValidationResult

def query_validator(query,llm,schema,response):
    with st.spinner("Validating Queries"):
        structured_llm=llm.with_structured_output(ValidationResult)
        validation_prompt_template = ChatPromptTemplate.from_template(validation_prompt)
        validation_chain = validation_prompt_template | structured_llm
        val = validation_chain.invoke({"schema": schema, "query": query, "generated_sql": response.queries})
    return val
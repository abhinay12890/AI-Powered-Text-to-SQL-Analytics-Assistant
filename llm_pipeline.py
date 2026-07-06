
from prompts import final_prompt_template,generator_prompt
from langchain.chat_models import init_chat_model

import streamlit as st

from generator import query_generator
from validator import query_validator
from langchain_core.prompts import ChatPromptTemplate

import pandas as pd
from schemas import SQLPlan

google_api=st.secrets["google_api"]
groq_api=st.secrets["groq_api"]

gem_llm=init_chat_model("google_genai:gemini-2.5-flash",api_key=google_api)
llm=init_chat_model("groq:llama-3.1-8b-instant",api_key=groq_api)



FORBIDDEN = [
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "INSERT",
    "TRUNCATE",
    "CREATE",
    "REPLACE"
]

def run_pipe(query,conn,schema):
    results={}
    retry_response={}
    response=query_generator(query.strip(),gem_llm,schema)
    val=query_validator(query,llm,schema,response)

    if val.valid:
            with st.spinner("Executing Following Queries"):
                for x in response.queries:
                    try:
                        if any(word in x.sql.upper() for word in FORBIDDEN):
                            raise Exception("Unsafe SQL")
                        else:
                            st.code(x.sql)
                            df=pd.read_sql(x.sql,conn)
                            if len(df)>100:
                                 df=df.head(100)
                            results[x.name]=df.to_markdown()
                    except Exception as e:
                        st.error(f"Query execution failed: {e}")
    else:
        max_retries=0
        k=val.valid
        res=val.reason
        retry_prompt= "Previous Query was failed due to {reason}. Generate new query"+generator_prompt
        retry_prompt=ChatPromptTemplate.from_template(retry_prompt)
        structured_llm=gem_llm.with_structured_output(SQLPlan)
        retry_chain=retry_prompt | structured_llm

        while not k and max_retries<2:
                retry_response= retry_chain.invoke({"schema":schema,"query":query,"reason":res})
                val = query_validator(query,llm,schema,retry_response)
                k=val.valid
                res=val.reason
                max_retries+=1 
        if k:
             with st.spinner("Executing Re-written Queries.."):
                    for x in retry_response.queries:
                        try:
                            if any(word in x.sql.upper() for word in FORBIDDEN):
                                raise Exception("Unsafe SQL")
                            else:
                                st.code(x.sql)
                                df=pd.read_sql(x.sql,conn)
                                if len(df)>100:
                                     df=df.head(100)
                                results[x.name]=df.to_markdown()
                        except Exception as e:
                            st.error(f"Query execution failed: {e}")
        else:
             st.write("Invalid SQL query generated and retries exceeded")
    with st.spinner("Generating Final Report/ Insights..."):
         final_prompt=ChatPromptTemplate.from_template(final_prompt_template)
         final_chain=final_prompt | llm
         final_response=final_chain.invoke({"query":query,"results":results})
    return final_response.content

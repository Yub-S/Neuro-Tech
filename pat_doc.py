from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import streamlit as st
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain

def mapping_patient_to_doctor():
    load_dotenv()
    groq_api_key = os.environ['GROQ_API_KEY']
    huggingface_api = "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"

    # Initialize the Groq model
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

    # Initialize session state for vector storage
    if "vector" not in st.session_state:
        st.session_state.embeddings = HuggingFaceBgeEmbeddings(
            model_name="BAAI/llm-embedder",
            model_kwargs={"device": "cpu"},
            encode_kwargs={'normalize_embeddings': True}
        )
        st.session_state.loader = PyPDFLoader("doctor_schedules.pdf")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vector = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

    # Define prompt for scheduling appointments
    prompt1 = ChatPromptTemplate.from_template(
        """
        You need to match a patient's problem to a doctor based on the doctor's schedule obtained from the PDF in the context below. Provide recommendations for available doctors based on the specialty that matches the patient's problem. The specialties available are: ENT, Cardiologist, Dermatologist, etc as you can see in the context after this.
        <context>
        {context}
        </context>
        Patient's Problem: {input}
        """
    )

    st.title("Mapping Patient to Doctor")

    # Create document chain and retriever
    document_chain = create_stuff_documents_chain(llm, prompt1)
    retriever = st.session_state.vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # User input for patient's problem
    prompt2 = st.text_input("Input your prompt here")

    if prompt2:
        response = retrieval_chain.invoke({"input": prompt2})
        st.write(response['answer'])

        with st.expander("Document Similarity Search"):
            # Display relevant chunks
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("-----------------------------------")

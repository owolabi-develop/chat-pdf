from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
import os
import instructor
from pydantic import BaseModel
from langchain_community.document_loaders import (
    PyPDFLoader,
    )
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
os.environ['PINECONE_API_KEY'] = ''
api_keys = ''
index_name = "chat"
client = instructor.from_openai(OpenAI(api_key=api_keys))

embeddings =OpenAIEmbeddings(api_key=api_keys)
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
)



class PfdResponse(BaseModel):
    """
    instructor response_model class for pdf response
    
    """
    text: str 
    page: int
    source:str
    
    

def load_pdf(file_path):
    
    loader = PyPDFLoader(file_path)
    doc = text_splitter.split_documents(loader.load())
    print(".....embedding to pincone")
    vectostore = PineconeVectorStore.from_documents(doc, embeddings, index_name=index_name)
    return doc
    

def query_pdf(query):
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    results = vectorstore.similarity_search_with_relevance_scores(query, k=3)
    
    for result, _ in results:
        source_knowledge = f"text: {result.page_content},\n Page: {result.metadata['page']}, \n Source: {result.metadata['source']}"
        
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=PfdResponse,
            messages=[
                {"role": "system", "content": "You are a pdf summarizer assistant. If does not match the query description, dont generate random once just return 'No such document'."},
                {"role": "user", "content": f"using the text: \n {str(source_knowledge)} \n  to answer the query: {query}"}
            ]
        )
     

    return resp.model_dump() 


def summarize_all_pdf(query):
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    results = vectorstore.similarity_search_with_relevance_scores(query, k=3)
    
    for result, _ in results:
        source_knowledge = f"text: {result.page_content},\n Page: {result.metadata['page']}"
        
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=PfdResponse,
            messages=[
                {"role": "system", "content": "You are a pdf summarizer assistant. If query doesnt match the pdf. dont generate random once just return 'No such document'."},
                {"role": "user", "content": f"using the text: \n {str(source_knowledge)} \n  to answer the query: {query} then return a message such as Hello and welcome to this insightful PDF file following with the main summary of what the pdf document is all about "}
            ]
        )
        
        print(resp.model_dump())
     

    return resp.model_dump() 
    
    
    
    
        
    
    
    
# res = query_pdf('management to enable dietary freedom in people with type')

# res

    
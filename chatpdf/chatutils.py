from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
import os
import instructor
from pydantic import BaseModel
from langchain import hub
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from uuid import uuid4
from langchain_community.document_loaders import (
    PyPDFLoader,
    )
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
os.environ['PINECONE_API_KEY'] = ""
os.environ["OPENAI_API_KEY"] = ''
index_name = "chat"
model = ChatOpenAI(model="gpt-3.5-turbo-0125")


embeddings =OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
)
 

def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    doc = text_splitter.split_documents(loader.load())
    # Check if page number is 0 and increment if needed
    for docs in doc:
        if 'page' in docs.metadata and docs.metadata['page'] == 0:
            docs.metadata['page'] += 1
    
    print("Embedding to Pinecone:")
    vectostore = PineconeVectorStore.from_documents(doc, embeddings, index_name=index_name)
    return doc
    






## conversation rag script


## retrieve the document from pinecone vector db
vectorstore = PineconeVectorStore(index_name=index_name, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={'k': 1})

### Contextualize question ###
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    model,retriever, contextualize_q_prompt
)


system_prompt = (
    "You are an assistant for question-answering tasks over pdf documents. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, reply to the user with something related to is question and dont return the page number "
    "Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


### Statefully manage chat history ###
store = {}



def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


def rag_message(input):
    response = conversational_rag_chain.invoke(
    {"input":input},
    config={
        "configurable": {"session_id": uuid4()}
    },  # constructs a key "abc123" in `store`.
)
    
    return dict(text=response['answer'],page=int(response['context'][0].metadata['page']),source=response['context'][0].metadata['source'])



 ## summarize the uploaded document
def summarize_all_pdf(input):
   
    summarize_system_prompt = (
        "You are an assistant for summarizing tasks over pdf documents."
        "Use the following pieces of retrieved context give to you and summarize the whole of it"
        "and then return an answer say this document is talk about the related summary with the headline propbably the document title on the first page "
        "\n\n"
        "{context}"
    )

    summary_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", summarize_system_prompt),
            ("human", "{input}"),
        ]
    )


    question_answer_chain = create_stuff_documents_chain(model, summary_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input":input})
    return  dict(text=response["answer"])



    
    

    
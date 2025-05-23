
import traceback
import pandas as pd
import os
import tiktoken
from oci_util import generate_oci_gen_ai_response
import zipfile
import re
import json
import shutil
from langchain_community.embeddings import HuggingFaceEmbeddings
from PIL import Image
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores.faiss import DistanceStrategy
import os
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from oci_util import *


conversion_folder = "code_conversion_files"
userId = "deepeshT"
conversion_id = 1742586056
react_project_zip_file = f"{conversion_folder}/target_react_structure/react_project.zip"
FILE_EXCLUSIONS = ["png","jpg","jpeg","txt","md","json","xml","csv","zip","gz","tar","pdf","doc","docx","xls","xlsx","ppt","pptx","pyc","exe","dll","so","lib",
                   "obj","bin","jar","war","ear","class","vbproj","csproj","vcxproj","vcproj","filters","user","data","vspscc","sln","suo","webinfo","xsd","xslt"]
COBOL_JS_FILE_INCLUSIONS = ["cbl"]
ROUTER_FILE_FIND_STRING = "$urlRouterProvider"


def get_document_generation_prompt(source_language, file_name, code, additional_context=None):
    project_structure = "/documentation/"
    #for file in project_files: project_structure = project_structure + f"\n{file.replace(source_path,'')}"
    #file_name = file_name.replace(source_path,'')
    
    document_generation_prompt = f"""
    You are an expert COBOL software documentation generator and business analyst.  
Given the following COBOL code and project file structure, analyze and extract key information to generate a structured file-level documentation.  
The documentation should include:  

1. **File Overview**: A brief summary of the purpose and functionality of the file.  
2. **Program Structure**: Describe the COBOL program's structure, including divisions (IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE) and their roles.  
3. **Data Definitions**: Identify and document key data structures, variables, and file definitions. Include details about record layouts, data types, and any relevant schema information.  
4. **File and Database Interactions**: Extract details about file I/O operations, database queries, tables, or stored procedures used. Include schema details and access methods (e.g., sequential, indexed).  
5. **Business Logic**: Summarize the core business logic implemented in the PROCEDURE DIVISION. Highlight key operations, validations, and transformations.  
6. **External Integrations**: Mention any external systems, APIs, or libraries the program interacts with. Specify communication methods (e.g., MQ, web services, batch jobs).  
7. **Error Handling**: Describe how errors are managed, including any specific error codes, exception handling routines, or recovery mechanisms.  
8. **Performance Considerations**: Highlight any optimizations or performance-critical sections of the code.  
9. **Configuration**: Identify any configuration parameters, environment variables, or external dependencies required for execution.  
10. **Testing and Validation**: Document any built-in testing or validation routines present in the code.  
11. **Comments and Annotations**: Summarize any meaningful comments or annotations in the code that provide additional context.  

**Important Notes**:  
- Only provide documentation based on the given COBOL code and project file structure.  
- Do not generate any content outside of the provided information.  
- Ensure the documentation is detailed enough to reverse-engineer the business requirements and workflows from the code.

    """
    document_generation_prompt = f"""
    {document_generation_prompt}
    
    My Project is using {source_language} programming language.    
    Project File Structure:
    {project_structure}
    
    File Name: {file_name}
    File Content:
    {code}
    """
    return document_generation_prompt

def get_brd_generation_prompt(documentation_content):
    brd_generation_prompt = f"""
    You are an expert business analyst with deep knowledge of software architecture, system design, and business requirements gathering. 
    Based on the provided documentation of multiple files from a software project, your task is to analyze and synthesize the key business requirements that emerge from the entire project.
    Carefully examine the content to identify:
        1) Core Business Objectives: What problem is the project solving? What are the main business goals?
        2) Key Features & Functionalities: Summarize the essential capabilities the system provides.
        3) User Roles & Interactions: Identify the main users and how they interact with the system.
        4) Data Flow & Processing: Describe how data moves through the system and any critical transformations.
        5) Integration Points: Highlight dependencies on other systems or APIs.
        6) Regulatory or Compliance Requirements (if applicable).
    Use concise, structured language to generate a well-organized Business Requirement Document (BRD). 
    The output should be formatted with proper sections, bullet points, and headings to ensure clarity.
    
    Only provide documentation on given file contents and do not generate any content outside of this information provided, this is super important while generating your response.

    Here is the documentation for all files in the project:
    {documentation_content}

    Format the response in a structured html format for easy readability without any unnecessary commentary.
    """
    return brd_generation_prompt

def extract_zip_file(zip_file_path, conversion_id):
    userid = userId
    # if os.name == 'nt':
    #     os.system(f"rmdir {conversion_folder}\\{userid} /s /q")
    #     os.system(f"mkdir {conversion_folder}\\{userid}")             
    # else:
    #     os.system(f"rm -rf {conversion_folder}/{userid}")
    #     os.system(f"mkdir -p {conversion_folder}/{userid}")
    source_folder = conversion_folder + f"/{userid}/" + str(conversion_id) + "/source"
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(source_folder)
    return source_folder

def get_files_from_directory(folder_path, exclude_files = None, include_files = None, include_empty_folders = False):
    filtered_files = []
    files = [val for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(folder_path)] for val in sublist]
    for file in files:
        extension = file.split(".")[-1]
        if "." not in file or (exclude_files is None or extension not in exclude_files) and (include_files is None or extension in include_files):
            file_name = file.replace("\\","/")
            filtered_files.append(file_name)
    if include_empty_folders:
        dirs = [i[0] for i in os.walk(folder_path)]
        filtered_files = filtered_files + dirs
    return filtered_files

# create_target_project_structure("code_conversion_files\\kunalkamble85\\1742586056\\source")
# print(get_files_from_directory("code_conversion_files\\kunalkamble85\\1742586056\\target", include_empty_folders=True))


def get_number_of_tokens(file_content):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(file_content)
    return len(tokens)

def write_file(file_name, data):
    directory = os.path.dirname(file_name)  
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Writing file: {file_name}")
    f = open(file_name, "w")
    f.write(data)
    f.close()

def read_file(file_name):
    try:
        #try utf-8 encoding
        f = open(file_name, 'r')
        file_content = f.read()
    except:
        #try unicode_escape encoding
        f = open(file_name, 'r', encoding='unicode_escape')
        file_content = f.read()
    f.close()
    return file_content

def delete_existing_docs_fs(filename_check):
    vectordb = FAISS.load_local(os.path.join(DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization=True)
    ids_to_delete =[]
    for i, j in enumerate(vectordb.docstore._dict.items()):
        if j[1].metadata.get("filename") == filename_check:
            ids_to_delete.append(j[0])
    
    if ids_to_delete:
        vectordb.delete(ids=ids_to_delete)
        vectordb.save_local(os.path.join(DATA_DIR, "faiss_index"))
    else:
        print("Nothing to delete")
    return ids_to_delete

def save_to_vector_db_fs(texts, filename, override_task, file_check_status):
    if override_task and file_check_status:
        if file_check_status:
            delete_existing_docs_fs(filename_check=filename)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separators=["\n","\r\n"])
    texts = text_splitter.create_documents([texts], metadatas=[{"filename":filename}])
    
    try:
        vectordb = FAISS.load_local(os.path.join(DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization=True)
        vector_store = FAISS.from_documents(texts, embeddings)
        vectordb.merge_from(vector_store)
        pkl = vectordb.serialize_to_bytes()
        vectordb = FAISS.deserialize_from_bytes(embeddings=embeddings, serialized=pkl, allow_dangerous_deserialization=True)
        vectordb.save_local(os.path.join(DATA_DIR, "faiss_index"))
    except Exception as e:
        print(e)
        print("No database available.")
        vectordb = FAISS.from_documents(texts, embeddings)
        vectordb.save_local(os.path.join(DATA_DIR, "faiss_index"))

def update_vector_store(file_name, file_content):
    override_task = False
    file_check_status = check_file_exists_fs(file_name)
    file_exists = check_file_exists_fs(file_name)
    if file_exists:
        override_task = True
    save_to_vector_db_fs(file_content, file_name, override_task, file_check_status)

def get_all_filenames_from_vector_store():
    try:
        filenames = set()
        vectordb = FAISS.load_local(os.path.join(DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization=True)
        for i, j in vectordb.docstore._dict.items():
            filename = j.metadata.get("filename")
            if filename:
                filenames.add(filename)
        return list(filenames)
    except Exception as e:
        print(e)
        return []

def user_input(user_question, files):
    docs = search_text_fs(user_question, files)
    if len(docs)>0:
        prompt = get_prompt_template(user_question, docs)
        chat_history = []
        messages = [{"role":"user", "content": prompt}]
        messages.append({"role":"user", "content": prompt})
        response = generate_oci_gen_ai_response("meta.llama3.1-70b", messages)
        return response
    else:
        return "I don't know"
    


def check_file_exists_fs(filename_check):
    try:
        vectordb = FAISS.load_local(os.path.join(DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization=True)
        flag = False
        for i, j in enumerate(vectordb.docstore._dict.items()):
            if j[1].metadata.get("filename") == filename_check:
                flag = True
                break
        return flag
    except Exception as e:
        print(e)
        return False
    
def get_prompt_template(question, context):
    prompt_template = f"""
    You are Document Q&A or Summarizer expert. 
    Give short answers for the questions in English.
    Give answer or summary to the questions solely from only provided Text.
    Do not give any general answers apart from Text provided.
    if you can't find the answer in the provided Text just say 'I don't know'. 
    """
    prompt_template = f"""{prompt_template}
    Text:{context}
    Question:{question}
    """
    return prompt_template

def get_document_prompt_template(question, context):
    
    prompt_template = f"""
    You are an expert programmer of Cobol and an expert software documentation generator. In user_input, I would be providing you the Buiness Use Case and given the following list of files, code and documentation to extract key information in context.
Understand the context of use case and generate detailed level Business requirement documents for the provided use case.
Consider the use case as the summary and generate all the possible information using the code to include all the validations, operation and flows.

**Formatting Requirements**:  
- Only provide documentation based on the given COBOL code and project file structure.  
- The file-level documentation should be in Markdown format for easy readability.  
- Do not generate unnecessary commentary in your answer.
- if you can't find the answer in the provided Text just say 'I don't know'. 
    """
    prompt_template = f"""{prompt_template}
    Code, file and documentation:{context}
    Buiness Use Case:{question}

    output_format: Markdown format
    """
    return prompt_template

# print(os.name)
DATA_DIR = "C:\\Development\\work\\repo\\document_based_chat\\vector_database\\deepeshT"
num_results = 5
os.makedirs(DATA_DIR, exist_ok=True)

def is_file_processed(filename):
    return os.path.exists(os.path.join(DATA_DIR, filename))

def search_text_fs(question, filename):
    vectordb = FAISS.load_local(os.path.join(
        DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization = True, distance_strategy = DistanceStrategy.COSINE)
    data = []
    vectordb.index.distance_measure = "cosine"

    if filename == ["All"]:
        results = vectordb.similarity_search_with_score(query=question, k=num_results)
    else:
        results = vectordb.similarity_search_with_score(query=question, k=num_results, filter={"filename":filename})
    print(results)
    for doc, score in results:
        if score < 0.99 or True:
            data.append(f"""filename: {doc.metadata.get('filename')}, content: {doc.page_content}""")
    return data

def search_document(user_question, files):
    vectordb = FAISS.load_local(os.path.join(
        DATA_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization = True, distance_strategy = DistanceStrategy.COSINE)
    data = []
    vectordb.index.distance_measure = "cosine"

    if files == ["All"]:
        results = vectordb.similarity_search_with_score(query=user_question, k=num_results)
    else:
        results = vectordb.similarity_search_with_score(query=user_question, k=num_results, filter={"filename":files})
    print(results)
    docs = []
    for doc, score in results:
        if score < 0.99 or True:
            filename = doc.metadata.get('filename')
            file_content = read_file(filename)
            data.append(f"""filename: {filename}, documentation: {doc.page_content}, code: {file_content}""")
    #print(data)
    print(f"data: {data}")
    #docs = search_text_fs(user_question, files)
    if len(data)>0:
        prompt = get_document_prompt_template(user_question, docs)
        chat_history = []
        messages = [{"role":"user", "content": prompt}]
        messages.append({"role":"user", "content": prompt})
        response = generate_oci_gen_ai_response("meta.llama3.1-70b", messages)
        return response
    else:
        return "I don't know"

source_zip_file = "C:/Users/dtejwani/Downloads/cics-genapp-main.zip"
source_folder = extract_zip_file(source_zip_file, 1)
#get all the cbl files in a list from source folder
project_files = get_files_from_directory(source_folder, exclude_files=FILE_EXCLUSIONS, include_files=COBOL_JS_FILE_INCLUSIONS, include_empty_folders=True)
#get first file from the list which has extension cbl
project_files = [file for file in project_files if file.endswith(".cbl")]
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5", encode_kwargs = {"normalize_embeddings": True})
#Uncomment the below for loop to generate documentation for all the files in the project_files list
###for file_name in project_files:
    ###print(file_name)
    #get the file name from the path
    ###file_nameExt = file_name.split("/")[-1]
    #read content of the file
    ###file_content = read_file(file_name)
    #print content of the file
    ###print(file_content)
    ###document_generation_prompt = get_document_generation_prompt("COBOL",file_name,file_content,"Documentation will be used to generate Application worflow via RAG in future")
    ###response = generate_oci_gen_ai_response("meta.llama3.1-70b", [{"role":"user", "content": document_generation_prompt}])
    ###print(f"response:{response}")
    #write the response in DATA_DIR to a markdown format file with 
    #contacatenate value from varirable file_name and .md in fucntion write_file(os.path.join(DATA_DIR, file_nameExt".md"), response)
    ###write_file(os.path.join(DATA_DIR, file_nameExt+".md"), response)
    #break the loop after first iteration
    #update the vector store with the file name and response    
    ###update_vector_store(file_name, response)
    #break the loop after first iteration
    ###update_vector_store(file_name, response)
###file_name = project_files[2]
###print(file_name)
#get the file name from the path
###file_nameExt = file_name.split("/")[-1]
###embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5", encode_kwargs = {"normalize_embeddings": True})
#read content of the file
###file_content = read_file(file_name)
#print content of the file
###print(file_content)
###document_generation_prompt = get_document_generation_prompt("COBOL",file_name,file_content,"Documentation will be used to generate Application worflow via RAG in future")
###response = generate_oci_gen_ai_response("meta.llama3.1-70b", [{"role":"user", "content": document_generation_prompt}])
###print(f"response:{response}")
#write the response in DATA_DIR to a markdown format file with 
#contacatenate value from varirable file_name and .md in fucntion write_file(os.path.join(DATA_DIR, file_nameExt".md"), response)
###write_file(os.path.join(DATA_DIR, file_nameExt+".md"), response)
###update_vector_store(file_name, response)
fileslist = get_all_filenames_from_vector_store()
userResponse = search_document("Run SSP3 to create a house insurance policy", fileslist)
print(userResponse)



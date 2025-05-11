
import traceback
import pandas as pd
from oci_util import generate_oci_gen_ai_response
import streamlit as st
import os
import tiktoken
# from utils.oci_utils import generate_oci_gen_ai_response
import zipfile
import re
import json
import shutil
import requests
import json

conversion_folder = "code_conversion_files"
react_project_zip_file = f"{conversion_folder}/target_react_structure/react_project.zip"
FILE_EXCLUSIONS = ["png","jpg","jpeg","txt","md","json","xml","csv","zip","gz","tar","pdf","doc","docx","xls","xlsx","ppt","pptx","pyc","exe","dll","so","lib",
                   "obj","bin","jar","war","ear","class","vbproj","csproj","vcxproj","vcproj","filters","user","data","vspscc","sln","suo","webinfo","xsd","xslt"]
ANGULER_JS_FILE_INCLUSIONS = ["png","jpg","jpeg","ts","js","html","css","xml","csv"]
ROUTER_FILE_FIND_STRING = "$urlRouterProvider"

def get_document_generation_prompt(source_path, source_language, project_files, file_name, code):
    project_structure = ""
    for file in project_files: 
        project_structure = project_structure + f"\n{file.replace(source_path,'')}"
    file_name = file_name.replace(source_path,'')
    
    document_generation_prompt = f"""
    You are an expert software documentation generator. 
    Given the following code and project file structure, analyze and extract key information to generate a structured file-level documentation. 
    The documentation should include:
    File Overview: A brief summary of the purpose and functionality of the file.
    UI Components (if applicable): List any frontend components, frameworks, or libraries used. Describe their role and interactions.
    Services & APIs (if applicable): Identify any internal or external services the file interacts with. Specify API endpoints, HTTP methods, request/response structures, and key functionalities.
    Database Interactions (if applicable): Extract details about database queries, tables, stored procedures, or ORM models used. Include schema details if possible.
    Other Integrations (if applicable): Mention any third-party libraries, messaging queues, authentication mechanisms, or infrastructure dependencies involved.
    Key Functions & Classes: Summarize the core functions, classes, and business logic present in the file. Provide a high-level explanation of their roles.
    Configuration & Environment Variables: Identify any configurations, feature flags, or environment variables required for execution.
    Error Handling & Logging: Describe how errors are managed and how logging is implemented.
    Format the response in a structured html format for easy readability.
    Only provide documentation on given file contents and do not generate any content outside of this information provided, this is super important while generating your response.
    """
    if "additional_context" in st.session_state:
        document_generation_prompt = document_generation_prompt + f"\nAdditional Context: {st.session_state.additional_context}"

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

def get_ang_to_react_code_conversion_prompt(source_path, file_name, source_project_files, target_path, target_project_files, code):
    source_project_structure = ""
    for file in source_project_files: source_project_structure = source_project_structure + f"\n{file.replace(source_path,'')}"
    target_project_structure = ""
    for file in target_project_files: target_project_structure = target_project_structure + f"\n{file.replace(target_path,'')}"
    
    file_name = file_name.replace(source_path,'')
    
    code_converion_prompt = f"""
    You are an expert in JavaScript frameworks, specializing in converting AngularJS applications to ReactJS. 
    Given the following inputs:
        1) AngularJS Project Folder Structure
        2) ReactJS Project Folder Structure
        3) Current AngularJS File Name
        4) AngularJS Code to Convert

    Analyze the provided details and generate an accurate ReactJS equivalent. 
    The output should include:
        1) Target File Name: Determine the appropriate file name for the converted ReactJS file, following ReactJS naming conventions. Embed it into <target_file_name></target_file_name> tag
        2) Target Folder Path: Identify the correct location within the ReactJS project structure to place the converted file, maintaining modularity and best practices. Embed it into <target_folder_path></target_folder_path> tag
        3) Converted ReactJS Code: Transform the given AngularJS code into a functionally equivalent ReactJS version.  Start and end it with <converted_code></converted_code> but return formatted code.
    
    Assume that other files will be converted too, so just give conversion for this file.
    Do not give extra commentary, just give what is asked for.
    All other files which returns react component (for example 'export default <component_name>') in the code must have .jsx extension in the file name.    
    main.jsx and App.jsx files are special files. These two files suppose to be in /src folder of project.
    If file is already present in the ReactJS project, suggest different target_file_name with jsx extension as per AnjularJS folder structure understanding.

    Ensure adherence to modern React best practices, including:
        -> Using functional components with hooks (if applicable).
        -> Replacing AngularJS-specific concepts (e.g., $scope, directives, services) with React equivalents.
        -> Handling state and side effects with useState, useEffect, or other appropriate hooks.
        -> Converting routing ($routeProvider/ui-router) to React Router.
        -> Migrating API calls ($http, $resource) to fetch or axios.
        -> Ensuring proper integration with context, Redux, or other state management solutions if needed.
        -> Maintaining modularity and reusability in the ReactJS code structure.
        -> Provide the response in a structured format to facilitate direct integration into the ReactJS project.
        -> When converting serivces, create service Class with methods which can be consumed by React components.
    """
    if "additional_context" in st.session_state:
        code_converion_prompt = code_converion_prompt + f"\nAdditional Context: {st.session_state.additional_context}"

    code_converion_prompt = f"""
    {code_converion_prompt}
    
    AngularJS Project Folder Structure:
    {source_project_structure}

    ReactJS Project Folder Structure:
    /react_project/src/components
    /react_project/src/contexts
    /react_project/src/services
    /react_project/src/utils
    /react_project/src/pages
    /react_project/src/hooks
    /react_project/src/assets
    
    Current AngularJS File Name: {file_name}
    AngularJS Code to Convert:
    {code}
    """
    return code_converion_prompt

def get_view_controller_conversion_prompt(source_path, view_file_name, controller_file_name, source_structure, target_path, target_structure, route_file):
    view_content = read_file(view_file_name)
    controller_content = read_file(controller_file_name)
    router_content = read_file(route_file)

    view_file_name = view_file_name.replace(source_path,'')
    controller_file_name = controller_file_name.replace(source_path,'')
    source_project_structure = ""
    for file in source_structure: source_project_structure = source_project_structure + f"\n{file.replace(source_path,'')}"
    target_project_structure = ""
    for file in target_structure: target_project_structure = target_project_structure + f"\n{file.replace(target_path,'')}"

    view_controller_conversion_prompt = f"""
    I have an AngularJS project that I am migrating to ReactJS. I will provide the following inputs:
        1) AngularJS View (HTML file)
        2) AngularJS Controller (JS file)
        3) Source folder structure of the AngularJS project
        4) Target folder structure of the ReactJS project
        5) ReactJS route configuration file

    Using these inputs, generate a ReactJS component that preserves the original functionality and UI while following modern React best practices.

    Conversion Expectations:
    Transform the AngularJS template (HTML) into a ReactJS JSX structure.
    Convert the AngularJS controller logic into React hooks (useState, useEffect, useContext, etc.) or React class components (if needed).
    Ensure state management is handled properly (use React Context, Redux, or local state as applicable).
    Replace AngularJS directives (ng-if, ng-repeat, etc.) with equivalent React implementations (map, conditional rendering, etc.).
    Use functional components with hooks unless a class component is necessary.
    Preserve event handling and API calls.
    Maintain component-based architecture, ensuring modularity and reusability.
    Place the new ReactJS component in the correct target folder as per the provided folder structure.
    Please use useNavigate instead of useHistory for routing in ReactJS.

    Input Files:
    AngularJS View (HTML)File Name: {view_file_name}
    File Contents:
    {view_content}

    AngularJS Controller (JS) File Name: {controller_file_name}
    File Contents: 
    {controller_content}

    ReactJS Route Configuration File: 
    {router_content}

    Source Folder Structure: 
    {source_project_structure}

    Target Folder Structure:
    /react_project/src/components
    /react_project/src/contexts
    /react_project/src/services
    /react_project/src/utils
    /react_project/src/pages
    /react_project/src/hooks
    /react_project/src/assets

    Expected Output:
    A fully functional ReactJS component file that correctly replaces the AngularJS implementation. Do not generate unnecessary commentary.
    The output should only include:
        1) Target File Name: Determine the appropriate .jsx file name for the converted ReactJS file, following ReactJS naming conventions. Embed it into <target_file_name></target_file_name> tag
        2) Target Folder Path: Identify the correct location within the ReactJS project structure to place the converted file, maintaining modularity and best practices. Embed it into <target_folder_path></target_folder_path> tag
        3) Converted ReactJS Code: Transform the given AngularJS code into a functionally equivalent ReactJS version.  Start and end it with <converted_code></converted_code> but return formatted code.
    """
    return view_controller_conversion_prompt

def get_routing_information_prompt(files_to_process):
    file_content = None
    found_route = False
    for file in files_to_process: 
        file_content = read_file(file)
        if ROUTER_FILE_FIND_STRING in file_content:  
            found_route = True
            print(f"Found route in file: {file}")
            break
    if not found_route: return None, None, None
    routing_information_prompt = f"""
    I am providing you the routing information about my angularJS project, extract the URL details in json format.
    Do not provide any unnecessary commentary.
    Use below keys for information:
            1) State
            2) URL
            3) View_Path
            4) Controller

    File_Content:
    {file_content}
    """
    return file, file_content, routing_information_prompt

def get_routing_information_prompt(files_to_process):
    userid = st.session_state.userid
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

def create_target_project_structure(source_folder):
    print(f"source_folder:{source_folder}")    
    # target_folder = source_folder.replace(\\source,\\target)
    target_folder = source_folder.replace("/source","/target")
    # if os.name == 'nt':        
    #     os.system(f"rmdir {target_folder}\\react_project /s /q")      
    # else:        
    #     os.system(f"rm -rf {target_folder}/react_project")
    with zipfile.ZipFile(react_project_zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
    print(f"target_folder:{target_folder}")
    return target_folder

def create_zip_file(target_folder, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zip_ref:
        for root, dirs, files in os.walk(target_folder):
            for file in files:
                zip_ref.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(target_folder, '..')))
    return zip_file_name

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

# def generate_analysis_report(source_folder):
#     print(f"Started generating analysis report for source folder: {source_folder}")
#     files_to_process = get_files_from_directory(source_folder, exclude_files=FILE_EXCLUSIONS, include_files=None)
#     # print(f"files_to_process:{files_to_process}")
#     if len(files_to_process) == 0:
#         st.error("No files found in the source folder")
#     sample_path = files_to_process[0]
#     package_name = sample_path.replace(source_folder+"/","").split("/")[0]
#     print(f"package_name:{package_name}")
#     errors = []
#     df = pd.DataFrame(columns=['file_path', 'package', 'num_lines', 'num_lines(no_doc)', 'tokens', 'tokens(no_doc)'])
#     data_counter = 0
#     placeholder = st.empty()
#     with placeholder:
#         for file_name in files_to_process:
#             try:
#                 st.write(f"Processing file: {file_name}")
#                 print(f"Processing file {file_name}")
#                 file_content = read_file(file_name)
#                 total_tokens = get_number_of_tokens(file_content)
#                 tokens_without_comments_content = ""
#                 tokens_without_comments = number_of_lines = 0
#                 number_of_lines_without_comments = 0
#                 with open(file_name, 'r') as file:
#                     for line in file:
#                         number_of_lines = number_of_lines + 1
#                         if not line.startswith("#") and line.strip()!="" and not line.startswith("//"):
#                             number_of_lines_without_comments = number_of_lines_without_comments + 1
#                             tokens_without_comments_content = tokens_without_comments_content + line
#                 tokens_without_comments = get_number_of_tokens(tokens_without_comments_content)                
#                 df.loc[data_counter] = [file_name, package_name, number_of_lines, number_of_lines_without_comments, total_tokens, tokens_without_comments]
#                 data_counter+= 1
#             except Exception as e:
#                 print(e)
#                 print(traceback.format_exc())
#                 errors.append(file_name)
#                 # break
#             placeholder.empty()
#         print(f"errors:{errors}")
#         print(f"Completed generating analysis report for source folder: {source_folder}")
#         return df



def get_files_from_database(project_id):
    url = f"https://apex.oraclecorp.com/pls/apex/tieaicckk/userrequestdetails/?q={{\"user_request_id\":\"{project_id}\"}}"
    print(url)
    res = requests.get(url)
    file_details=[]
    parsed_data = json.loads(res.content)

    if len(parsed_data) != 0:
        for iter in range (len(parsed_data["items"])):
            file_details.append({"file_name":parsed_data["items"][iter]['file_name'],"file_content":parsed_data["items"][iter]["file_content"]})
    else:
        print("Failed to retrieve data ", {res.status_code})
        return {}
    return file_details
    # return [{"file_name": 'ea-bank/src/test_controller.js', "file_content":'import { Component } from' },{"file_name": 'ea-bank/src/test213_controller.js', "file_content":"export class AppComponent {\ntitle = 'angular-app';" }]

def generate_analysis_report(project_id):
    print(f"Started generating analysis report for source folder: {project_id}")
    files_to_process = get_files_from_database(project_id) #{{'file_name': "ea-bank/src/test_controller.js", "file_content":"import { Component } from '@angular/core'" }}
    if len(files_to_process) == 0:
        st.error("No files found in the Project ID - ",project_id)
    package_name = files_to_process[0]['file_name'].split("/")[0]
    print(f"package_name:{package_name}")
    errors = []
    df = pd.DataFrame(columns=['file_path', 'package', 'num_lines', 'num_lines(no_doc)', 'tokens', 'tokens(no_doc)'])
    data_counter = 0
  
    for file in files_to_process:
        try:
            # st.write(f"Processing file: {file['file_name']}")
            print(f"Processing file {file['file_name']}")
            file_content = file['file_content']
            total_tokens = get_number_of_tokens(file_content)
            tokens_without_comments_content = ""
            tokens_without_comments = number_of_lines = 0
            number_of_lines_without_comments = 0
            for line in file_content:
                number_of_lines = number_of_lines + 1
                if not line.startswith("#") and line.strip()!="" and not line.startswith("//"):
                    number_of_lines_without_comments = number_of_lines_without_comments + 1
                    tokens_without_comments_content = tokens_without_comments_content + line
            tokens_without_comments = get_number_of_tokens(tokens_without_comments_content)                
            df.loc[data_counter] = [file['file_name'], package_name, number_of_lines, number_of_lines_without_comments, total_tokens, tokens_without_comments]
            data_counter+= 1
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            errors.append(file['file_name'])
    print(df.shape)
    # print(df.to_json(orient='records'))
    return df.to_json(orient='records')

# def generate_documentation_report(source_folder, source_language):
#     test_mode = st.session_state.test_mode
#     print(f"Started generating documentation report for source folder: {source_folder}")
#     files_to_process = get_files_from_directory(source_folder, exclude_files=FILE_EXCLUSIONS, include_files=None)
#     if len(files_to_process) == 0:
#         st.error("No files found in the source folder")
#     sample_path = files_to_process[0]
#     package_name = sample_path.replace(source_folder+"/","").split("/")[0].replace("-master","")
#     print(f"package_name:{package_name}")
#     errors = []
#     df = pd.DataFrame(columns=["File_Path", "Documentation_Path", "SUCCESS", "ERROR"])
#     data_counter = 0
#     placeholder = st.empty()
#     documentation_content = ""
#     with placeholder:
#         for file_name in files_to_process:
#             st.write(f"Processing file: {file_name}")
#             print(f"Processing file {file_name}")
#             file_content = read_file(file_name)
#             try:
#                 document_generation_prompt = get_document_generation_prompt(source_folder, source_language, files_to_process, file_name, file_content)
#                 response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": document_generation_prompt}])                
#                 target_file = file_name.replace("/source/","/target/documentation/")                
#                 if "." in target_file:
#                     extension = target_file.split(".")[-1]
#                     target_file = target_file.replace(f".{extension}","_documentation.html")
#                 else:
#                     target_file = target_file + "_documentation.html"

#                 print(f"target_file:{target_file}")
#                 write_file(f"{target_file}", response)   
#                 documentation_content = documentation_content + f"\nFile:{target_file}\nHTML Content of file:\n{response}"     
#                 df.loc[data_counter] = [file_name, target_file, True, None]
#                 data_counter+= 1
#             except Exception as e:
#                 error = str(e)
#                 print(traceback.format_exc())
#                 df.loc[data_counter] = [file_name, None, False, error]
#                 data_counter+= 1
#                 errors.append(file_name)
#             placeholder.empty()
#             if test_mode and data_counter == 1:
#                 break
#         brd_generation_prompt = get_brd_generation_prompt(documentation_content)
#         response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": brd_generation_prompt}])      
#         write_file(f'{source_folder.replace("/source","/target/documentation")}/BRD.html', response)
#         print(f"errors:{errors}")
#         print(f"Completed generating documentation report for source folder: {source_folder}")
#         return df

def generate_documentation_report(project_id, source_language):
    files_to_process = get_files_from_database(project_id) #{{'file_name': "ea-bank/src/test_controller.js", "file_content":"import { Component } from '@angular/core'" }}
    if len(files_to_process) == 0:
        st.error("No files found in the Project ID - ",project_id)
    package_name = files_to_process[0]['file_name'].split("/")[0]
    print(f"package_name:{package_name}")
    errors = []
    df = pd.DataFrame(columns=["File_Path", "Documentation_Path", "SUCCESS", "ERROR"])
    data_counter = 0
    documentation_content = ""
    for file in files_to_process:
        file_content = file['file_content']
        source_folder = "/".join("ea-bank/config/test.config".split('/')[:-1])
        try:
            document_generation_prompt = get_document_generation_prompt(source_folder, source_language, files_to_process, file['file_name'], file_content)
            response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": document_generation_prompt}])                
            target_file = file['file_name'].replace("/source/","/target/documentation/")                
            if "." in target_file:
                extension = target_file.split(".")[-1]
                target_file = target_file.replace(f".{extension}","_documentation.html")
            else:
                target_file = target_file + "_documentation.html"

            print(f"target_file:{target_file}")
            write_file(f"{target_file}", response)   
            documentation_content = documentation_content + f"\nFile:{target_file}\nHTML Content of file:\n{response}"     
            df.loc[data_counter] = [file['file_name'], target_file, True, None]
            data_counter+= 1
        except Exception as e:
            error = str(e)
            print(traceback.format_exc())
            df.loc[data_counter] = [file['file_name'], None, False, error]
            data_counter+= 1
            errors.append(file['file_name'])
    brd_generation_prompt = get_brd_generation_prompt(documentation_content)
    response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": brd_generation_prompt}])      
    write_file(f'{source_folder.replace("/source","/target/documentation")}/BRD.html', response)
    print(f"errors:{errors}")
    print(f"Completed generating documentation report for source folder: {source_folder}")
    return df.to_json(orient='records')

def __get_details_from_repsonse(response):
    target_file_name = re.search(r"<target_file_name>(.*?)</target_file_name>", response, re.DOTALL)
    if target_file_name:
        target_file_name =  target_file_name.group(1)
    print(target_file_name) # AccountCtrl.jsx

    target_folder_path = re.search(r"<target_folder_path>(.*?)</target_folder_path>", response, re.DOTALL)
    if target_folder_path:
        target_folder_path =  target_folder_path.group(1)
    print(target_folder_path) # AccountCtrl.jsx

    converted_code = re.search(r"<converted_code>(.*?)</converted_code>", response, re.DOTALL)
    if converted_code:
        converted_code =  converted_code.group(1)
    # print(converted_code) 
    return target_file_name, target_folder_path, converted_code

def __run_copy(src, dst):
    print(f"Copying file from {src} to {dst}")
    print(f"Copied:" + shutil.copy(src, dst))

def get_view_controller_info(files_to_process, routing_information):
    print(f"routing_information:{routing_information}")
    view_controller_mapping = {}
    for route_info in routing_information:
        view_path =  route_info["View_Path"]
        controller = route_info["Controller"]
        controller = controller.replace("Ctrl", "")
        gotController = False
        gotView = False
        for file in files_to_process:
            fname = file.split("/")[-1]
            if "controller" in file and controller in fname:
                controller = file
                gotController = True
                break
        for file in files_to_process:
            if file.endswith(view_path):
                view_path = file
                gotView = True
                break
        if gotController and gotView:
            view_controller_mapping[view_path] = controller
    print(f"view_controller_mapping:{view_controller_mapping}")
    return view_controller_mapping

def generate_route_file(source_folder, files_to_process, target_folder, target_folder_structure):
    route_file, route_file_content, routing_information_prompt = get_routing_information_prompt(files_to_process)
    view_controller_info ={}
    if route_file is not None:
        response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": routing_information_prompt}])  
        response = response.replace("```json","").replace("```","")
        routing_information = json.loads(response)
        view_controller_info = get_view_controller_info(files_to_process, routing_information)    
        code_converion_prompt = get_ang_to_react_code_conversion_prompt(source_folder, route_file, files_to_process, target_folder, target_folder_structure, route_file_content)
        response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": code_converion_prompt}])                                     
        _, _, converted_code = __get_details_from_repsonse(response)
        target_file_to_create = target_folder + "/react_project/src/App.jsx"
        target_file_to_create = target_file_to_create.replace("\\","/").replace("//","/").replace("/\\","/")
        print(f"target_file_to_create:{target_file_to_create}")
        write_file(f"{target_file_to_create}", converted_code.replace("```javascript","").replace("```","").replace("```jsx","").replace("```","").replace("jsx",""))
    return route_file, target_file_to_create,view_controller_info

def handle_view_controller_files(view_controller_info, source_path, source_structure, target_folder, target_structure, route_file):
    placeholder = st.empty()
    output = []
    errors = []
    test_mode = st.session_state.test_mode  
    with placeholder:
        for view_file_name, controller_file_name in view_controller_info.items():
            st.write(f"Processing view file: {view_file_name}, controller_file:{controller_file_name}")
            print(f"Processing view file: {view_file_name}, controller_file:{controller_file_name}")            
            try:
                view_controller_conversion_prompt = get_view_controller_conversion_prompt(source_path, view_file_name, controller_file_name, source_structure, target_folder, target_structure, route_file)
                print(f"code_converion_prompt:{view_controller_conversion_prompt}")
                response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": view_controller_conversion_prompt}])                                     
                target_file_name, target_folder_path, converted_code = __get_details_from_repsonse(response)
                target_file_to_create = target_folder + "/" + target_folder_path + "/" + target_file_name
                target_file_to_create = target_file_to_create.replace("\\","/").replace("//","/").replace("/\\","/")
                print(f"target_file_to_create:{target_file_to_create}")
                write_file(f"{target_file_to_create}", converted_code.replace("```javascript","").replace("```","").replace("```jsx","").replace("```","").replace("jsx",""))      
                output.append([view_file_name, target_file_to_create, True, None])
                output.append([controller_file_name, target_file_to_create, True, None])
                target_structure.append(target_folder_path + "/" + target_file_name)                
            except Exception as e:      
                error = str(e)          
                print(traceback.format_exc())
                errors.append(view_file_name)
                errors.append(controller_file_name)
                output.append([view_file_name, None, False, error])
                output.append([controller_file_name, None, False, error])
            placeholder.empty()
            if test_mode:
                break
    return output, errors, target_structure

def generate_conversion_report(source_folder, source_lang, target_lang):
    print(f"Started converting code from: {source_lang} to {target_lang} for source folder: {source_folder}")
    if source_lang != "AngularJS" or target_lang != "ReactJS":
        st.error("Invalid source or target language selected. Please select AngularJS as source and ReactJS as target language.")
        st.stop()
    target_folder = create_target_project_structure(source_folder)
    test_mode = st.session_state.test_mode    
    files_to_process = get_files_from_directory(source_folder, exclude_files=None, include_files=ANGULER_JS_FILE_INCLUSIONS)
    if len(files_to_process) == 0:
        st.error("No files found in the source folder")    
        st.stop()
    target_folder_structure = get_files_from_directory(target_folder, exclude_files=None, include_files=ANGULER_JS_FILE_INCLUSIONS, include_empty_folders=True)
    route_file, target_file_to_create, view_controller_info = generate_route_file(source_folder, files_to_process, target_folder, target_folder_structure)
    data_counter = 0
    errors = []
    df = pd.DataFrame(columns=["Source_Path", "Target_Path", "SUCCESS", "ERROR"])    
    print(f"Before files_to_process size:{len(files_to_process)}")
    if route_file is not None:
        target_folder_structure.append(route_file)
        files_to_process.remove(route_file)
        df.loc[data_counter] = [route_file, target_file_to_create, True, None]
        data_counter+= 1
        output, errors, target_folder_structure = handle_view_controller_files(view_controller_info, source_folder, files_to_process, target_folder, target_folder_structure, route_file)
        for item in output:
            df.loc[data_counter] = item
            data_counter+= 1
            print(f"Removing file: {item[0]}")
            files_to_process.remove(item[0])
    print(f"After files_to_process size:{len(files_to_process)}")
    # return target_folder, df
    placeholder = st.empty()
    files_to_not_override = ["App.jsx","main.jsx","index.html","package.json","vite.config.js"]
    with placeholder:
        for file_name in files_to_process:
            try:
                st.write(f"Processing file: {file_name}")
                print(f"Processing file {file_name}")
                if  "/tests/" in file_name: 
                    print(f"Skipping test file: {file_name}")
                    continue
                extension = file_name.split(".")[-1]
                f_name = file_name.split("/")[-1]
                files_to_copy = ["png","jpg","jpeg","css","xml","csv","json"]
                if extension in files_to_copy:
                    target_file_to_create = f"{target_folder}/react_project/src/assets/{f_name}"                    
                    __run_copy(file_name, target_file_to_create)                
                else:                                      
                    file_content = read_file(file_name)
                    code_converion_prompt = get_ang_to_react_code_conversion_prompt(source_folder, file_name, files_to_process, target_folder, target_folder_structure, file_content)
                    print(f"code_converion_prompt:{code_converion_prompt}")
                    response = generate_oci_gen_ai_response(st.session_state.LLM_MODEL, [{"role":"user", "content": code_converion_prompt}])                                     
                    target_file_name, target_folder_path, converted_code = __get_details_from_repsonse(response)
                    if target_file_name in files_to_not_override:   target_file_name = f"{target_file_name}_{data_counter}.jsx"
                    target_file_to_create = target_folder + "/" + target_folder_path + "/" + target_file_name
                    target_file_to_create = target_file_to_create.replace("\\","/").replace("//","/").replace("/\\","/")
                    write_file(f"{target_file_to_create}", converted_code.replace("```javascript","").replace("```","").replace("```jsx","").replace("```","").replace("jsx",""))      
                    target_folder_structure.append(target_folder_path + "/" + target_file_name)
                    print(f"target_file_to_create:{target_file_to_create}")
                                
                df.loc[data_counter] = [file_name, target_file_to_create, True, None]                
                data_counter+= 1
            except Exception as e:
                error = str(e)
                print(traceback.format_exc())
                df.loc[data_counter] = [file_name, None, False, error]
                data_counter+= 1
                errors.append(file_name)
            placeholder.empty()
            if test_mode and data_counter >= 1:
                break
        print(f"errors:{errors}")
        print(f"Completed converting code from: {source_lang} to {target_lang} for source folder: {source_folder}")
        return target_folder, df
from io_utils import read_file
import logging

ROUTER_FILE_FIND_STRING = "$urlRouterProvider"

def get_document_generation_prompt(source_language, files_to_process, file_name,  file_content, additional_context):
    project_structure = ""
    for _, (file, _) in files_to_process.items():
        project_structure = project_structure + f"\n{file}"
    
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
    Format the response in a structured Markdown format for easy readability.
    Only provide documentation on given file contents and do not generate any content outside of this information provided, this is super important while generating your response.
    """
    if additional_context: document_generation_prompt = document_generation_prompt + f"\nAdditional Context: {additional_context}"

    document_generation_prompt = f"""
    {document_generation_prompt}
    
    My Project is using {source_language} programming language.    
    Project File Structure:
    {project_structure}
    
    File Name: {file_name}
    File Content:
    {file_content}
    """
    return document_generation_prompt

def get_brd_generation_prompt(documentation_content, component):
    brd_generation_prompt = f"""
    You are an expert business analyst with deep knowledge of software architecture, system design, and business requirements gathering. 
    Based on the provided documentation of multiple files from a software project, your task is to analyze and synthesize the key business requirements that emerge from the entire project.
    Carefully examine the content to identify:
    {component}

    Use detailed, structured language to generate a well-organized Business Requirement Document (BRD). 
    The output should be formatted with proper sections, bullet points, and headings to ensure clarity.
    
    Only provide documentation on given file contents and do not generate any content outside of this information provided, this is super important while generating your response.

    Here is the documentation for all files in the project:
    {documentation_content}

    Format the response in a structured Markdown format for easy readability without any unnecessary commentary.
    """
    return brd_generation_prompt


def get_user_stories_generation_prompt(documentation_content):
    template = f"""
        You are an certified product owner of Agile Scrum methodology and you know how to write perfect User Story for Agile Scrum process. 
        I would be providing you the Buiness Use Case. Understand the context of use case and generate User Stories.
        Format the response in a structured Markdown format for easy readability without any unnecessary commentary.
        Do not generate unnecessary commentary in your answer.
        Only generate functional User Stories nothing else.
        Buiness Use Case:
        {documentation_content}
    """
    return template



def get_ang_to_react_code_conversion_prompt(files_to_process, file_name,  file_content, additional_context):
    project_structure = ""
    for _, (file, _) in files_to_process.items():
        project_structure = project_structure + f"\n{file}"
    
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

    code_converion_prompt = code_converion_prompt + f"\nAdditional Context: {additional_context}"

    code_converion_prompt = f"""
    {code_converion_prompt}
    
    AngularJS Project Folder Structure:
    {project_structure}

    ReactJS Project Folder Structure:
    react_project/src/components
    react_project/src/contexts
    react_project/src/services
    react_project/src/utils
    react_project/src/pages
    react_project/src/hooks
    react_project/src/assets
    
    Current AngularJS File Name: {file_name}
    AngularJS Code to Convert:
    {file_content}
    """
    return code_converion_prompt

# files_to_process, view_file_name, controller_file_name, SAMPLE_REACT_PROJECT_PATH, target_folder_structure, route_file, route_file_content
def get_view_controller_conversion_prompt(files_to_process, target_folder_structure, view_file_name, controller_file_name, route_file_content, file_objects):
    for item in file_objects:
        file_name = item["file_name"]
        if file_name == view_file_name: view_content = item["file_content"]
        if file_name == controller_file_name: controller_content = item["file_content"]
    
    source_project_structure = ""
    for _, (file_name, _) in files_to_process.items():
        source_project_structure = source_project_structure + f"\n{file_name}"
    target_project_structure = ""
    for file in target_folder_structure: target_project_structure = target_project_structure + f"\n{file}"

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
    {route_file_content}

    Source Folder Structure: 
    {source_project_structure}

    Target Folder Structure:
    react_project/src/components
    react_project/src/contexts
    react_project/src/services
    react_project/src/utils
    react_project/src/pages
    react_project/src/hooks
    react_project/src/assets

    Expected Output:
    A fully functional ReactJS component file that correctly replaces the AngularJS implementation. Do not generate unnecessary commentary.
    The output should only include:
        1) Target File Name: Determine the appropriate .jsx file name for the converted ReactJS file, following ReactJS naming conventions. Embed it into <target_file_name></target_file_name> tag
        2) Target Folder Path: Identify the correct location within the ReactJS project structure to place the converted file, maintaining modularity and best practices. Embed it into <target_folder_path></target_folder_path> tag
        3) Converted ReactJS Code: Transform the given AngularJS code into a functionally equivalent ReactJS version.  Start and end it with <converted_code></converted_code> but return formatted code.
    """
    return view_controller_conversion_prompt


def get_routing_information_prompt(files_to_process):
    found_route = False
    for user_request_details_id, (file_name, file_content) in files_to_process.items():
        # print(file_name)
        # if file_name.endswith("config.js"): print(file_content)
        if ROUTER_FILE_FIND_STRING in file_content:  
            found_route = True
            logging.info(f"Found route in file: {file_name}")
            break
    if not found_route: return None, None, None, None
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
    return user_request_details_id, file_name, file_content, routing_information_prompt

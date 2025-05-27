from io_utils import read_file
import logging

ROUTER_FILE_FIND_STRING = "$urlRouterProvider"

def get_document_generation_prompt(source_language, files_to_process, file_name,  file_content, additional_context):
    project_structure = ""
    for _, (file, _) in files_to_process.items():
        project_structure = project_structure + f"\n{file}"
    
    document_generation_prompt = f"""
	You are a technical analyst assisting in generating business documentation from source code.
	The following is the content of a code file from a larger software project. Your task is to extract relevant information that will later help generate business requirement documents (BRDs) and user stories.
	Focus on translating low-level implementation details into higher-level functional and business context, suitable for stakeholders like Product Owners, Business Analysts, or Delivery Managers.
    Do not generate anything outside of this documentation.

    ### Input:
        File Name: {file_name}
        File Content:
        {file_content}
        
        My Project is using {source_language} programming language.
        {"" if additional_context is None else {"Additional Context:" + additional_context}}

        Project File Structure:
        {project_structure}

	### For each file, extract the following in clear, structured form:

	1. **Purpose of the File**  
	   - What is this file responsible for?
	   - How does it contribute to the overall application?

	2. **Key Responsibilities / Logic Implemented**  
	   - Summarize the main logic, workflows, or operations in simple terms.
	   - Mention any input/output handling, validations, data processing, etc.

    3. **UI Components** (if applicable): 
       - List any frontend components, frameworks, or libraries used. Describe their role and interactions. 
    
    4. **Key Functions & Classes**: 
       - Summarize the core functions, classes, and business logic present in the file. Provide a high-level explanation of their roles.
	
    5. **User or Business Impact**  
	   - Describe what feature or user interaction this supports.
	   - How does this help fulfill a business or user need?

	6. **Dependencies / Interactions**  
	   - What modules, services, or components does this file rely on?
	   - What external systems or APIs does it interact with?
       - Database Interactions

    7. **Configuration & Environment Variables
       - Identify any configurations, feature flags, or environment variables required for execution.

    8. **Error Handling & Logging**
       - Describe how errors are managed and how logging is implemented.

	### Output Format:
	Respond in **Markdown** using the structure below.

	## File: [filename or path]

	### 1. Purpose of the File
	[Explanation]

	### 2. Key Responsibilities / Logic Implemented
	- [Responsibility 1]
	- [Responsibility 2]

    ### 3. *UI Components
	- [Any textboxes, Checkbox, label, buttons and more html components]

    ### 4. *Key Functions & Classes
	- [Describe keywords technical keyword used and usage]

	### 5. User or Business Impact
	[Describe the user-facing or business-relevant purpose of this functionality.]

	### 6. Dependencies / Interactions
	- Depends on: [list modules/services]
	- Interacts with: [list APIs/external systems]

    ### 7. Configuration & Environment Variables
    [Identify any configurations, feature flags, or environment variables required for execution]

    ### 8. Error Handling & Logging
    [Describe how errors are managed and how logging is implemented]

    Format the response in a structured Markdown format for easy readability without any unnecessary commentary.
    """
    return document_generation_prompt


def get_brd_generation_prompt(documentation_content, additional_context):
    brd_generation_prompt = f"""
    You are a Business Analyst generating a **Business Requirement Document (BRD)** based on detailed technical documentation provided from a software project. This documentation is extracted file by file, including the purpose, responsibilities, business impact, and dependencies of each file/module.
    Your task is to consolidate and translate this technical information into a coherent and stakeholder-friendly BRD that includes the following sections:
    Do not generate anything outside of this documentation.
    ### Input:
    {documentation_content}

    {"" if additional_context is None else {"Additional Context:" + additional_context}}

    ### Desired Output Format (in Markdown):

    # Business Requirement Document (BRD)

    ## 1. Project Overview
    Provide a high-level summary of what the project is, what problems it solves, and its business goals.

    ## 2. Core Business Objectives
    Summarize the key business drivers, goals, or user needs that this solution addresses.

    ## 3. Functional Scope
    List the main business capabilities and functionalities delivered by the system, structured as sub-sections where relevant.

    ## 4. System Features & Descriptions
    Detail the functional modules, their responsibilities, and user-facing outcomes. Use the file-by-file documentation to build this section. Present each module or component with:
    - Feature Name
    - Description
    - Business Use Case
    - Dependencies or external interactions

    ## 5. UI Screen Details:
    - Screen Name
    - Description
    - UI Components (textbox, label, dropdown, checkbox, buttons and other html components)
        - details of each component 

    ## 6. Assumptions and Constraints
    Mention any business or technical assumptions, limitations, or required conditions based on the documentation.

    ## 7. Stakeholders and Impacted Users
    (Optional if inferable) List the primary users, departments, or roles impacted or served by this project.

    Use simple, clear language appropriate for business and product stakeholders. Avoid code references unless necessary to clarify a feature or behavior.
    Format the response in a structured Markdown format for easy readability without any unnecessary commentary.
    """
    return brd_generation_prompt

def get_user_query_prompt(documentation_content, additional_context, user_query):
    user_query_prompt = f"""
    You are an expert business and technical analyst assistant.
    Below is a business functionality or technical documentation extracted from a software project. A user has a specific question about this documentation.
    Do not respond anything outside of this documentation.

    ### Your Task:
    - Analyze the documentation and provide a detailed, accurate, and clear answer to the user's question.
    - If the answer involves multiple parts or components, use bullet points or subheadings for clarity.
    - If the answer is not directly found in the document, infer from related content and mention that the answer is inferred.

    ### Response Format: Markdown
    
    ### User Question:
    {user_query}

    ### Documentation Context:
    {documentation_content}

    {"" if additional_context is None else {"Additional Context:" + additional_context}}
    """
    return user_query_prompt


def get_document_consolidation_prompt(documentation_content, additional_context):
    document_consolidation_prompt = f"""
    You are an expert business documentation analyst.

    The input below contains multiple business functionality documents, each describing features, use cases, and user impact for different (but possibly overlapping) modules of a software system. These documents may contain:
    - Redundant or similar content under different headings.
    - Varying levels of detail or naming for the same feature.
    - Disjointed structure across documents.

    Do not generate anything outside of this documentation.

    ### Input:
    {documentation_content}

    {"" if additional_context is None else {"Additional Context:" + additional_context}}

    ### Your Task:
    Carefully read and consolidate the input documents into one **comprehensive, deduplicated, and well-organized** business functionality document.

    ### Requirements:
    1. **Merge Similar Sections**  
    - Combine overlapping content into unified sections.
    - Use the most detailed or accurate descriptions where duplication exists.

    2. **Organize Logically**  
    - Group features or functionality under intuitive, clearly named sections.
    - Maintain a logical flow from business goals to features and interactions.

    3. **Enhance Clarity & Detail**  
    - Rewrite or expand summaries for better business understanding.
    - Add bullet points or sub-sections where helpful.

    4. **Output Format: Markdown**
    """
    return document_consolidation_prompt

def get_review_prompt(documentation_content, additional_context, llm_response):
    review_prompt = f"""
    You are a senior business analyst and domain expert tasked with reviewing a business functionality document.
    The document below was created from code-level or module-level analysis, and your job is to evaluate the **quality of the output** based on the following criteria:
    Do not suggest anything from outside of this documentation.

    {"" if additional_context is None else {"Additional Context of the project:" + additional_context}}

    ### Documentation Provided:
    {documentation_content}

    ### Created Documentation by business analyst:
    {llm_response}

    ### Review Criteria:

    1. **Accuracy**  
    - Does the document correctly describe the functionalities based on the input?
    - Are the business use cases and module purposes described precisely?

    2. **Completeness**  
    - Are all relevant features, modules, and interactions captured?
    - Are any important elements missing or overly summarized?

    3. **Clarity & Readability**  
    - Is the language easy to understand for business and product stakeholders?
    - Are sections logically structured and labeled appropriately?

    4. **Business Relevance**  
    - Do the described features clearly tie to business needs, user goals, or outcomes?
    - Are the business objectives and impacts well aligned with the features?

    5. **Duplication or Redundancy**  
    - Are there repeated sections or redundant descriptions that need merging?
    - Could similar items be grouped or unified for better flow?

    ### Your Task:
    Provide a constructive review of the created document using the criteria above. 
    Summarize what is done well and what needs improvement. Suggest specific changes where applicable.
    Just provide review comments without additonal commentary.
    """
    return review_prompt


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

import traceback
import pandas as pd
import os
import tiktoken
from oci_utils import generate_oci_gen_ai_response
import re
import json
import shutil
import database_utils
import logging
import prompts

conversion_folder = "code_conversion_files"
react_project_zip_file = f"{conversion_folder}/target_react_structure/react_project.zip"
FILE_EXCLUSIONS = ["png","jpg","jpeg","txt","md","json","xml","csv","zip","gz","tar","pdf","doc","docx","xls","xlsx","ppt","pptx","pyc","exe","dll","so","lib",
                   "obj","bin","jar","war","ear","class","vbproj","csproj","vcxproj","vcproj","filters","user","data","vspscc","sln","suo","webinfo","xsd","xslt"]
ANGULER_JS_FILE_INCLUSIONS = ["png","jpg","jpeg","ts","js","html","css","xml","csv"]
ROUTER_FILE_FIND_STRING = "$urlRouterProvider"
SAMPLE_REACT_PROJECT_PATH = "./react_project"

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
        for _, (file_name, _) in files_to_process.items():
            fname = file_name.split("/")[-1]
            if "controller" in file_name and controller in fname:
                controller = file_name
                gotController = True
                break
        for _, (file_name, _) in files_to_process.items():
            if file_name.endswith(view_path):
                view_path = file_name
                gotView = True
                break
        if gotController and gotView:
            view_controller_mapping[view_path] = controller
    print(f"view_controller_mapping:{view_controller_mapping}")
    return view_controller_mapping


def generate_route_file(llm_model, files_to_process):
    user_request_details_id, file_name, routing_information_prompt = prompts.get_routing_information_prompt(files_to_process)
    view_controller_info ={}
    if user_request_details_id is not None:
        response = generate_oci_gen_ai_response(llm_model, [{"role":"user", "content": routing_information_prompt}])  
        response = response.replace("```json","").replace("```","")
        routing_information = json.loads(response)
        view_controller_info = get_view_controller_info(files_to_process, routing_information)    
        code_converion_prompt = prompts.get_ang_to_react_code_conversion_prompt(files_to_process)
        response = generate_oci_gen_ai_response(llm_model, [{"role":"user", "content": code_converion_prompt}])                                     
        _, _, converted_code = __get_details_from_repsonse(response)
        target_file_to_create = "react_project/src/App.jsx"
        print(f"target_file_to_create:{target_file_to_create}")
        converted_code = converted_code.replace("```javascript","").replace("```","").replace("```jsx","").replace("```","").replace("jsx","")
    return user_request_details_id, file_name, target_file_to_create, view_controller_info, converted_code


def handle_view_controller_files(files_to_process, target_folder_structure, view_controller_info, route_file, route_file_content, test_mode):
    output = []
    errors = []
    for view_file_name, controller_file_name in view_controller_info.items():
        print(f"Processing view file: {view_file_name}, controller_file:{controller_file_name}")            
        try:
            view_controller_conversion_prompt = prompts.get_view_controller_conversion_prompt(files_to_process, view_file_name, controller_file_name, SAMPLE_REACT_PROJECT_PATH, target_folder_structure, route_file, route_file_content)
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
        if test_mode:
            break
    return output, errors, target_structure


def get_number_of_tokens(file_content):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(file_content)
    return len(tokens)

def get_files_from_database(user_request_id, exclude_files=FILE_EXCLUSIONS, include_files=None, include_empty_folders = False):
    db_get_user_request_details = database_utils.db_get_user_request_details(user_request_id)
    files_to_process = {}
    dirs = []
    file_objects = db_get_user_request_details["items"]    
    for item in file_objects:
        user_request_details_id = item["user_request_details_id"]
        file_name = item["file_name"]
        extension = file_name.split(".")[-1]
        if "." not in file_name or (exclude_files is None or extension not in exclude_files) and (include_files is None or extension in include_files):            
            file_content = item["file_content"]
            files_to_process[user_request_details_id] = (file_name, file_content)
    if include_empty_folders and file_name.endswith("/"):
        dirs.append(file_name)
    return files_to_process, dirs

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
    
def generate_analysis_report(user_request_id, test_mode):
    logging.info(f"START: generate_analysis_report with user_request_id={user_request_id}")
    try:
        db_user_request = database_utils.db_get_user_request(user_request_id)
        package_name = db_user_request["zip_file_name"].split(".")[0]
        updated_by = db_user_request["updated_by"]
        logging.info(f"Package name: {package_name}, Updated by: {updated_by}")
        
        files_to_process, _ = get_files_from_database(user_request_id, exclude_files=FILE_EXCLUSIONS, include_files=None)
        logging.info(f"Number of files to process: {len(files_to_process)}")
        
        if len(files_to_process) == 0:
            logging.error("No files found in the source folder")
            raise Exception("No files found in the source folder")
        
        errors = []
        df = pd.DataFrame(columns=['user_request_details_id', 'user_request_id', 'num_lines', 'num_lines_no_docs', 'token_count', 'token_count_no_docs', 'success_flag', 'error_details', 'updated_by'])
        data_counter = 0
        
        for user_request_details_id, (file_name, file_content) in files_to_process.items():
            try:
                logging.info(f"Processing file: {file_name}")
                total_tokens = get_number_of_tokens(file_content)
                tokens_without_comments = number_of_lines = 0
                number_of_lines_without_comments = 0
                tokens_without_comments_content = ""
                
                for line in file_content.splitlines():
                    number_of_lines += 1
                    if not line.startswith("#") and line.strip() != "" and not line.startswith("//"):
                        number_of_lines_without_comments += 1
                        tokens_without_comments_content += line
                
                tokens_without_comments = get_number_of_tokens(tokens_without_comments_content)
                df.loc[data_counter] = [user_request_details_id, user_request_id, number_of_lines, number_of_lines_without_comments, total_tokens, tokens_without_comments, "Y", None, updated_by]
                data_counter += 1
                logging.info(f"File processed successfully: {file_name}")
                if test_mode and data_counter >= 3:
                    break
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {str(e)}")
                logging.debug(traceback.format_exc())
                errors.append(file_name)
        
        logging.info(f"Errors encountered: {errors}")
        logging.info(f"Completed generating analysis report for package_name: {package_name}")
        database_utils.update_analysis_report(df)
    except Exception as e:
        logging.error(f"Error in generate_analysis_report: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info(f"END: generate_analysis_report with user_request_id={user_request_id}")


def generate_documentation_report(llm_model, user_request_id, test_mode, additional_context):
    logging.info(f"START: generate_documentation_report with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        db_user_request = database_utils.db_get_user_request(user_request_id)
        package_name = db_user_request["zip_file_name"].split(".")[0]
        updated_by = db_user_request["updated_by"]
        source_language = database_utils.get_language_details(db_user_request["source_lang_id"])

        logging.info(f"Package name: {package_name}, Updated by: {updated_by}, Source language: {source_language}")
        
        files_to_process, _ = get_files_from_database(user_request_id, exclude_files=FILE_EXCLUSIONS, include_files=None)
        logging.info(f"Number of files to process: {len(files_to_process)}")

        if len(files_to_process) == 0:
            logging.error("No files found in the source folder")
            raise Exception("No files found in the source folder")

        errors = []
        df = pd.DataFrame(columns=['user_request_details_id', 'user_request_id', 'documentation_file_name', 'documentation_file_content', 'success_flag', 'error_details', 'updated_by'])
        data_counter = 0
        documentation_content = ""

        for user_request_details_id, (file_name, file_content) in files_to_process.items():
            try:
                logging.info(f"Processing file: {file_name}")
                document_generation_prompt = prompts.get_document_generation_prompt(source_language, files_to_process, additional_context)
                response = generate_oci_gen_ai_response(llm_model, [{"role": "user", "content": document_generation_prompt}])
                
                target_file = f"documentation/{file_name}"
                if "." in target_file:
                    extension = target_file.split(".")[-1]
                    target_file = target_file.replace(f".{extension}", "_documentation.md")
                else:
                    target_file = target_file + "_documentation.md"

                logging.info(f"Generated documentation for file: {file_name}, Target file: {target_file}")
                documentation_content += f"\nFile:{target_file}\nContent of file:\n{response}"
                df.loc[data_counter] = [user_request_details_id, user_request_id, target_file, response, "Y", None, updated_by]
                data_counter += 1

                if test_mode and data_counter >= 3:
                    logging.info("Test mode enabled, stopping after processing 3 files.")
                    break
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {str(e)}")
                logging.debug(traceback.format_exc())
                errors.append(file_name)

        logging.info(f"Generating BRD content")
        brd_generation_prompt = prompts.get_brd_generation_prompt(documentation_content)
        response = generate_oci_gen_ai_response(llm_model, [{"role": "user", "content": brd_generation_prompt}])
        df.loc[data_counter] = [None, user_request_id, "documentation/BusinessRequirementDocument.md", response, "Y", None, updated_by]

        logging.info(f"Errors encountered: {errors}")
        logging.info(f"Completed generating documentation report for package_name: {package_name}")
        database_utils.update_documentation_report(df)
    except Exception as e:
        logging.error(f"Error in generate_documentation_report: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info(f"END: generate_documentation_report with user_request_id={user_request_id}, test_mode={test_mode}")

def generate_conversion_report(llm_model, user_request_id, test_mode, additional_context):
    db_user_request = database_utils.db_get_user_request(user_request_id)
    package_name = db_user_request["zip_file_name"].split(".")[0]
    updated_by = db_user_request["updated_by"]
    source_language = database_utils.get_language_details(db_user_request["source_lang_id"])
    target_language = database_utils.get_language_details(db_user_request["target_lang_id"])
    
    files_to_process, _ = get_files_from_database(user_request_id, exclude_files=None, include_files=ANGULER_JS_FILE_INCLUSIONS)
    logging.info(f"Number of files to process: {len(files_to_process)}")

    if len(files_to_process) == 0:
        logging.error("No files found in the source folder")
        raise Exception("No files found in the source folder")

    errors = []
    df = pd.DataFrame(columns=['user_request_details_id', 'user_request_id', 'documentation_file_name', 'documentation_file_content', 'success_flag', 'error_details', 'updated_by'])
    data_counter = 0

    print(f"Started converting code from: {source_language} to {target_language} for package_name: {package_name}")
    if source_language.lower() != "AngularJS".lower() or target_language.lower() != "ReactJS".lower():
        raise Exception("Invalid source or target language selected. Please select AngularJS as source and ReactJS as target language.")

    target_folder_structure = get_files_from_directory(SAMPLE_REACT_PROJECT_PATH, exclude_files=None, include_files=ANGULER_JS_FILE_INCLUSIONS, include_empty_folders=True)
    user_request_details_id, route_file, target_file_to_create, view_controller_info, route_file_content = generate_route_file(llm_model, files_to_process)
    data_counter = 0
    errors = []
    df = pd.DataFrame(columns=['user_request_details_id', 'user_request_id', 'conversion_file_name', 'conversion_file_content', 'success_flag', 'error_details', 'updated_by'])
    print(f"Before files_to_process size:{len(files_to_process)}")
    if user_request_details_id is not None:
        target_folder_structure.append(route_file)
        files_to_process.remove(user_request_details_id)
        df.loc[data_counter] = [user_request_details_id, user_request_id, target_file_to_create, converted_code, "Y", None, updated_by]
        data_counter+= 1
        output, errors, target_folder_structure = handle_view_controller_files(files_to_process, target_folder_structure, view_controller_info, route_file, route_file_content, test_mode)
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
            if test_mode and data_counter >= 3:
                break
        print(f"errors:{errors}")
        print(f"Completed converting code from: {source_lang} to {target_lang} for source folder: {source_folder}")
        return target_folder, df


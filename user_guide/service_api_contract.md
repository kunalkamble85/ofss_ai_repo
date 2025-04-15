# UI Changes
0) Add Download Project button
1) Source Code Files: VIew File, File Path, File Type
2) Analysis: File Path, Package, Number Of Lines, Number of Lines without Comments, Tokens, Tokens without comments, SUCCESS, ERROR
3) Documentation: File Path, Documentation Path, SUCCESS, ERROR, View and Download
4) Conversion Region: Source Path, Target Path, SUCCESS, ERROR, View and Download


# UI and Service communication

### Run Analysis Button Click:

    -- service name: generate_anylysis
    -- rest_type: POST
    -- INPUT - file_name, file_content
    -- OUTPUT - file_name, package, number_of_lines, number_of_lines_no_doc,tokens, tokens_no_doc, success, error    
    
    example input: {"file_name":"{}","file_content":"{}"}
    example response: {"file_name":"test_name","number_of_lines":"5", "number_of_lines_no_doc":"3", "tokens":"100", "tokens_no_doc":"80", "error":"", "success":{}}

### Run Documentation Button Click:
    -- service name -- generate_documentation
    -- rest_type: POST
    -- INPUT - file_name, file_content, source_language, additional_context, project_structure
    -- OUTPUT - file_name, documentation_path, documentation_content, success, error

    -- service name -- generate_brd_documenation
    -- rest_type: POST
    -- INPUT - documentation_content, additional_context
    -- OUTPUT - brd_file_name, brd_path, brd_content, success, error
    example for input: -- documentation_content = documentation_content + f"\nFile:{target_file}\nHTML Content of file:\n{response}"

### Run Conversion Button Click:
    -- service name -- generate_conversion
    -- rest_type: POST
    -- INPUT - file_name, file_content, source_language, target_language, additional_context, project_structure
    -- OUTPUT - file_name, conversion_path, conversion_content, success, error


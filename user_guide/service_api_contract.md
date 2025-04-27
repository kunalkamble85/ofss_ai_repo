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
    -- INPUT - USER_REQUEST_ID
    -- OUTPUT - list of {"success":True/False}
    
    example input: {"USER_REQUEST_ID":"1"}
    example response: {"success":True/False}

### Run Documentation Button Click:
    -- service name -- generate_documentation
    -- rest_type: POST
    -- INPUT - USER_REQUEST_ID, ADDITIONAL_CONTEXT
    -- OUTPUT - {"success":True/False}

    -- service name -- generate_brd_documenation
    -- rest_type: POST
    -- INPUT - USER_REQUEST_ID, ADDITIONAL_CONTEXT
    -- OUTPUT - {"success":True/False}

### Run Conversion Button Click:
    -- service name -- generate_conversion
    -- rest_type: POST
    -- INPUT - USER_REQUEST_ID, SOURCE_LANG, TARGET_LANG, ADDITIONAL_CONTEXT
    -- OUTPUT - {"success":True/False}


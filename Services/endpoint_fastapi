from fastapi import FastAPI
from GenAI_Service import generate_analysis_report, generate_documentation_report, generate_conversion_report
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

#Create a post service to receive a json object with the following fields: file_name and file_content. The service should return the json object with fields: file_name, package, number_of_lines, number_of_lines_no_doc,tokens, tokens_no_doc, success, error
@app.post("/generate_analysis/")
async def generate_analysis(project_id: str):

        response = generate_analysis_report(project_id)
        return {
            "success": response
        }
        
#Create a post service to receive a json object with the following fields: file_name, file_content, source_language, additional_context, project_structure. The service should return the json object with fields: file_name, documentation_path, documentation_content, success, error
@app.post("/generate_documentation/")
async def generate_documentation(project_id, source_language, additional_context: str, project_structure: str):
        return generate_documentation_report(project_id, source_language)

         
 #Create a post service to receive a json object with the following fields: file_name, file_content, source_language, target_language, additional_context, project_structure. The service should return the json object with fields: file_name, conversion_path, conversion_content, success, error.
@app.post("/generate_conversion/")
async def generate_conversion(file_name: str, file_content: str, source_language: str, target_language: str, additional_context: str, project_structure: str):
    try:
        # Simulate some processing
        conversion_path = f"/conversions/{file_name}.{target_language}"
        conversion_content = f"// Converted content from {source_language} to {target_language}\n\n{file_content}"

        return {
            "file_name": file_name,
            "conversion_path": conversion_path,
            "conversion_content": conversion_content,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "file_name": file_name,
            "success": False,
            "error": str(e)
        }
    
#Create a post service to receive a json object with the following fields: documentation_content, additional_context. The service should return the json object with fields: brd_file_name, brd_path, brd_content, success, error.
#example for input: -- documentation_content = documentation_content + f"\nFile:{target_file}\nHTML Content of file:\n{response}"
@app.post("/generate_brd/")
async def generate_brd(documentation_content: str, additional_context: str):
    try:
        # Simulate some processing
        brd_file_name = "BRD.md"
        brd_path = f"/brds/{brd_file_name}"
        brd_content = f"# Business Requirements Document\n\n{documentation_content}"

        return {
            "brd_file_name": brd_file_name,
            "brd_path": brd_path,
            "brd_content": brd_content,
            "success": True,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 

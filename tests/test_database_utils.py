import requests
import database_utils
import base64

def test_docx_file(num):
    api_endpoint = f"{database_utils.ORDS_SERVICE_ENDPOINT}/{database_utils.DOCUMENTATION_DETAILS}/{num}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        data = response.json()
        docx_blob = data.get("documentation_file_content_docx")
        if docx_blob:
            # Decode base64 to bytes
            docx_bytes = base64.b64decode(docx_blob)
            # Write to a .docx file
            filename = f"output_{num}.docx"
            with open(filename, "wb") as f:
                f.write(docx_bytes)
            print(f"Wrote docx file: {filename}")

def test_update_user_request_status():
    data = {"analysis_request_status": "Done", "error_message":None}
    database_utils.update_user_request_status(4, data)


# test_update_user_request_status()
for num in [604,605,587,589,591,588]:
    test_docx_file(num)
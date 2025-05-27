import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI
import code_conversion_utils
from pydantic import BaseModel
import threading
import time

# Configure logging with a rolling appender for daily logs
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "fast_serv.log")

handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
handler.suffix = "%Y-%m-%d"

logging.basicConfig(level=logging.WARNING, handlers=[handler])

os.environ["TIKTOKEN_CACHE_DIR"] = "./cache"
app = FastAPI()

class UserRequest(BaseModel):
    """
    Represents the structure of a user request for the API endpoints.
    """
    user_request_id: int
    llm_model: str = "meta.llama3.3-70b"
    test_mode: bool = False
    use_embedding: bool = True
    additional_context: str = None
    documentation_components: list = []
    user_query: str = None


@app.get("/")
async def root(test_mode: bool = False):
    logging.warning(f"Input parameters for root: test_mode={test_mode}")
    logging.warning(f"START: root method with test_mode={test_mode}")
    response = {"message": "Fast API is running successfully."}
    logging.warning(f"END: root method with response={response}")
    return response


@app.post("/generate_analysis/")
async def generate_analysis(user_request: UserRequest):
    logging.warning(f"Input parameters for generate_analysis: user_request_id={user_request.user_request_id}, test_mode={user_request.test_mode}")
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    logging.warning(f"START: generate_analysis method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        def run_report():
            code_conversion_utils.generate_analysis_report(user_request_id, test_mode)

        thread = threading.Thread(target=run_report)
        logging.warning(f"Calling code_conversion_utils.generate_analysis_report with user_request_id={user_request_id}, test_mode={test_mode} in a separate thread")
        thread.start()
        # Do not join the thread; respond immediately
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.warning(f"END: generate_analysis method with response={response}")
        return response
    except Exception as e:
        logging.warning(f"Error in generate_analysis: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.warning(f"END: generate_analysis method with response={response}")
        return response

@app.post("/generate_documentation/")
async def generate_documentation(user_request: UserRequest):
    logging.warning(f"Input parameters for generate_documentation: user_request_id={user_request.user_request_id}, test_mode={user_request.test_mode}, llm_model={user_request.llm_model}, additional_context={user_request.additional_context}, documentation_components={user_request.documentation_components}")
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model
    documentation_components = user_request.documentation_components

    logging.warning(f"START: generate_documentation method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        def run_report():
            code_conversion_utils.generate_documentation_report(llm_model, user_request_id, test_mode, additional_context, documentation_components)

        thread = threading.Thread(target=run_report)
        logging.warning(f"Calling code_conversion_utils.generate_documentation_report with user_request_id={user_request_id}, test_mode={test_mode} in a separate thread")
        thread.start()
        # Do not join the thread; respond immediately
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.warning(f"END: generate_documentation method with response={response}")
        return response
    except Exception as e:
        logging.warning(f"Error in generate_documentation: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.warning(f"END: generate_documentation method with response={response}")
        return response

@app.post("/generate_conversion/")
async def generate_conversion(user_request: UserRequest):
    logging.warning(f"Input parameters for generate_conversion: user_request_id={user_request.user_request_id}, test_mode={user_request.test_mode}, llm_model={user_request.llm_model}, additional_context={user_request.additional_context}")
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model
    logging.warning(f"START: generate_conversion method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        def run_report():
            code_conversion_utils.generate_conversion_report(llm_model, user_request_id, test_mode, additional_context)

        thread = threading.Thread(target=run_report)
        logging.warning(f"Calling code_conversion_utils.generate_conversion_report with user_request_id={user_request_id}, test_mode={test_mode} in a separate thread")
        thread.start()
        # Do not join the thread; respond immediately
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.warning(f"END: generate_conversion method with response={response}")
        return response
    except Exception as e:
        logging.warning(f"Error in generate_conversion: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.warning(f"END: generate_conversion method with response={response}")
        return response
    

@app.post("/handle_documentation_user_request/")
async def handle_documentation_user_request_endpoint(user_request: UserRequest):
    logging.warning(f"Input parameters for handle_documentation_user_request_endpoint: user_request_id={user_request.user_request_id}, llm_model={user_request.llm_model}, additional_context={user_request.additional_context}, user_query={user_request.user_query}")
    user_request_id = user_request.user_request_id
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model
    user_query = user_request.user_query
    use_embedding = user_request.use_embedding

    logging.warning(f"START: handle_documentation_user_request_endpoint with user_request_id={user_request_id}")
    try:
        user_query_response = code_conversion_utils.handle_documentation_user_request(llm_model, user_request_id, additional_context, user_query, use_embedding)
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None,
            "user_query_response": user_query_response
        }
        logging.warning(f"END: handle_documentation_user_request_endpoint with response={response}")
        return response
    except Exception as e:
        logging.warning(f"Error in handle_documentation_user_request_endpoint: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e),
            "user_query_response": None
        }
        logging.warning(f"END: handle_documentation_user_request_endpoint with response={response}")
        return response
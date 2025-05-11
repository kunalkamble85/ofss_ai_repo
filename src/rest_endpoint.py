import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI
import code_conversion_utils
from pydantic import BaseModel

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

@app.get("/")
async def root(test_mode: bool = False):
    """
    Root endpoint to check if the FastAPI service is running.

    Args:
        test_mode (bool): Indicates whether the service is running in test mode.

    Returns:
        dict: A message indicating the service status.
    """
    logging.warning(f"START: root method with test_mode={test_mode}")
    response = {"message": "Fast API is running successfully."}
    logging.warning(f"END: root method with response={response}")
    return response

class UserRequest(BaseModel):
    """
    Represents the structure of a user request for the API endpoints.
    """
    user_request_id: int
    llm_model: str = "meta.llama3.3-70b"
    test_mode: bool = False
    additional_context: str = None

@app.post("/generate_analysis/")
async def generate_analysis(user_request: UserRequest):
    """
    Endpoint to generate an analysis report for a given user request.

    Args:
        user_request (UserRequest): The user request containing the request ID, test mode, and additional context.

    Returns:
        dict: A response indicating the success or failure of the operation.
    """
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    logging.warning(f"START: generate_analysis method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.warning(f"Calling code_conversion_utils.generate_analysis_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_analysis_report(user_request_id, test_mode)
        logging.warning(f"Completed code_conversion_utils.generate_analysis_report for user_request_id={user_request_id}")
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
    """
    Endpoint to generate a documentation report for a given user request.

    Args:
        user_request (UserRequest): The user request containing the request ID, test mode, LLM model, and additional context.

    Returns:
        dict: A response indicating the success or failure of the operation.
    """
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model

    logging.warning(f"START: generate_documentation method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.warning(f"Calling code_conversion_utils.generate_documentation_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_documentation_report(llm_model, user_request_id, test_mode, additional_context)
        logging.warning(f"Completed code_conversion_utils.generate_documentation_report for user_request_id={user_request_id}")        
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
    """
    Endpoint to generate a conversion report for a given user request.

    Args:
        user_request (UserRequest): The user request containing the request ID, test mode, LLM model, and additional context.

    Returns:
        dict: A response indicating the success or failure of the operation.
    """
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model
    logging.warning(f"START: generate_conversion method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.warning(f"Calling code_conversion_utils.generate_conversion_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_conversion_report(llm_model, user_request_id, test_mode, additional_context)
        logging.warning(f"Completed code_conversion_utils.generate_conversion_report for user_request_id={user_request_id}")
        
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
import os
import logging
from fastapi import FastAPI
import code_conversion_utils
from pydantic import BaseModel

logging.basicConfig(filename="./logs/fast_serv.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
os.environ["TIKTOKEN_CACHE_DIR"] = "./cache"
app = FastAPI()

@app.get("/")
async def root(test_mode: bool = False):
    logging.info(f"START: root method with test_mode={test_mode}")
    response = {"message": "Fast API is running successfully."}
    logging.info(f"END: root method with response={response}")
    return response

class UserRequest(BaseModel):
    user_request_id: int
    llm_model: str = "meta.llama3.3-70b"
    test_mode: bool = False
    additional_context: str = None


@app.post("/generate_analysis/")
async def generate_analysis(user_request: UserRequest):
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    logging.info(f"START: generate_analysis method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.info(f"Calling code_conversion_utils.generate_analysis_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_analysis_report(user_request_id, test_mode)
        logging.info(f"Completed code_conversion_utils.generate_analysis_report for user_request_id={user_request_id}")
        
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.info(f"END: generate_analysis method with response={response}")
        return response
    except Exception as e:
        logging.error(f"Error in generate_analysis: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.info(f"END: generate_analysis method with response={response}")
        return response

@app.post("/generate_documentation/")
async def generate_documentation(user_request: UserRequest):
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model

    logging.info(f"START: generate_documentation method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.info(f"Calling code_conversion_utils.generate_documentation_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_documentation_report(llm_model, user_request_id, test_mode, additional_context)
        logging.info(f"Completed code_conversion_utils.generate_documentation_report for user_request_id={user_request_id}")        
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.info(f"END: generate_documentation method with response={response}")
        return response
    except Exception as e:
        logging.error(f"Error in generate_documentation: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.info(f"END: generate_documentation method with response={response}")
        return response


@app.post("/generate_conversion/")
async def generate_conversion(user_request: UserRequest):
    user_request_id = user_request.user_request_id
    test_mode = user_request.test_mode
    additional_context = user_request.additional_context
    llm_model = user_request.llm_model
    logging.info(f"START: generate_conversion method with user_request_id={user_request_id}, test_mode={test_mode}")
    try:
        logging.info(f"Calling code_conversion_utils.generate_conversion_report with user_request_id={user_request_id}, test_mode={test_mode}")
        code_conversion_utils.generate_conversion_report(llm_model, user_request_id, test_mode, additional_context)
        logging.info(f"Completed code_conversion_utils.generate_conversion_report for user_request_id={user_request_id}")
        
        response = {
            "user_request_id": user_request_id,
            "success": True,
            "error": None
        }
        logging.info(f"END: generate_conversion method with response={response}")
        return response
    except Exception as e:
        logging.error(f"Error in generate_conversion: {str(e)}")
        response = {
            "user_request_id": user_request_id,
            "success": False,
            "error": str(e)
        }
        logging.info(f"END: generate_conversion method with response={response}")
        return response
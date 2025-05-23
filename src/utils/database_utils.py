import requests
import json
import datetime
import traceback
import logging
import base64

ORDS_SERVICE_ENDPOINT = "https://apex.oraclecorp.com/pls/apex/tieaicckk"
SOURCE_LANGUAGES = "sourcelanguages"
USER_REQUEST = "userrequest"
USER_REQUEST_DETAILS = "userrequestdetails"
ANALYSIS_DETAILS = "analysisdetails"
DOCUMENTATION_DETAILS = "documentationdetails"
CONVERSION_DETAILS = "conversiondetails"
DOCUMENTATION_COMPONENTS = "documentationcomponents"


def get_language_details(code_language_id):
    """
    Fetches the language code for a given language ID.

    Args:
        code_language_id (int): The ID of the language.

    Returns:
        str: The language code corresponding to the given ID.

    Raises:
        Exception: If there is an error during the API call or response processing.
    """
    logging.warning(f"START: get_language_details with code_language_id={code_language_id}")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{SOURCE_LANGUAGES}/{code_language_id}"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            logging.warning(f"END: get_language_details with response={data}")
            return data["code"]
        else:
            response.raise_for_status()
    except Exception as e:
        logging.warning(f"Error in get_language_details: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: get_language_details with code_language_id={code_language_id}")


def db_get_user_request(user_request_id):
    """
    Fetches user request details for a given user request ID.

    Args:
        user_request_id (int): The ID of the user request.

    Returns:
        dict: The user request details.

    Raises:
        Exception: If there is an error during the API call or response processing.
    """
    logging.warning(f"START: db_get_user_request with user_request_id={user_request_id}")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST}/{user_request_id}"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            data["zip_file_content"] = None
            logging.warning(f"END: db_get_user_request with response={data}")
            return data
        else:
            response.raise_for_status()            
    except Exception as e:
        logging.warning(f"Error in db_get_user_request: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: db_get_user_request with user_request_id={user_request_id}")

def db_get_user_request_details(user_request_id):
    """
    Fetches user request details for all items associated with a given user request ID.

    Args:
        user_request_id (int): The ID of the user request.

    Returns:
        dict: The details of all items associated with the user request.

    Raises:
        Exception: If there is an error during the API call or response processing.
    """
    logging.warning(f"START: db_get_user_request_details with user_request_id={user_request_id}")
    try:
        query_param = '?q={"user_request_id":{"$eq":"'+str(user_request_id)+'"}}&limit=500'
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST_DETAILS}/{query_param}"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            file_objects = data["items"]    
            for item in file_objects:
                if item["file_content"] is not None and item["file_type"] == "Text": item["file_content"] = decode_blob_to_string(item["file_content"])
            return data
        else:
            response.raise_for_status()            
    except Exception as e:
        logging.warning(f"Error in db_get_user_request_details: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: db_get_user_request_details with user_request_id={user_request_id}")

def db_get_documentation_components():
    logging.warning(f"START: db_get_documentation_components.")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{DOCUMENTATION_COMPONENTS}/"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            # If there are any BLOB fields, decode as needed here
            return data["items"]
        else:
            response.raise_for_status()
    except Exception as e:
        logging.warning(f"Error in db_get_documentation_components: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: db_get_documentation_components.")


def db_get_documentation_details(user_request_id):
    logging.warning(f"START: db_get_documentation_details.")
    try:
        query_param = '?q={"user_request_id":{"$eq":"'+str(user_request_id)+'"}}&limit=500'
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{DOCUMENTATION_DETAILS}/{query_param}"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()            
            return data["items"]
        else:
            response.raise_for_status()
    except Exception as e:
        logging.warning(f"Error in db_get_documentation_details: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: db_get_documentation_details.")
    return None


def db_get_documentation_and_file_details(user_request_id):
    logging.warning(f"START: db_get_documentation_and_file_details.")
    code_documentation_details = []
    try:        
        documentation_details_list = db_get_documentation_details(user_request_id)
        for documentation_details in documentation_details_list:
            user_request_details_id = documentation_details["user_request_details_id"]
            if user_request_details_id is not None:
                api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST_DETAILS}/{user_request_details_id}"
                response = requests.get(api_endpoint)
                user_request_detail = response.json()
                if user_request_detail["file_type"] == "Text":
                    file_name = user_request_detail["file_name"]
                    file_code_content = decode_blob_to_string(user_request_detail["file_content"])
                    code_documentation_details.append((file_name, file_code_content, documentation_details["documentation_file_name"], documentation_details["documentation_file_content"]))
            else:
                code_documentation_details.append((None, None, documentation_details["documentation_file_name"], documentation_details["documentation_file_content"]))
    except Exception as e:
        logging.warning(f"Error in db_get_documentation_and_file_details: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning(f"END: db_get_documentation_and_file_details.")
    return code_documentation_details


def update_database_by_dict(api_endpoint, prop_dict, method = "POST"):
    """
    Updates the database by sending a dict object to the specified API endpoint.

    Args:
        api_endpoint (str): The API endpoint URL.
        prop_dict (dict): The dictionary containing the data to be sent.

    Raises:
        Exception: If there is an error during the API call.
    """
    json_string = json.dumps(prop_dict)
    logging.warning(f"json_string: {json_string}")
    if method == "POST":
        response = requests.post(api_endpoint, data=json_string, headers={"Content-Type": "application/json"})
    else:
        response = requests.put(api_endpoint, data=json_string, headers={"Content-Type": "application/json"})
    # print(vars(response))
    if response.status_code in (200, 201):
        logging.warning(f"Inserted/Updated Successfully.")
    else:
        logging.warning(f"Error for record.")
        response.raise_for_status()


def update_database(api_endpoint, df):
    """
    Updates the database by iterating over a DataFrame and sending each row as a JSON object.

    Args:
        api_endpoint (str): The API endpoint URL.
        df (DataFrame): The DataFrame containing the data to be sent.

    Raises:
        Exception: If there is an error during the API call.
    """
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict['updated_datetime'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')        
        logging.warning(f"Row {index}: {row_dict}")
        update_database_by_dict(api_endpoint, row_dict)

def update_user_request_status(user_request_id, action_status_dict):
    """
    Updates the user request in the database.

    Args:
        df (DataFrame): The DataFrame containing the user request data.

    Raises:
        Exception: If there is an error during the update process.
    """
    logging.warning("START: update_user_request")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST}/{user_request_id}"
        logging.warning(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            response_dict = response.json()
            response_dict["zip_file_content"] = None
            response_dict.update(action_status_dict)
            
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST}/{user_request_id}"
        update_database_by_dict(api_endpoint, response_dict, "PUT")
    except Exception as e:
        # print(traceback.format_exc())
        logging.warning(f"Error in update_user_request: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning("END: update_user_request")


def update_analysis_report(df):
    """
    Updates the analysis report in the database.

    Args:
        df (DataFrame): The DataFrame containing the analysis report data.

    Raises:
        Exception: If there is an error during the update process.
    """
    logging.warning("START: update_analysis_report")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{ANALYSIS_DETAILS}/"
        update_database(api_endpoint, df)
    except Exception as e:
        logging.warning(f"Error in update_analysis_report: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning("END: update_analysis_report")

def update_documentation_report(df):
    """
    Updates the documentation report in the database.

    Args:
        df (DataFrame): The DataFrame containing the documentation report data.

    Raises:
        Exception: If there is an error during the update process.
    """
    logging.warning("START: update_documentation_report")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{DOCUMENTATION_DETAILS}/"
        update_database(api_endpoint, df)
    except Exception as e:
        logging.warning(f"Error in update_documentation_report: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning("END: update_documentation_report")

def update_conversion_report(df):
    """
    Updates the conversion report in the database.

    Args:
        df (DataFrame): The DataFrame containing the conversion report data.

    Raises:
        Exception: If there is an error during the update process.
    """
    logging.warning("START: update_conversion_report")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{CONVERSION_DETAILS}/"
        update_database(api_endpoint, df)
    except Exception as e:
        logging.warning(f"Error in update_conversion_report: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
    finally:
        logging.warning("END: update_conversion_report")


def decode_blob_to_string(blob_data):
    """
    Decodes a base64-encoded Oracle BLOB data to a string.

    Args:
        blob_data (str): The base64-encoded BLOB data.

    Returns:
        str: The decoded string.
    """
    try:
        decoded_bytes = base64.b64decode(blob_data)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        logging.warning(f"Error decoding BLOB data: {str(e)}")
        logging.warning(traceback.format_exc())
        raise
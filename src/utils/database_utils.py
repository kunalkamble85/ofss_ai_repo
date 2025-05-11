import requests
import json
import datetime
import traceback
import logging

ORDS_SERVICE_ENDPOINT = "https://apex.oraclecorp.com/pls/apex/tieaicckk"
SOURCE_LANGUAGES = "sourcelanguages"
USER_REQUEST = "userrequest"
USER_REQUEST_DETAILS = "userrequestdetails"
ANALYSIS_DETAILS = "analysisdetails"
DOCUMENTATION_DETAILS = "documentationdetails"
CONVERSION_DETAILS = "conversiondetails"


def get_language_details(code_language_id):
    logging.info(f"START: get_language_details with code_language_id={code_language_id}")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{SOURCE_LANGUAGES}/{code_language_id}"
        logging.info(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"END: get_language_details with response={data}")
            return data["code"]
        else:    
            response.raise_for_status()
    except Exception as e:
        logging.error(f"Error in get_language_details: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info(f"END: get_language_details with code_language_id={code_language_id}")


def db_get_user_request(user_request_id):
    logging.info(f"START: db_get_user_request with user_request_id={user_request_id}")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST}/{user_request_id}"
        logging.info(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            data["zip_file_content"] = None
            logging.info(f"END: db_get_user_request with response={data}")
            return data
        else:
            response.raise_for_status()            
    except Exception as e:
        logging.error(f"Error in db_get_user_request: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info(f"END: db_get_user_request with user_request_id={user_request_id}")

def db_get_user_request_details(user_request_id):
    logging.info(f"START: db_get_user_request_details with user_request_id={user_request_id}")
    try:
        query_param = '?q={"user_request_id":{"$eq":"'+str(user_request_id)+'"}}'
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{USER_REQUEST_DETAILS}/{query_param}"
        logging.info(f"Calling API: {api_endpoint}")
        response = requests.get(api_endpoint)
        if response.status_code == 200:
            data = response.json()
            # logging.info(f"END: db_get_user_request_details with response={data}")
            return data
        else:
            response.raise_for_status()            
    except Exception as e:
        logging.error(f"Error in db_get_user_request_details: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info(f"END: db_get_user_request_details with user_request_id={user_request_id}")

def update_database_by_json(api_endpoint, json_string):
    logging.info(f"json_string: {json_string}")
    response = requests.post(api_endpoint, data=json_string, headers={"Content-Type": "application/json"})
    if response.status_code == 201:
        logging.info(f"Inserted Successfully.")
    else:
        logging.error(f"Error for record.")
        response.raise_for_status()


def update_database(api_endpoint, df):
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict['updated_datetime'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        json_string = json.dumps(row_dict)
        logging.info(f"Row {index}: {json_string}")
        update_database_by_json(api_endpoint, json_string)

def update_analysis_report(df):
    logging.info("START: update_analysis_report")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{ANALYSIS_DETAILS}/"
        update_database(api_endpoint, df)
    except Exception as e:
        logging.error(f"Error in update_analysis_report: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info("END: update_analysis_report")

def update_documentation_report(df):
    logging.info("START: update_documentation_report")
    try:
        api_endpoint = f"{ORDS_SERVICE_ENDPOINT}/{DOCUMENTATION_DETAILS}/"
        update_database(api_endpoint, df)
    except Exception as e:
        logging.error(f"Error in update_documentation_report: {str(e)}")
        logging.debug(traceback.format_exc())
        raise
    finally:
        logging.info("END: update_documentation_report")
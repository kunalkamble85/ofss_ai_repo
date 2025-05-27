import time
import logging
import database_utils
import oci_utils
import requests

# EMBEDDING_TABLE_ENDPOINT = "https://m8yollkmjgtvmcu-finergyai.adb.us-ashburn-1.oraclecloudapps.com/ords/finergyai/codedocumentationembedding/"

def update_embedding_for_entry(doc_entry, embedding, cursor):
    """
    Update the documentation_details entry with the embedding and set EMBEDDED flag to True.
    Insert the entry into Oracle DB directly using the provided cursor.
    """
    try:
        doc_id = doc_entry["documentation_details_id"]
        user_request_details_id = doc_entry["user_request_details_id"]
        api_endpoint = f"{database_utils.ORDS_SERVICE_ENDPOINT}/{database_utils.USER_REQUEST_DETAILS}/{user_request_details_id}"
        response = requests.get(api_endpoint)
        user_request_detail = response.json()
        user_request_detail["file_content"] = database_utils.decode_blob_to_string(user_request_detail["file_content"])
        # Prepare values for insertion
        documentation_details_id = doc_id
        user_request_id = doc_entry["user_request_id"]
        code_file_name = user_request_detail["file_name"]
        code_file_content = user_request_detail["file_content"]
        documentation_file_name = doc_entry["documentation_file_name"]
        documentation_file_content = doc_entry["documentation_file_content"]

        # Convert embedding (list of floats) to a string representation for insertion
        # Example: store as comma-separated string
        # if isinstance(embedding, list):
        #     documentation_embedding = ",".join(str(float(x)) for x in embedding)
        # else:
        documentation_embedding = str(embedding)

        insert_sql = """
            INSERT INTO CODE_DOCUMENTATION_EMBEDDING (
                DOCUMENTATION_DETAILS_ID,
                USER_REQUEST_ID,
                CODE_FILE_NAME,
                DOCUMENTATION_FILE_NAME,
                DOCUMENTATION_EMBEDDING,
                CODE_FILE_CONTENT,
                DOCUMENTATION_FILE_CONTENT
            ) VALUES (:1, :2, :3, :4, :5, :6, :7)
        """
        # Note: Place LOB columns (CODE_FILE_CONTENT, DOCUMENTATION_FILE_CONTENT) at the end of the insert and bind order
        cursor.execute(
            insert_sql,
            (
                documentation_details_id,
                user_request_id,
                code_file_name,
                documentation_file_name,
                documentation_embedding,
                code_file_content,
                documentation_file_content
            )
        )
        logging.warning(f"Inserted embedding for documentation_details_id={doc_id} into Oracle DB")
    except Exception as e:
        logging.warning(f"Error updating embedding for documentation_details_id={doc_entry['documentation_details_id']}: {str(e)}")

def main():
    logging.warning("Starting embedding job loop.")
    
    while True:
        conn = None
        cursor = None
        try:
            # Check for start_batch flag
            try:
                with open("./config/start_batch", "r") as f:
                    flag = f.read().strip().lower()
                if flag not in ["yes", "true", "y", "1"]:
                    logging.warning("start_batch flag is not 'yes'. Pausing embedding job loop.")
                    time.sleep(30)
                    continue
            except Exception as e:
                logging.warning(f"Could not read start_batch flag file: {str(e)}. Pausing embedding job loop.")
                time.sleep(30)
                continue

            pending_entries = database_utils.db_get_documentation_for_embedding()
            if pending_entries:                
                id_text_map = {entry["documentation_details_id"]: entry["documentation_file_content"] for entry in pending_entries if entry.get("documentation_file_content") and entry.get("user_request_details_id")}
                if id_text_map:
                    logging.warning(f"Found {len(id_text_map)} documentation entries pending embedding.")
                    embeddings = oci_utils.generate_embeddings(id_text_map)
                    # Get connection and cursor once for all entries
                    conn = database_utils.get_oracle_connection()
                    cursor = conn.cursor()
                    # embeddings is a dict: id -> embedding
                    for entry in pending_entries:
                        doc_id = entry.get("documentation_details_id")
                        if doc_id and doc_id in embeddings:
                            update_embedding_for_entry(entry, embeddings[doc_id], cursor)
                            database_utils.update_documentation_details_embedding_status(doc_id)
                    conn.commit()
                else:
                    logging.warning("No documentation entries pending embedding.")
            else:
                logging.warning("No documentation entries pending embedding.")
        except Exception as e:
            logging.warning(f"Exception in embedding job loop: {str(e)}")
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            # break
        time.sleep(30)

if __name__ == "__main__":
    main()

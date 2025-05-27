import oci
import logging

compartment_id = "ocid1.compartment.oc1..aaaaaaaacqxr3j2qbhntidg2s32gb67lv7ydpbfkvcazqvnjfsaxj3vdxr7a"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('./config/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.uk-london-1.oci.oraclecloud.com"
model_endpoint_map = {"meta.llama3.1-70b":"ocid1.generativeaimodel.oc1.uk-london-1.amaaaaaask7dceyarp4fbl4nicr66ibhaqqxg5w77nnzlgmof5hinslboika",
                      "meta.llama3.3-70b":"ocid1.generativeaimodel.oc1.uk-london-1.amaaaaaask7dceyach2dyu6g5w5ocnvbkto2g76wxitj3rpddplsqoxqh2lq",
                      "meta.llama3.1-405b": "ocid1.generativeaiendpoint.oc1.uk-london-1.amaaaaaah7afz4ia4s7lwl5qt7bmupjqknwyvwbfpi7id3onks5rdaga2v5a",
                      "cohere.command-r-plus":"ocid1.generativeaimodel.oc1.uk-london-1.amaaaaaask7dceya5umoptfnq5yg7w2l5lte3fjpism64ismzmyehfcdh5cq",
                      "cohere.command-r":"ocid1.generativeaimodel.oc1.uk-london-1.amaaaaaask7dceyahpidcahiiyhcdmnvicfxo7suq3pxcimkyik75mbxziqq",
                      "cohere.embed-english":""}


generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
chat_detail = oci.generative_ai_inference.models.ChatDetails()
   

def generate_oci_gen_ai_response(model, messages):
    logging.debug(messages)
    if model.startswith("cohere.command"):
        logging.info(f"Sending request to model cohere Command model {model}")
        return handle_cohere_model_request(model, messages)
    else:
        logging.info(f"Sending request to model Meta Llama model {model}")
        return handle_llama_model_request(model, messages)


def handle_llama_model_request(model, messages):
    model_id=model_endpoint_map.get(model)
    all_oci_messages = []
    for message in messages:
        role = message["role"].upper()
        content = message["content"]
        oci_content = oci.generative_ai_inference.models.TextContent()
        oci_content.text = content
        oci_message = oci.generative_ai_inference.models.Message()
        oci_message.role = role
        oci_message.content = [oci_content]
        all_oci_messages.append(oci_message)

    chat_request = oci.generative_ai_inference.models.GenericChatRequest()
    chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    chat_request.messages = all_oci_messages
    if model == "meta.llama3-70b":
        chat_request.max_tokens = 4000
    else:
        chat_request.max_tokens = 4000
    chat_request.temperature = 0.1
    chat_request.frequency_penalty = 0
    chat_request.presence_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = -1

    if model =="meta.llama3.1-405b":
        chat_detail.serving_mode = oci.generative_ai_inference.models.DedicatedServingMode(endpoint_id=model_id)
    else:
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response = chat_response.data.chat_response.choices[0].message.content[0].text
    logging.info(f"Got Response from {model}.")
    return response

def handle_cohere_model_request(model, messages):
    model_id=model_endpoint_map.get(model)
    message_history = []
    for message in messages:
        role = message["role"].upper()
        content = message["content"]
        if role == "USER":
            message_history.append({"role":"USER" , "message": content})
        else:
            message_history.append({"role":"CHATBOT" , "message":content})
    user_last_message = message_history[-1]["message"]
    message_history =message_history[:-1]
    
    chat_request = oci.generative_ai_inference.models.CohereChatRequest()
    chat_request.message = user_last_message
    chat_request.max_tokens = 4000
    chat_request.temperature = 0.1
    chat_request.frequency_penalty = 0
    chat_request.top_p = 0.75
    chat_request.top_k = 0
    chat_request.chat_history = message_history

    chat_detail = oci.generative_ai_inference.models.ChatDetails()
    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=model_id)
    chat_detail.chat_request = chat_request
    chat_detail.compartment_id = compartment_id
    chat_response = generative_ai_inference_client.chat(chat_detail)
    response = chat_response.data.chat_response.chat_history[-1].message
    logging.info(f"Got Response from {model}.")
    return response


def generate_embeddings(inputs):
    """
    Generates embeddings for a list of input texts using OCI Generative AI Inference.
    Handles a maximum of 96 inputs at a time.

    Args:
        inputs (dict): Dictionary mapping id to text to generate embeddings for.

    Returns:
        dict: Dictionary mapping id to embedding.
    """
    logging.warning("START: generate_embeddings")
    logging.info(f"Input Length for embedding: {len(inputs)}")
    max_batch_size = 96
    embeddings_dict = {}

    # Convert dict to list of (id, text) tuples
    items = list(inputs.items())

    # Process inputs in batches of max_batch_size
    for i in range(0, len(items), max_batch_size):
        batch = items[i:i+max_batch_size]
        ids = [item[0] for item in batch]
        texts = [item[1] for item in batch]
        embed_text_detail = oci.generative_ai_inference.models.EmbedTextDetails()
        embed_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="cohere.embed-english-v3.0")
        embed_text_detail.inputs = texts
        embed_text_detail.truncate = "NONE"
        embed_text_detail.compartment_id = compartment_id
        embed_text_response = generative_ai_inference_client.embed_text(embed_text_detail)
        logging.info("Received embedding response from OCI Generative AI Inference.")
        logging.info(f"Number of embeddings generated in batch: {len(embed_text_response.data.embeddings)}")
        if embed_text_response.data.embeddings:
            logging.info(f"First embedding in batch: {embed_text_response.data.embeddings[0]}")
        # Map each id to embedding
        for id_val, embedding in zip(ids, embed_text_response.data.embeddings):
            embeddings_dict[id_val] = embedding

    logging.warning("END: generate_embeddings")
    return embeddings_dict

# inputs = {1:"Hello, How Are you?", 2:"I am Kunal"}
# print(generate_embeddings(inputs))

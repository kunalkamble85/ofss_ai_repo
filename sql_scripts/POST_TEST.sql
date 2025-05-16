DECLARE
    l_response_clob      CLOB;
    l_request_body       CLOB;
    l_api_url            VARCHAR2(1000);
    l_user_request_id    NUMBER;
    l_test_mode_input    VARCHAR2(10);
    l_test_mode_boolean  BOOLEAN;
    l_additional_context VARCHAR2(1000);
BEGIN
    l_api_url := 'https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/generate_analysis/';
    l_user_request_id    := 1;
    l_test_mode_input    := 'TRUE';
    l_additional_context := '';
    IF UPPER(l_test_mode_input) IN ('TRUE', 'Y', '1') THEN
        l_test_mode_boolean := TRUE;
    ELSE
        l_test_mode_boolean := FALSE;
    END IF;

    apex_web_service.g_request_headers(1).name  := 'Content-Type';
    apex_web_service.g_request_headers(1).value := 'application/json';

    apex_json.initialize_clob_output;
    apex_json.open_object;
    apex_json.write('user_request_id', l_user_request_id);
    apex_json.write('test_mode', l_test_mode_boolean);
    apex_json.write('additional_context', l_additional_context);
    apex_json.close_object;
    l_request_body := apex_json.get_clob_output;
    apex_json.free_output;

    l_response_clob := apex_web_service.make_rest_request(
        p_url         => l_api_url,
        p_http_method => 'POST',
        p_body        => l_request_body
    );
    htp.p(l_response_clob);
END;
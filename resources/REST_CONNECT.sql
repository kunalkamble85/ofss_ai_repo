DECLARE
  l_clob    CLOB;
  l_buffer  VARCHAR2(32767);
  l_amount  NUMBER := 32000;
  l_offset  NUMBER := 1;
  l_json    VARCHAR2(32767);
  l_status  VARCHAR2(100); -- example parameter from JSON
BEGIN
  -- Make REST request
  l_clob := apex_web_service.make_rest_request(
              p_url => 'https://finergy-ai.sniadprshared1.gbucdsint02iad.oraclevcn.com:9300/',
              p_http_method => 'GET');

  -- Read CLOB response into string
  BEGIN
    LOOP
      dbms_lob.read(l_clob, l_amount, l_offset, l_buffer);
      l_json := l_json || l_buffer;
      l_offset := l_offset + l_amount;
    END LOOP;
  EXCEPTION
    WHEN no_data_found THEN
      NULL;
  END;

  -- Parse JSON using APEX_JSON
  APEX_JSON.parse(l_json);

  -- Extract JSON value (example: $.status or $.data.id, etc.)
  l_status := APEX_JSON.get_varchar2(p_path => 'message'); -- adjust the path based on actual JSON structure

  -- Print the value
  htp.p('Message from JSON: ' || l_status);
  
  -- Cleanup
--   APEX_JSON.FREE;
END;

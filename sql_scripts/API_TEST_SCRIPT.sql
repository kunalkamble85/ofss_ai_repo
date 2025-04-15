DECLARE
  l_clob    CLOB;
  l_buffer  VARCHAR2(32767);
  l_amount  NUMBER := 32000;
  l_offset  NUMBER := 1;
  l_json    VARCHAR2(32767);
  l_status  VARCHAR2(100); -- example parameter from JSON
BEGIN
  -- Parse JSON using APEX_JSON
--   l_json := '{"message": "Welcome"}'; -- OUTPUT FROM REST
  l_json := '{"file_name":"test_name","number_of_lines":"5", "number_of_lines_no_doc":"3", "tokens":"100", "tokens_no_doc":"80"}'; -- OUTPUT FROM REST
  APEX_JSON.parse(l_json);

  -- Extract JSON value (example: $.status or $.data.id, etc.)
  l_status := APEX_JSON.get_varchar2(p_path => 'number_of_lines'); -- adjust the path based on actual JSON structure

  -- Print the value
  htp.p('Message from JSON: ' || l_status);
END;
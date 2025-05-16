DECLARE
  l_clob clob;
  l_buffer         varchar2(32767);
  l_amount         number;
  l_offset         number;
BEGIN

  l_clob := apex_web_service.make_rest_request(
              p_url => 'https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/',
              p_http_method => 'GET');

    l_amount := 32000;
    l_offset := 1;
    BEGIN
        LOOP
            dbms_lob.read( l_clob, l_amount, l_offset, l_buffer );
            htp.p(l_buffer);
            l_offset := l_offset + l_amount;
            l_amount := 32000;
        END LOOP;
    EXCEPTION
        WHEN no_data_found THEN
            NULL;
    END;
END;


select apex_web_service.make_rest_request(
    p_url         => 'https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/',
    p_http_method => 'GET'
) from dual;
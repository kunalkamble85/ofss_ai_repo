import unittest
import oci_util

class TestOciUtil(unittest.TestCase):

    def test_handle_llama33_model_request(self):
        messages = [{"role": "user", "content": "Hello"}]
        response = oci_util.generate_oci_gen_ai_response("meta.llama3.3-70b", messages)
        print(response)
        self.assertEqual(False, response == "")

    def test_handle_cohere_model_request(self):
        messages = [{"role": "user", "content": "Hello"}]
        response = oci_util.generate_oci_gen_ai_response("cohere.command-r", messages)
        print(response)
        self.assertEqual(False, response == "")

    def test_handle_llama31_model_request(self):
        messages = [{"role": "user", "content": "Hello"}]
        response = oci_util.generate_oci_gen_ai_response("meta.llama3.1-70b", messages)
        print(response)
        self.assertEqual(False, response == "")

    def test_handle_cohere_p_model_request(self):
        messages = [{"role": "user", "content": "Hello"}]
        response = oci_util.generate_oci_gen_ai_response("cohere.command-r-plus", messages)
        print(response)
        self.assertEqual(False, response == "")

if __name__ == '__main__':
    unittest.main()
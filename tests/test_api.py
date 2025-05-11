import requests
url = "https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/generate_analysis"
url = "https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/generate_documentation"
url = "https://ehagexkm6mf2ngjogvtvksf2sm.apigateway.us-ashburn-1.oci.customer-oci.com/finergy-ai/generate_conversion"

headers = {"Content-Type": "application/json"}
data = {
    "user_request_id": 1,
    "test_mode": True,
    "additional_context": None
}
response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")


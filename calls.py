import http.client

conn = http.client.HTTPSConnection("zabbix.yelpcorp.com")

payload = "{\n    \"jsonrpc\": \"2.0\",\n    \"method\": \"user.login\",\n    \"params\": {\n        \"user\": \"svc-zabbix\",\n        \"password\": \"28uBRjiiqIutpODn3SZo\"\n    },\n    \"id\": 1,\n    \"auth\": null\n}"

headers = {
    'content-type': "application/json-rpc",
    'cache-control': "no-cache",
    'postman-token': "7a202916-b04d-4a29-ee0a-126b0f7e9dea"
    }

conn.request("POST", "/api_jsonrpc.php", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

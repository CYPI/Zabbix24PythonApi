#!/usr/bin/env python

import requests
import json

url = "https://zabbix.yelpcorp.com/api_jsonrpc.php"
secrets = open('secrets.json').read()

def auth(creds):
  headers = {
    'content-type': "application/json-rpc",
    'cache-control': "no-cache",
    'postman-token': "561fd14a-0622-1d41-4c60-d7582b740e5e"
    }
  response = requests.request("POST", url, data=creds, headers=headers)
  return response

def main():
  print(auth(secrets).text)

if __name__ == '__main__':
    main()

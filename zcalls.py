#!/usr/bin/env python
import requests
import json

zabbix_server = 'https://zabbix.yelpcorp.com/api_jsonrpc.php'
secrets_file = 'secrets.json'


secrets = open(secrets_file).read()


def auth_token(auth):

  resp = requests.post(zabbix_server,
                     data=auth,
                     headers={'Content-Type':'application/json'},)
  return resp

def main():
  print auth_token(secrets)

if __name__ == '__main__':
    main()

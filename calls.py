#!/usr/bin/env python

import requests
import json
import time
import re

api = "https://zabbix.yelpcorp.com/api_jsonrpc.php"
secrets = open('secrets.json').read()
headers = {
  'content-type': "application/json-rpc",
  'cache-control': "no-cache",
  'postman-token': "561fd14a-0622-1d41-4c60-d7582b740e5e"
  }


def get_token(creds):
  try:
    response = requests.request("POST", api, data=creds, headers=headers)
  except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
  else:
    try:
      return json.loads(response.text)
    except:
      print 'problem getting a token'


def get_host_id(host):
    hostid = re.sub("host:", "", host, count=1)
    token = get_token(secrets)
    data = {
      'jsonrpc': '2.0',
      'method': 'host.get',
      'params': {
                  'output': 'extend',
                  'filter': {
                              'host': [hostid]
                            }
                },
      'auth': token['result'],
      'id': token['id'],
      }
    response = requests.request("POST", api, data=json.dumps(data), headers=headers)
    response_formated = json.loads(response.text)
    return response_formated['result'][0]['hostid']


def get_group_id(group):
    groupid = re.sub("group:", "", group, count=1)
    token = get_token(secrets)
    data = {
      'jsonrpc': '2.0',
      'method': 'hostgroup.get',
      'params': {
                  'output': 'extend',
                  'filter': {
                              'name': [groupid]
                            }
                },
      'auth': token['result'],
      'id': token['id'],
      }
    try:
      response = requests.request("POST", api, data=json.dumps(data), headers=headers)
      response_formated = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print 'error:' + e
        sys.exit(1)
    else:
      try:
        return response_formated['result'][0]['groupid']
      except:
        print 'error getting groupid for: ' + group


def get_maintenance_id(host_group):
  if re.search('group:', host_group):
        group_type = 'groupids'
        hostid = get_group_id(host_group)
  else:
        group_type = 'hostids'
        hostid = get_host_id(host_group)

  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.get',
      'params': {
          'output': 'extend',
          'selectHosts': 'extend',
          'selecttimeperiods': 'extend',
          group_type: hostid,
      },
      'auth': token['result'],
      'id': token['id'],
  }
  try:
    response = requests.request("POST", api, data=json.dumps(data), headers=headers)
    response_formated = json.loads(response.text)
  except requests.exceptions.RequestException as e:
    print 'error:' + e
    sys.exit(1)
  else:
    try:
      return response_formated['result'][0]['maintenanceid']
    except:
      print 'No maintenance for host: ' + host


def get_maintenance_name(host_group):
  if re.search('group:', host_group):
        group_type = 'groupids'
        hostid = get_group_id(host_group)
  else:
        group_type = 'hostids'
        hostid = get_host_id(host_group)

  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.get',
      'params': {
          'output': 'extend',
          'selectHosts': 'extend',
          'selecttimeperiods': 'extend',
          group_type: hostid
      },
      'auth': token['result'],
      'id': token['id'],
  }
  try:
    response = requests.request("POST", api, data=json.dumps(data), headers=headers)
    response_formated = json.loads(response.text)
  except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
  else:
    try:
      return response_formated['result'][0]['name']
    except:
      print 'No maintenance for host: ' + host


def del_maintenance(host):
  mid = get_maintenance_id(host)
  maintenance_name = get_maintenance_name(host)
  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.delete',
      'params': [mid],
      'auth': token['result'],
      'id': token['id'],
  }
  try:
    requests.request("POST", api, data=json.dumps(data), headers=headers)
  except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
  else:
      return 'maintenance: ' + maintenance_name + ' was deleted for host: ' + host


def start_maintenance(host_group,howlong):
  if re.search('group:', host_group):
    group_type = 'groupids'
    hostid = get_group_id(host_group)
  else:
    group_type = 'hostids'
    hostid = get_host_id(host_group)

  now = int(time.time())
  until = '1594080000'  # 07/07/2020 @ 12:00am (UTC)
  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.create',
      'params': {
          'name': 'pause_' + group_type,
          'active_since': now,
          'active_till': until,
          group_type: [hostid],
          'timeperiods': [
              {
            'timeperiod_type': 0,
            'period': howlong*3600,
              }
          ],
      },
      'auth': token['result'],
      'id': token['id'],
  }
  try:
    requests.request("POST", api, data=json.dumps(data), headers=headers)
  except requests.exceptions.RequestException as e:
    print e
    sys.exit(1)
  else:
      return 'maintenance pause_' + group_type + ' was created for: ' + group_type


def main():
#     print(start_maintenance('group:pao',1))
#    print(get_maintenance_id('group:pao'))
#    print(get_maintenance_name('host:paoad1'))
    print(del_maintenance('group:pao'))
#    print(get_host_id('PAOAD1'))
#    print(start_maintenance('PAOAD1', 1))

if __name__ == '__main__':
    main()

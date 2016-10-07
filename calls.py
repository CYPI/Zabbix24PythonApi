#!/usr/bin/env python

import argparse
import json
import requests
import re
import time

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
      raise Exception ('problem getting a token')


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
        raise Exception ('error getting groupid for: ' + group)


def get_maintenance_group_id(group):

  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.get',
      'params': {
          'output': 'extend',
          'selectHosts': 'extend',
          'selecttimeperiods': 'extend',
          'groupids': get_group_id(group),
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
      raise Exception ('No maintenance for group: ' + group)


def get_maintenance_host_id(host):

  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.get',
      'params': {
          'output': 'extend',
          'selectHosts': 'extend',
          'selecttimeperiods': 'extend',
          'hostids': get_host_id(host),
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
      raise Exception ('No maintenance for host: ' + host)


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
      raise Exception ('No maintenance for host: ' + host_group)


def del_maintenance(args):
  if args.group:
      mid = get_maintenance_group_id(args.group)
      maintenance_name = get_maintenance_name('group:' + args.group)
  elif args.host:
      mid = get_maintenance_host_id(args.host)
      maintenance_name = get_maintenance_name('host:' + args.host)
  else:
      raise Exception('please provide a host name or a group name')

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
      return 'maintenance: ' + maintenance_name + 'was deleted successfully'


def start_maintenance_host(args):
  if args.host:
      hostid = get_host_id(args.host)
  else:
      raise Exception('please provide an host name')
  if args.howlong:
      howlong = args.howlong
  else:
      raise Exception('please provide a maintenance duration in hours')

  now = int(time.time())
  until = '1594080000'  # 07/07/2020 @ 12:00am (UTC)
  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.create',
      'params': {
          'name': 'pause_' + args.host,
          'active_since': now,
          'active_till': until,
          'hostids': [hostid],
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
      return 'maintenance pause_' + args.host + ' was created for: ' + args.host


def start_maintenance_group(args):
  if args.group:
      groupid = get_group_id(args.group)
  else:
      raise Exception('please provide a group name')
  if args.howlong:
      howlong = args.howlong
      print howlong
  else:
      raise Exception('please provide a maintenance duration in hours')


  now = int(time.time())
  until = '1594080000'  # 07/07/2020 @ 12:00am (UTC)
  token = get_token(secrets)
  data = {
      'jsonrpc': '2.0',
      'method': 'maintenance.create',
      'params': {
          'name': 'pause_' + args.group,
          'active_since': now,
          'active_till': until,
          'groupids': [groupid],
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
      return 'maintenance group pause_' + args.group + ' was created for: ' + args.group


def cli_root_check(args):
    if (args.pause and args.host and args.howlong):
        print(start_maintenance_host(args))
    elif (args.pause and args.group and args.howlong):
        print(start_maintenance_group(args))
    elif (args.unpause):
        print(del_maintenance(args))
    else:
        raise Exception('please select an host or a group and a time during')


def main():
    """Command-line options"""
    app_caption = 'Zabbix api calls'
    arg_caption_pause = 'Create a maintenance period for a host or group'
    arg_caption_unpause = 'Delete a maintenance period for a host or group'
    arg_caption_host = 'Host name'
    arg_caption_group = 'Group name'
    arg_caption_howlong = 'how long the maintenance will be for in hours'


    parser = argparse.ArgumentParser(description=app_caption)
    parser.add_argument('--pause', action='store_true',
                        help=arg_caption_pause)
    parser.add_argument('--unpause', action='store_true',
                        help=arg_caption_unpause)
    parser.add_argument('--host', type=str,
                        help=arg_caption_host)
    parser.add_argument('--group', type=str,
                        help=arg_caption_group)
    parser.add_argument('--howlong', type=int,
                        help=arg_caption_howlong)

    args = parser.parse_args()
    cli_root_check(args)
#     print(start_maintenance('group:pao',1))
#    print(get_maintenance_id('group:pao'))
#    print(get_maintenance_name('host:paoad1'))
#    print(del_maintenance('group:pao'))
#    print(get_host_id('PAOAD1'))
#    print(start_maintenance('PAOAD1', 1))

if __name__ == '__main__':
    main()

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
    method = 'host.get'
    params = {
                  'output': 'extend',
                  'filter': {
                              'host': [hostid]
                            }
                }
    response = 'host_id'
    exception = ''
    return apicall(method, params, response, exception)


def get_group_id(group):
    groupid = re.sub("group:", "", group, count=1)
    token = get_token(secrets)
    method = 'hostgroup.get'
    params = {
                  'output': 'extend',
                  'filter': {
                              'name': [groupid]
                            }
                }
    response = 'group_id'
    exception = ''
    return apicall(method, params, response, exception)


def apicall(method, params, response, exception):

    token = get_token(secrets)

    data = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'auth': token['result'],
            'id': token['id'],
            }
    try:
        responsecall = requests.request("POST", api, data=json.dumps(data), headers=headers)
        response_formated = json.loads(responsecall.text)
    except requests.exceptions.RequestException as e:
        print 'error:' + e
        sys.exit(1)
    else:
        try:
            if response == 'maintenance_id':
                return response_formated['result'][0]['maintenanceid']
            elif response == 'maintenance_name':
                return response_formated['result'][0]['name']
            elif response == 'host_id':
                return response_formated['result'][0]['hostid']
            elif response == 'group_id':
                return response_formated['result'][0]['groupid']
            else:
                return response
        except:
            raise Exception(exception)


class Maintenance(object):

    def __init__(self, args):

        self.args = args

    @staticmethod
    def get_maintenance_group_id(group):
        method = 'maintenance.get'
        params = {
                'output': 'extend',
                'selectHosts': 'extend',
                'selecttimeperiods': 'extend',
                'groupids': get_group_id(group),
                }
        response = 'maintenance_id'
        exception = 'No maintenance for group: ' + group

        return apicall(method, params, response, exception)

    @staticmethod
    def get_maintenance_name(host_group):
        if re.search(r'group:', host_group):
            group_type = 'groupids'
            hostid = get_group_id(host_group)
        else:
            group_type = 'hostids'
            hostid = get_host_id(host_group)

        method = 'maintenance.get'
        params = {
                'output': 'extend',
                'selectHosts': 'extend',
                'selecttimeperiods': 'extend',
                group_type: hostid
                }
        response = 'maintenance_name'
        exception = 'No maintenance for host: ' + host_group
        return apicall(method, params, response, exception)

    @staticmethod
    def get_maintenance_host_id(host):
        method = 'maintenance.get'
        params = {
            'output': 'extend',
            'selectHosts': 'extend',
            'selecttimeperiods': 'extend',
            'hostids': get_host_id(host),
            }
        exception = 'No maintenance for host: ' + host
        return apicall(method, params, 'maintenance_id', exception)

    def del_maintenance(self):
        if self.args.group:
            mid = self.get_maintenance_group_id(self.args.group)
            maintenance_name = self.get_maintenance_name('group:' + self.args.group)
        elif self.args.host:
            mid = self.get_maintenance_host_id(self.args.host)
            maintenance_name = self.get_maintenance_name('host:' + self.args.host)
        else:
            raise Exception('please provide a host name or a group name')
        method = 'maintenance.delete'
        params = [mid]
        response = 'maintenance: ' + maintenance_name + ' was deleted successfully'
        exception = ''
        return apicall(method, params, response, exception)

    def start_maintenance_host(self):
        if self.args.host:
            hostid = get_host_id(self.args.host)
        else:
            raise Exception('please provide an host name')
        if self.args.hours:
            howlong = self.args.hours
        else:
            raise Exception('please provide a maintenance duration in hours')

        now = int(time.time())
        until = '1594080000'  # 07/07/2020 @ 12:00am (UTC)
        method = 'maintenance.create'
        params = {
                'name': 'pause_' + self.args.host,
                'active_since': now,
                'active_till': until,
                'hostids': [hostid],
                'timeperiods': [
                    {
                    'timeperiod_type': 0,
                    'period': howlong*3600,
                    }
                ],
            }
        response = 'maintenance pause_' + self.args.host + ' was created for: ' + self.args.host
        exception = ''
        return apicall(method, params, response, exception)

    def start_maintenance_group(self):
        if self.args.group:
            groupid = get_group_id(self.args.group)
        else:
            raise Exception('please provide a group name')
        if self.args.hours:
            howlong = self.args.hours
            print howlong
        else:
            raise Exception('please provide a maintenance duration in hours')

        now = int(time.time())
        until = '1594080000'  # 07/07/2020 @ 12:00am (UTC)
        method = 'maintenance.create'
        params = {
                'name': 'pause_' + self.args.group,
                'active_since': now,
                'active_till': until,
                'groupids': [groupid],
                'timeperiods': [
                    {
                    'timeperiod_type': 0,
                    'period': howlong*3600,
                    }
                ],
            }
        response = 'maintenance group pause_' + self.args.group + ' was created for: ' + self.args.group
        exception = ''
        return apicall(method, params, response, exception)


def argument_check(args):
    if args.pause and args.host and args.hours:
        pause_host = Maintenance(args)
        print(pause_host.start_maintenance_host())
    elif args.pause and args.group and args.hours:
        pause_group = Maintenance(args)
        print(pause_group.start_maintenance_group())
    elif args.unpause:
        unpause = Maintenance(args)
        print(unpause.del_maintenance())
    else:
        raise Exception('please select an host or a group and a time during')


def main():

    app_caption = 'Zabbix api calls'
    arg_caption_pause = 'Create a maintenance period for a host or group'
    arg_caption_unpause = 'Delete a maintenance period for a host or group'
    arg_caption_host = 'Host name'
    arg_caption_group = 'Group name'
    arg_caption_hours = 'how long the maintenance will be for in hours'

    parser = argparse.ArgumentParser(description=app_caption)
    parser.add_argument('--pause', action='store_true',
                        help=arg_caption_pause)
    parser.add_argument('--unpause', action='store_true',
                        help=arg_caption_unpause)
    parser.add_argument('--host', type=str,
                        help=arg_caption_host)
    parser.add_argument('--group', type=str,
                        help=arg_caption_group)
    parser.add_argument('--hours', type=int,
                        help=arg_caption_hours)

    args = parser.parse_args()
    argument_check(args)

if __name__ == '__main__':
    main()

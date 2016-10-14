#!/usr/bin/env python

import argparse
import datetime
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
    return apicall(method, params, 'hostid')


def get_group_id(group):
    groupid = re.sub("group:", "", group, count=1)
    method = 'hostgroup.get'
    params = {
                  'output': 'extend',
                  'filter': {
                              'name': [groupid]
                            }
                }
    return apicall(method, params, 'groupid')


def apicall(method, params, response, exception=''):

    token = get_token(secrets)

    response_options = ['maintenanceid', 'name', 'hostid', 'groupid']

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
            if response in response_options:
                return response_formated['result'][0][response]
            elif response == 'eventid':
                events = []
                for event in response_formated['result']:
                    if not event['acknowledges']:
                        events.append(event['eventid'])
                print events
                return events
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
        exception = 'No maintenance for group: ' + group
        return apicall(method, params, 'maintenanceid', exception)

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
        return apicall(method, params, 'maintenanceid', exception)

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
        return apicall(method, params, response, '')

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
        return apicall(method, params, response)

    def start_maintenance_group(self):
        if self.args.group:
            groupid = get_group_id(self.args.group)
        else:
            raise Exception('please provide a group name')
        if self.args.hours:
            howlong = self.args.hours
        else:
            raise Exception('please provide a maintenance duration in hours')

#        now = int(time.time())
        now = datetime.datetime.now()
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
        return apicall(method, params, response)


def acknowledge_trigger(args):
#    now = datetime.datetime.fromtimestamp(time.time()).strftime('%d/%m/%Y')
#    nowtimestamp = time.mktime(datetime.datetime.strptime(now, "%d/%m/%Y").timetuple())
#    timefrom = '1476304253'  # Wed, 12 Oct 2016 20:30:53 GMT
    method = 'event.get'
    params = {
        'output': 'extend',
        'select_acknowledges': 'extend',
        'objectids': args.trigger,
#        'time_from': timefrom,
#        'time_till': nowtimestamp,
        'sortfield': ['clock', 'eventid'],
        'sortorder': 'DESC'
        }
    events = apicall(method, params, 'eventid')
    for event in events:
        i = 0
        while i <= 10:
            print (acknowledge_event(event, args.m))
            i += 1
    return 'all events for trigger: ' + args.trigger + 'have been ack.'


def acknowledge_event(eventid, message=''):

    method = 'event.acknowledge'
    params = {
        'eventids': eventid,
        'message': message
        }
    response = 'alert ' + str(eventid) + ' has been ack sucessfully.'
    return apicall(method, params, response)


def argument_check(args):
    pause = Maintenance(args)
    if args.pause:
        if args.host and args.hours:
            print(pause.start_maintenance_host())
        elif args.group and args.hours:
            print(pause.start_maintenance_group())
    elif args.unpause:
        print(pause.del_maintenance())
    elif args.ackevent:
        eventid = args.ackevent
        if args.m:
            print(acknowledge_event(eventid, args.m))
        else:
            print(acknowledge_event(eventid))
    elif args.acktrigger:
        print(acknowledge_trigger(args))
    else:
        raise Exception('please select an host or a group and a time during')


def main():

    app_caption = 'Zabbix api calls'
    arg_caption_pause = 'Create a maintenance period for a host or group'
    arg_caption_unpause = 'Delete a maintenance period for a host or group'
    arg_caption_host = 'Host name'
    arg_caption_group = 'Group name'
    arg_caption_hours = 'how long the maintenance will be for in hours'
    arg_caption_trigger = 'shows trigger events'
    arg_caption_ackevent = 'ack event'
    arg_caption_acktrigger = 'ack trigger'
    arg_caption_m = 'ack comment'

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
    parser.add_argument('--trigger', type=int,
                        help=arg_caption_trigger)
    parser.add_argument('--ackevent', type=int,
                        help=arg_caption_ackevent)
    parser.add_argument('--acktrigger', type=int,
                        help=arg_caption_acktrigger)
    parser.add_argument('--m', type=str,
                        help=arg_caption_m)


    args = parser.parse_args()
    argument_check(args)

if __name__ == '__main__':
    main()

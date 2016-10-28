# Zabbix24PythonApi
Zabbix 2.4 api python script

This script let's you create Zabbix maintenance period for a host or a group of hosts.
It allows you to acknowledge events as well.

#configuration

in zabbix.py, add your zabbix server's fqdn:

  api = "https://<<zabbixserver_fqdn>>/api_jsonrpc.php"
  
in secrets.json, add a username and password with api permissions:

{
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": "<username>",
        "password": "<password>"
    },
    "id": 1,
    "auth": null
}

#optional arguments:

  -h, --help           show this help message and exit
  
  --pause              Create a maintenance period for a host or group
  
  --unpause            Delete a maintenance period for a host or group
  
  --host HOST          Host name
  
  --group GROUP        Group name
  
  --hours HOURS        how long the maintenance will be for in hours
  
  --ack                eventid that you want to acknowledge
  
  --m                  acknowledge comment
  
  
  
  e.g
  
  $python calls.py --pause --host paoad1 --hours 1
  
  $python calls.py --pause --group PAO --hours 2
  
  $python calls.py --unpause --group PAO
  
  $python calls.py --ack 9287242 --m "issue resolved"


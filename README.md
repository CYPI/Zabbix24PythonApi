# Zabbix24PythonApi
Zabbix 2.4 api python script

optional arguments:
  -h, --help           show this help message and exit
  --pause              Create a maintenance period for a host or group
  --unpause            Delete a maintenance period for a host or group
  --host HOST          Host name
  --group GROUP        Group name
  --hours HOURS        how long the maintenance will be for in hours
  --ackevent ACKEVENT  ack event
  --m M                ack comment
  
  
  e.g
  $python calls.py --pause --host paoad1 --hours 1
  $python calls.py --pause --group PAO --hours 2
  $python calls.py --unpause --group PAO
  $python calls.py --ack 9287242 --m "issue resolved"


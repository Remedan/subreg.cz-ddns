#!/usr/bin/env python3

'''
Uses the subreg.cz API to update the specified record to current public IP.

Copyright 2019 Vojtech Balak

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from sys import stderr
from urllib import request
from configparser import ConfigParser

from zeep import Client


def check_response(response):
    '''
    Checks the API response for errors. If error is returned, prints it
    and stops script execution.
    '''
    if response['status'] == 'error':
        print('SOAP Error: '+response['error']['errormsg'], file=stderr)
        exit(1)


def get_record_id(client, ssid, domain, subdomain):
    '''
    Returns the record id from the DNS zone or None.
    '''
    record_id = None
    old_ip = None
    response = client.service.Get_DNS_Zone(ssid=ssid, domain=domain)
    check_response(response)
    for record in response['data']['records']:
        if record['name'] == subdomain and record['type'] == 'A':
            record_id = record['id']
            old_ip = record['content']

    return (record_id, old_ip)


def update_record(user, password, domain, subdomain='', ):
    '''
    Creates or updates a dns record pointing to the current public IP.
    For sub.example.org domain is 'example.org' and subdomain is 'sub'.
    '''
    client = Client('https://subreg.cz/wsdl')
    response = client.service.Login(login=user, password=password)
    check_response(response)
    ssid = response['data']['ssid']
    record_id, old_ip = get_record_id(client, ssid, domain, subdomain)

    ip = request.urlopen('https://api.ipify.org').read().decode('utf8')
    record = {
        'id': record_id,
        'type': 'A',
        'content': ip,
        'prio': 0,
        'ttl': 900
    }

    if record_id is None:
        response = client.service.Add_DNS_Record(
            ssid=ssid,
            domain=domain,
            record=record
        )
        check_response(response)
        record_id, old_ip = get_record_id(client, ssid, domain, subdomain)
    if old_ip != ip:
        response = client.service.Modify_DNS_Record(
            ssid=ssid,
            domain=domain,
            record=record
        )
        check_response(response)


if __name__ == '__main__':
    config = ConfigParser()
    config.read_file(open('settings.ini'))
    update_record(
        config['subreg']['user'],
        config['subreg']['password'],
        config['subreg']['domain'],
        config['subreg']['subdomain']
    )

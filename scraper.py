#!/usr/bin/env python3


import click
import re
import requests
from requests.auth import HTTPDigestAuth
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.option('--host')
@click.option('--username')
@click.option('--password')
def get_vlans(host, username, password):
   url = 'http://%s/vlan/VLAN_8021q.shtml' % host
   response = requests.post(url, auth=HTTPDigestAuth(username, password))
   html = response.text
   table_body = re.findall(REGEXP_VLANS, html)[0]
   _process_table_body_vlans(table_body[1:])


@cli.command()
@click.option('--host')
@click.option('--username')
@click.option('--password')
@click.option('--port', type=int)
def get_port_statistics(host, username, password, port):
   url = 'http://%s/info/port_info.shtml?port=%d' % (host, port)
   response = requests.post(url, auth=HTTPDigestAuth(username, password))
   html = response.text
   table_body = re.findall(REGEXP_PORT_STATISTICS, html)[0]
   _process_table_body_port_info(table_body[1:])


@cli.command()
@click.option('--host')
@click.option('--username')
@click.option('--password')
@click.option('--port', type=int)
def get_poe_status(host, username, password, port):
   url = 'http://%s/info/port_info.shtml?port=%d' % (host, port)
   response = requests.post(url, auth=HTTPDigestAuth(username, password))
   html = response.text
   table_body = re.findall(REGEXP_POE_STATUS, html)[0]
   _process_table_body_port_info(table_body[1:])


def _process_table_body_vlans(table_body):
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        print(d[0], d[1], d[2], d[3], d[4])


def _process_table_body_port_info(table_body):
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        print(d[0], d[1], d[2])


def _abort(message):
    print(message, file=sys.stderr)
    sys.exit(1)


REGEXP_VLANS = r'<b>VLAN List</b><br><table.*?>(.*?)</table>'
REGEXP_PORT_STATISTICS = r'<b>Port Statistics</b><table.*?>(.*?)</table>'
REGEXP_POE_STATUS = r'<b>PoE Status</b><table.*?>(.*?)</table>'
REGEXP_TR = r'<tr.*?>(.*?)</tr>'
REGEXP_TD = r'<td.*?>(.*?)</td>'


if __name__ == '__main__':
    cli()

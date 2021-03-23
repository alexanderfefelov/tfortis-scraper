#!/usr/bin/env python3


import click
import json
import re
import requests
from requests.auth import HTTPDigestAuth
import sys
import yaml


@click.group()
def cli():
    pass


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_device_info(host, username, password, output_format):
    url = URL_DEVICE_INFO % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_DEVICE_INFO, html)[0]
    result = _process_device_info(table_body)
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_arp_table(host, username, password, output_format):
    url = URL_ARP_TABLE % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_ARP_TABLE, html)[0]
    result = _process_arp_table(table_body[1:])
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--port', required=True, help='Port name')
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_port_mac_table(host, username, password, port, output_format):
    url = URL_PORT_MAC_TABLE % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_PORT_MAC_TABLE, html)[1]
    result = _process_mac_table(table_body[1:], port)
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_vlans(host, username, password, output_format):
    url = URL_VLANS % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_VLANS, html)[0]
    result = _process_vlans(table_body[1:])
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--port', required=True, type=int, help='Port number, zero-based')
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_port_statistics(host, username, password, port, output_format):
    url = URL_PORT_STATISTICS % (host, port)
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_PORT_STATISTICS, html)[0]
    result = _process_port_statistics(table_body[1:])
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--port', required=True, type=int, help='Port number, zero-based')
@click.option('--output-format', required=True, type=click.Choice(['json', 'python', 'yaml']))
def get_port_poe_status(host, username, password, port, output_format):
    url = URL_PORT_POE_STATUS % (host, port)
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_PORT_POE_STATUS, html)[0]
    result = _process_poe_status(table_body[1:])
    _print_result(result, output_format)


def _process_device_info(table_body):
    result = {}
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result[_normalize_key_name(d[0])] = d[1]
    return result


def _process_arp_table(table_body):
    result = []
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result.append({
            'ip-address': d[1],
            'mac-address': d[2],
            'age': int(d[3]),
            'type': d[4]
        })
    return result


def _process_mac_table(table_body, port):
    result = []
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        if d[2].strip() == port:
            result.append(d[1])
    return result


def _process_vlans(table_body):
    result = []
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result.append({
            'vid': int(d[0]),
            'name': d[2],
            'enabled': bool(d[1]),
            'tagged-ports': d[3].split(),
            'untagged-ports': d[4].split()
        })
    return result


def _process_port_statistics(table_body):
    result = {}
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result[_normalize_key_name('rx %s' % d[0])] = _to_int(d[1])
        result[_normalize_key_name('tx %s' % d[0])] = _to_int(d[2])
    return result


def _process_poe_status(table_body):
    result = {}
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result[_normalize_key_name('type a %s' % d[0])] = _normalize_poe_value(d[1])
        result[_normalize_key_name('type b %s' % d[0])] = _normalize_poe_value(d[2])
    return result


def _normalize_key_name(s):
    return s \
        .replace('  ', '-') \
        .replace(' ', '-') \
        .lower()


def _normalize_poe_value(s):
    if not s:
        return None
    else:
        maybe_pair = s.split()
        if len(maybe_pair) == 2:
            return float(maybe_pair[0])
        else:
            return s


def _to_int(s):
    try:
        return int(s)
    except ValueError:
        return None


def _print_result(result, output_format):
    if output_format == 'python':
        print(result)
    elif output_format == 'json':
        print(json.dumps(result))
    elif output_format == 'yaml':
        print(yaml.dump(result))
    else:
        abort('Unknown output format')


def _abort(message):
    print(message, file=sys.stderr)
    sys.exit(1)


REGEXP_ARP_TABLE = r'<table.*?>(.*?)</table>'
REGEXP_DEVICE_INFO = r'<table.*?>(.*?)</table>'
REGEXP_PORT_MAC_TABLE = r'<table.*?>(.*?)</table>'
REGEXP_PORT_POE_STATUS = r'<b>PoE Status</b><table.*?>(.*?)</table>'
REGEXP_PORT_STATISTICS = r'<b>Port Statistics</b><table.*?>(.*?)</table>'
REGEXP_VLANS = r'<b>VLAN List</b><br><table.*?>(.*?)</table>'

REGEXP_TR = r'<tr.*?>(.*?)</tr>'
REGEXP_TD = r'<td.*?>(.*?)</td>'

URL_ARP_TABLE = 'http://%s/info/ARP.shtml'
URL_DEVICE_INFO = 'http://%s/info/cpuinfo.shtml'
URL_PORT_MAC_TABLE = 'http://%s/info/MAC.shtml'
URL_PORT_POE_STATUS = 'http://%s/info/port_info.shtml?port=%d'
URL_PORT_STATISTICS = 'http://%s/info/port_info.shtml?port=%d'
URL_VLANS = 'http://%s/vlan/VLAN_8021q.shtml'


if __name__ == '__main__':
    cli()

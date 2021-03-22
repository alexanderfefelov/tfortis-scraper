#!/usr/bin/env python3


import click
import json
import re
import requests
from requests.auth import HTTPDigestAuth
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python']))
def get_device_info(host, username, password, output_format):
    url = 'http://%s/info/cpuinfo.shtml' % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_DEVICE_INFO, html)[0]
    result = _process_device_info(table_body)
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python']))
def get_vlans(host, username, password, output_format):
    url = 'http://%s/vlan/VLAN_8021q.shtml' % host
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_VLANS, html)[0]
    result = _process_vlans(table_body[1:])
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--port', required=True, type=int)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python']))
def get_port_statistics(host, username, password, port, output_format):
    url = 'http://%s/info/port_info.shtml?port=%d' % (host, port)
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_PORT_STATISTICS, html)[0]
    result = _process_port_statistics(table_body[1:])
    _print_result(result, output_format)


@cli.command()
@click.option('--host', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@click.option('--port', required=True, type=int)
@click.option('--output-format', required=True, type=click.Choice(['json', 'python']))
def get_poe_status(host, username, password, port, output_format):
    url = 'http://%s/info/port_info.shtml?port=%d' % (host, port)
    response = requests.post(url, auth=HTTPDigestAuth(username, password))
    html = response.text
    table_body = re.findall(REGEXP_POE_STATUS, html)[0]
    result = _process_poe_status(table_body[1:])
    _print_result(result, output_format)


def _process_device_info(table_body):
    result = {}
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result[_normalize_key_name(d[0])] = d[1]
    return result


def _process_vlans(table_body):
    result = []
    for r in re.findall(REGEXP_TR, table_body):
        d = re.findall(REGEXP_TD, r)
        result.append({
            'vid': int(d[0]),
            'name': d[2],
            'enabled': bool(d[1]),
            'tagged-ports': [int(x) for x in d[3].split()],
            'untagged-ports': [int(x) for x in d[4].split()]
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
        result[_normalize_key_name('type a %s' % d[0])] = d[1]
        result[_normalize_key_name('type b %s' % d[0])] = d[2]
    return result


def _normalize_key_name(s):
    return s \
        .replace('  ', '-') \
        .replace(' ', '-') \
        .lower()


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
    else:
        abort('Unknown output format')


def _abort(message):
    print(message, file=sys.stderr)
    sys.exit(1)


REGEXP_DEVICE_INFO = r'<table.*?>(.*?)</table>'
REGEXP_VLANS = r'<b>VLAN List</b><br><table.*?>(.*?)</table>'
REGEXP_PORT_STATISTICS = r'<b>Port Statistics</b><table.*?>(.*?)</table>'
REGEXP_POE_STATUS = r'<b>PoE Status</b><table.*?>(.*?)</table>'
REGEXP_TR = r'<tr.*?>(.*?)</tr>'
REGEXP_TD = r'<td.*?>(.*?)</td>'


if __name__ == '__main__':
    cli()

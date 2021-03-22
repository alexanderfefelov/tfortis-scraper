# TFortis Scraper

## What

TFortis Scraper is a tool to scrape viable data from TFortis switches.

TFortis Scraper is capable to show:

- VLANs,
- PoE status,
- port statistics.

## Why

We need this because the very poor TFortis' SNMP implementation.

## Where

Scraper was tested with the following  models:

- TFortis PSW-2G+
- TFortis PSW-2G4F
- TFortis PSW-2G6F+

## How

Install:

```bash
pip3 install --requirement requirements.txt
```

Run:

```bash
scraper.py --help
```

Examples:

`scraper.py get-poe-status --host 10.200.199.198 --username admin --password admin --port 0 --output-format json | jq`:

```json
{
  "type-a-state": "ON",
  "type-b-state": "OFF",
  "type-a-voltage": "47.92 V",
  "type-b-voltage": "",
  "type-a-current": "51 mA",
  "type-b-current": "",
  "type-a-power": "2.401 W",
  "type-b-power": ""
}
```

`scraper.py get-port-statistics --host 10.200.199.198 --username admin --password admin --port 0 --output-format json | jq`:

```json
{
  "rx-good-bytes": 2860647484,
  "tx-good-bytes": 2234770824,
  "rx-bad-bytes": 0,
  "tx-bad-bytes": null,
  "rx-collision-packets": 0,
  "tx-collision-packets": null,
  "rx-discards-packets": 49859,
  "tx-discards-packets": null,
  "rx-filtered-packets": 0,
  "tx-filtered-packets": 49166,
  "rx-unicast-packets": 655319341,
  "tx-unicast-packets": 2881055942,
  "rx-broadcast-packets": 13765823,
  "tx-broadcast-packets": 336705415,
  "rx-multicast-packets": 16391,
  "tx-multicast-packets": 24854558,
  "rx-fcs-errors": 0,
  "tx-fcs-errors": 0,
  "rx-pause": 0,
  "tx-pause": 0,
  "rx-undersize": 0,
  "tx-undersize": null,
  "rx-oversize": 0,
  "tx-oversize": null,
  "rx-fragments": 0,
  "tx-fragments": null,
  "rx-jabber": 0,
  "tx-jabber": null,
  "rx-macrcverror": 0,
  "tx-macrcverror": null,
  "rx-deferred": null,
  "tx-deferred": 0,
  "rx-excessive": null,
  "tx-excessive": 0,
  "rx-single": null,
  "tx-single": 0,
  "rx-multiple": null,
  "tx-multiple": 0
}
```

`scraper.py get-vlans --host 10.200.199.198 --username admin --password admin --output-format json | jq`:

```json
[
  {
    "vid": 1,
    "name": "Default",
    "enabled": true,
    "tagged-ports": [],
    "untagged-ports": []
  },
  {
    "vid": 8,
    "name": "v8",
    "enabled": true,
    "tagged-ports": [
      5,
      6
    ],
    "untagged-ports": []
  },
  {
    "vid": 76,
    "name": "v76",
    "enabled": true,
    "tagged-ports": [
      5,
      6
    ],
    "untagged-ports": [
      2,
      3,
      4
    ]
  },
  {
    "vid": 3504,
    "name": "v3504",
    "enabled": true,
    "tagged-ports": [
      5,
      6
    ],
    "untagged-ports": [
      1
    ]
  }
]
```

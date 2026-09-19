# Ukraine Alerts

A Home Assistant custom integration for monitoring Ukrainian air-raid and threat alerts, including Yellow and Red threat levels.

## Version

Current version: **0.1.5**

## Features

- Air
- Artillery
- Urban fights
- Chemical
- Nuclear
- Unknown
- Yellow threat level
- Red threat level
- Rocket threat
- Drone threat
- Overall Threat level sensor: `safe`, `yellow`, `red`
- Exact API threat reasons and timestamps
- Separate rocket and drone threat details
- 15 UI languages
- Automatic polling every 10 seconds

Yellow and Red can be active at the same time. When both are active, the overall Threat level is `red`, while both dedicated Yellow and Red entities remain available.

## Data source

The integration uses the [uasiren](https://github.com/PaulAnnekov/uasiren) Python library, which accesses the public Ukraine Alarm API through `siren.pp.ua`.

## Installation

### HACS

Add this repository as a **Custom repository** in HACS and select **Integration**:

```
https://github.com/Kuresha-HA/Ukraine-Alerts
```

Then install **Ukraine Alerts** and restart Home Assistant.

### Manual

Copy the `custom_components/ukraine_alerts` directory into your Home Assistant configuration directory:

```
/config/custom_components/ukraine_alerts/
```

Restart Home Assistant, then add **Ukraine Alerts** from **Settings → Devices & services → Add Integration**.

## Configuration

Select the state, district or community you want to monitor. Up to five regions can be configured.

## Entities

For each configured region the integration creates:

- six original alert-type binary sensors
- Yellow threat binary sensor
- Red threat binary sensor
- Rocket threat binary sensor
- Drone threat binary sensor
- overall Threat level sensor

The Threat level sensor exposes additional attributes containing active reasons, localized summaries, rocket/drone reasons, API update time, and individual Yellow/Red/Rocket/Drone activity flags.

## Home Assistant version

Developed and tested with Home Assistant 2026.9.x.

## Disclaimer

This is a community-maintained Home Assistant integration. Alert information is provided by the Ukraine Alarm service. For safety-critical decisions, use official civil protection channels as well.

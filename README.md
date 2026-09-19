<div align="center">

<img src="https://raw.githubusercontent.com/Kuresha-HA/Ukraine-Alerts/main/custom_components/ukraine_alerts/brand/logo.png" alt="Ukraine Alerts" width="760">

# Ukraine Alerts

### 🇺🇦 Home Assistant integration for Ukrainian air-raid and threat alerts

Monitor regional alerts directly in Home Assistant with dedicated sensors for **Yellow**, **Red**, **Rocket**, **Drone**, and other threat types.

<p>
  <a href="https://github.com/Kuresha-HA/Ukraine-Alerts/releases"><img src="https://img.shields.io/github/v/release/Kuresha-HA/Ukraine-Alerts?style=for-the-badge" alt="Release"></a>
  <a href="https://github.com/Kuresha-HA/Ukraine-Alerts/actions/workflows/hassfest.yaml"><img src="https://img.shields.io/github/actions/workflow/status/Kuresha-HA/Ukraine-Alerts/hassfest.yaml?style=for-the-badge&label=Hassfest" alt="Hassfest"></a>
  <a href="https://github.com/Kuresha-HA/Ukraine-Alerts/actions/workflows/hacs.yaml"><img src="https://img.shields.io/github/actions/workflow/status/Kuresha-HA/Ukraine-Alerts/hacs.yaml?style=for-the-badge&label=HACS" alt="HACS"></a>
  <a href="https://github.com/Kuresha-HA/Ukraine-Alerts/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kuresha-HA/Ukraine-Alerts?style=for-the-badge" alt="License"></a>
</p>

</div>

---

## ✨ What it does

**Ukraine Alerts** brings Ukrainian air-raid and threat information into Home Assistant and turns it into native entities that can be used in dashboards, automations, notifications, lights, sirens, and other smart-home workflows.

### Threat types

| Category | Entity |
|---|---|
| 🛩️ Air | Air threat |
| 💥 Artillery | Artillery threat |
| ⚔️ Urban fights | Urban combat threat |
| ☣️ Chemical | Chemical threat |
| ☢️ Nuclear | Nuclear threat |
| ❔ Unknown | Unknown threat |
| 🟡 Yellow | Yellow threat level |
| 🔴 Red | Red threat level |
| 🚀 Rocket | Rocket threat |
| 🛸 Drone | Drone threat |

### 🎯 Overall Threat Level

Each configured region also receives an overall threat-level sensor:

| State | Meaning |
|---|---|
| 🟢 `safe` | No active Yellow or Red threat |
| 🟡 `yellow` | Yellow threat is active |
| 🔴 `red` | Red threat is active |

If **Yellow and Red are active simultaneously**, the overall state is **`red`**, while the dedicated Yellow and Red entities remain available independently.

---

## 📊 Rich entity data

The integration exposes more than a simple alarm state.

The overall Threat Level sensor can provide:

- active threat reasons;
- localized threat summaries;
- Yellow and Red activity;
- Rocket and Drone activity;
- Rocket threat reasons;
- Drone threat reasons;
- API update timestamp;
- individual alert-type states.

This makes the integration suitable for advanced Home Assistant automations and dashboards.

---

## ⚡ Fast automatic updates

Data is polled automatically every **10 seconds**.

This allows automations to react to changes without requiring manual refreshes.

Typical use cases include:

- 🔔 phone and push notifications;
- 💡 changing lights according to threat level;
- 🔊 activating speakers or sirens;
- 📺 displaying alerts on dashboards;
- 🏠 switching smart-home scenes;
- 🤖 triggering complex automation sequences.

---

## 🌐 Data source

Ukraine Alerts uses the [**uasiren**](https://github.com/PaulAnnekov/uasiren) Python library to access the public Ukraine Alarm API through **siren.pp.ua**.

The integration does not create or modify alerts. It only retrieves publicly available alert information and exposes it to Home Assistant.

---

## 🧩 Configuration

During setup, select the Ukrainian regions you want to monitor.

Supported configuration:

- state / oblast;
- district;
- community;
- up to **5 regions** per integration entry.

You can create additional entries if you need a different regional configuration.

---

## 📦 Installation

### HACS — recommended

1. Open **HACS → Integrations**.
2. Search for **Ukraine Alerts**.
3. Install the integration.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services → Add Integration**.
6. Select **Ukraine Alerts**.
7. Choose the regions to monitor.

If you are installing directly from GitHub as a custom repository:

```
https://github.com/Kuresha-HA/Ukraine-Alerts
```

Select **Integration** as the repository type.

### Manual installation

Copy:

```
custom_components/ukraine_alerts
```

to:

```
/config/custom_components/ukraine_alerts/
```

Restart Home Assistant and add **Ukraine Alerts** from:

**Settings → Devices & services → Add Integration**

---

## 🏠 Home Assistant

Developed and tested with **Home Assistant 2026.9.x**.

The integration uses the modern Home Assistant config-flow architecture and provides localized UI strings in **15 languages**.

---

## 🔧 Technical details

| Property | Value |
|---|---|
| Integration | Ukraine Alerts |
| Domain | `ukraine_alerts` |
| Version | **0.1.5** |
| IoT class | Cloud polling |
| Update interval | **10 seconds** |
| Regions per entry | **Up to 5** |
| Languages | **15** |
| Dependency | `uasiren==0.0.1` |
| License | MIT |

---

## ⚠️ Disclaimer

This is a community-maintained Home Assistant integration.

Alert information is provided by the Ukraine Alarm service. **For safety-critical decisions, always follow official civil protection instructions and official emergency channels.**

---

<div align="center">

### 🇺🇦 Ukraine Alerts for Home Assistant

**Real-time alert information. Native Home Assistant entities. Powerful automations.**

</div>

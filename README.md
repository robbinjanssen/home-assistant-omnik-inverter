<!-- PROJECT SHIELDS -->
[![hacs_badge][hacs-shield]][hacs-url]
![Project Stage][project-stage-shield]

![Project Maintenance][maintenance-shield]
[![Maintainability][maintainability-shield]][maintainability-url]

# Omnik Inverter Integration for Home Assistant

The Omnik Inverter integration will scrape data from an Omnik inverter connected to your local network.
It has been tested and developed on the following inverters:

## Supported models

| Brand    | Model            | Datasource |
|----------|------------------|------------|
| Omnik    | Omniksol 1000TL  | JS         |
| Omnik    | Omniksol 1500TL  | JS         |
| Omnik    | Omniksol 2000TL  | JS         |
| Omnik    | Omniksol 2000TL2 | JSON       |
| Omnik    | Omniksol 2500TL  | HTML       |
| Omnik    | Omniksol 3000TL  | JS/TCP     |
| Omnik    | Omniksol 4000TL2 | JS         |
| Ginlong  | Solis-DLS-WiFi   | JSON/HTML  |
| Hosola   | 1500TL           | JS         |
| Bosswerk | BW-MI300         | HTML       |
| Bosswerk | BW-MI600         | HTML       |
| Sofar    | 3600TLM          | HTML       |
| Huayu    | HY-600-Pro       | HTML       |

After installation you can add the inverter through the integration page. The values will be presented by two devices in Home Assistant. One is the inverter containing the actual solar power, and one is the device containing information about the wifi signal.

## Requirements

Your Omnik Inverter needs to be connected to your local network, as this custom integration will utilise the web interface of the Omnik inverter to read data. All you need to know is the IP address of the Omnik inverter and you are good to go.

## HACS installation

Add this integration using HACS by searching for `Omnik Inverter Solar Sensor (No Cloud)` on the `Integrations` page.

## Manual installation

Create a directory called `omnik_inverter` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this integration by copying all files in `/custom_components/omnik_inverter/` folder from this repo into the new `<config directory>/custom_components/omnik_inverter/` directory you just created.

This is how your custom_components directory should be:
```bash
custom_components
├── omnik_inverter
│   ├── translations
│   │   ├── de.json
│   │   ├── en.json
│   │   └── nl.json
│   ├── __init__.py
│   ├── binary_sensor.py
│   ├── config_flow.py
│   ├── const.py
│   ├── coordinator.py
│   ├── diagnostics.py
│   ├── manifest.json
│   ├── models.py
│   ├── sensor.py
│   └── strings.json
```

## Configuration

[![ha_badge][ha-add-shield]][ha-add-url]

To configure the integration, add it using [Home Assistant integrations][ha-add-url]. This will provide you with a configuration screen where you can first select the data source. Again, most inverters use JS. Some use JSON and in some rare cases HTML is used. The TCP backend contains additional electrical statistics but lacks information about the WiFi module.

After selecting the data source, enter a **name** and IP address as **host** and you're good to go!

_Optionally you can update the scan interval in the integration settings._

## Examples

### Config flow

<img src="/images/config_flow.gif" width="500" />

### Entities

<img src="/images/all_entities.png" width="500" />

## What data source do I use?

The web interface has a javascript, JSON or HTML file that contains the actual values. These values are updated every few minutes.

- Most inverters have a JS file, try accessing `http://<your omnik ip address>/js/status.js` in your browser.
- Some inverters use a JSON status file to output the values. Check if your inverter outputs JSON data by navigating to: `http://<your omnik ip address>/status.json?CMD=inv_query`.
- A few inverters don't have JS or JSON but output the values directly in a HTML files. Check if your inverter supports the following URL: `http://<your omnik ip address>/status.html`. _Note that this will work for almost all inverters, but you need to check the HTML source for a `<script>` tag that contains the relevant `webData`._

If none of the methods work, please open a [new issue](https://github.com/robbinjanssen/home-assistant-omnik-inverter/issues/new) and we might be able to make it work for your inverter 😄 Make sure you let us know what inverter you use.

## Contributing

Please see [CONTRIBUTING](.github/CONTRIBUTING.md) and [CODE_OF_CONDUCT](.github/CODE_OF_CONDUCT.md) for details.

### Thanks

Special thank you to [@klaasnicolaas](https://github.com/klaasnicolaas) for taking this integration to the next level 🚀 and [@relout](https://github.com/relout) for testing 👍

## References

- https://community.home-assistant.io/t/omink-inverter-in-home-assistant/102455/36
- https://github.com/heinoldenhuis/home_assistant_omnik_solar
- https://github.com/sincze/Domoticz-Omnik-Local-Web-Plugin
- https://github.com/klaasnicolaas/python-omnikinverter

[maintainability-shield]: https://qlty.sh/gh/robbinjanssen/projects/home-assistant-omnik-inverter/maintainability.svg
[maintainability-url]: https://qlty.sh/gh/robbinjanssen/projects/home-assistant-omnik-inverter
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-stable-brightgreen.svg?style=for-the-badge

[hacs-url]: https://github.com/hacs/integration
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge

[ha-add-url]: https://my.home-assistant.io/redirect/config_flow_start/?domain=omnik_inverter
[ha-add-shield]: https://my.home-assistant.io/badges/config_flow_start.svg

<!-- PROJECT SHIELDS -->
[![hacs_badge][hacs-shield]][hacs-url]
![Project Stage][project-stage-shield]

![Project Maintenance][maintenance-shield]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Quality][code-quality-shield]][code-quality-url]

# Omnik Inverter Sensor for Home Assistant

The Omnik Inverter Sensor component will scrape data from an Omnik inverter connected to your local network.
It has been tested and developed on the following inverters:

## Supported models

- Omnik1000TL
- Omnik1500TL
- Omnik2000TL
- Omnik2500TL (HTML)
- Omnik2000TL2
- Omnik4000TL2
- Ginlong stick (JSON)

After installation you can add the sensors through the integration page. The values will be presented as sensors in [Home Assistant](https://home-assistant.io/).

## Requirements

Your Omnik Inverter needs to be connected to your local network, as this custom component will utilise the web interface of the Omnik inverter to read data. All you need to know is the IP address of the Omnik inverter and you are good to go.

## HACS installation

Add this component using HACS by searching for `Omnik Inverter Solar Sensor (No Cloud)` on the `Integrations` page.

## Manual installation

Create a directory called `omnik_inverter` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this component by copying all files in `/custom_components/omnik_inverter/` folder from this repo into the new `<config directory>/custom_components/omnik_inverter/` directory you just created.

This is how your custom_components directory should be:
```bash
custom_components
├── omnik_inverter
│   ├── translations
│   │   ├── en.json
│   │   └── nl.json
│   ├── __init__.py
│   ├── config_flow.py
│   ├── const.py
│   ├── manifest.json
│   ├── sensor.py
│   └── strings.json
```


## How does it work?

The web interface has a javascript file that contains the actual values. This is updated every 
5 minutes. Check it out in your browser at `http://<your omnik ip address>/js/status.js`

The result contains a lot of information, but there is one part we're interested in:
```js
// ... Bunch of data
var webData="NLBN1234567A1234,iv4-V6.5-140-4,V5.2-42819,omnik4000tl2,4000,1920,429,87419,,3,";
// Or for some inverters:
var myDeviceArray=new Array(); myDeviceArray[0]="AANN3020,V5.04Build230,V4.13Build253,Omnik3000tl,3000,1313,685,9429,,1,";
// ... Even more data
```

This output contains your serial number, firmware versions, hardware information, the 
current power output: 1920, the energy (kWh) generated today: 429 and the total energy (kWh) generated: 87419.

The component basically requests the URL, looks for the _webData_ part and extracts the 
values as sensors.

### My inverter doesn't show any output when I go to the URL.

> Use this if you have an Omnik Inverter 2k TL2.

Some inverters use a JSON status file to output the values. Check if your 
inverter outputs JSON data by navigating to: `http://<your omnik ip address>/status.json?CMD=inv_query&rand=0.1234567`.

If so, then use the `use_json` config boolean to make the component use the URL above.

### Thanks

Special thank you to [@klaasnicolaas](https://github.com/klaasnicolaas) for taking this component to the next level 🚀 and [@relout](https://github.com/relout) for testing :-)

## References

- https://community.home-assistant.io/t/omink-inverter-in-home-assistant/102455/36
- https://github.com/heinoldenhuis/home_assistant_omnik_solar (This uses omnikportal.com to get data for your inverter, check it out!)
- https://github.com/sincze/Domoticz-Omnik-Local-Web-Plugin
- https://github.com/klaasnicolaas/python-omnikinverter

[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/robbinjanssen/home-assistant-omnik-inverter.svg
[code-quality-url]: https://lgtm.com/projects/g/robbinjanssen/home-assistant-omnik-inverter/context:python
[maintainability-shield]: https://api.codeclimate.com/v1/badges/08d56a884fe1971d1c12/maintainability
[maintainability-url]: https://codeclimate.com/github/robbinjanssen/home-assistant-omnik-inverter/maintainability
[maintenance-shield]: https://img.shields.io/maintenance/yes/2021.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-stable-brightgreen.svg?style=for-the-badge

[hacs-url]: https://github.com/custom-components/hacs
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
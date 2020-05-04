[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Home Assistant Omnik Inverter
The Omnik Inverter Sensor component will retrieve data from an Omnik inverter connected to your local network.
It has been tested and developed on an Omnik 4K TL2 and it might work for other inverters as well.

The values will be presented as sensors in [Home Assistant](https://home-assistant.io/).

## Requirements

Your Omnik Inverter needs to be connected to your local network, as this custom component will utilise the web interface of the Omnik inverter to read data. All you need to know is the IP address of the Omnik inverter and you are good to go.

## HACS installation

Add this component using HACS, search for the `Omnik Inverter` integration.

## Manual installation

Create a directory called `omnik_inverter` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this component by copying all files in `/custom_components/omnik_inverter/` folder from this repo into the new `<config directory>/custom_components/omnik_inverter/` directory you just created.

This is how your custom_components directory should be:
```bash
custom_components
├── omnik_inverter
│   ├── __init__.py
│   ├── manifest.json
│   └── sensor.py
```

## Configuration example

To enable this sensor, add the following lines to your configuration.yaml file:

``` YAML
sensor:
  - platform: omnik_inverter
    host: 192.168.100.100
```

By default caching the power today value is enabled, you can disable it using the `cache_power_today` configuration attribute. Check "How does it work?" when/why you might need to disable it.

``` YAML
sensor:
  - platform: omnik_inverter
    host: 192.168.100.100
    cache_power_today: false
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

This variable declaration contains your serial number, firmware versions, hardware information, the 
current power output: 1920, the energy generated today: 429 and the total energy generated: 87419.

This custom component basically requests the URL, looks for the _webData_ part and extracts the 
values as the following sensors:
- `sensor.solar_power_current` (Watt)
- `sensor.solar_power_today` (kWh)
- `sensor.solar_power_total` (kWh)

### Caching "power today".

In a few cases the Omnik inverter resets the `solar_power_today` to 0.0 after for example 21:00. By 
setting the `cache_power_today` config attribute to `true` (default) this component will cache the 
value and only resets to 0.0 after midnight. If you do not experience this, then disable the 
cache by setting the config variable to `false`.

## References

- https://community.home-assistant.io/t/omink-inverter-in-home-assistant/102455/36
- https://github.com/heinoldenhuis/home_assistant_omnik_solar (This uses omnikportal.com to get data for your inverter, check it out!)
- https://github.com/sincze/Domoticz-Omnik-Local-Web-Plugin

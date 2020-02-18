# Home Assistant Omnik Inverter
The Omnik Inverter Sensor component will retrieve data from an Omnik inverter connected to your local network.
It has been tested and developed on an Omnik 4K TL2 and it is currently unknown if it works for other inverters.

The values will be presented as sensors in [Home Assistant](https://home-assistant.io/).

## Requirements

Your Omnik Inverter needs to be connected to your local network, as this custom component will utilise the web interface of the Omnik inverter to read data. All you need to know is the IP address of the Omnik inverter and you are good to go.

## HACS installation

Add this component using HACS by adding this repository as a custom repository in your settings.
- URL: https://github.com/robbinjanssen/home-assistant-omnik-inverter
- Category: Integration

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

## How does it work?

The web interface has a javascript file that contains the actual values. This is updated every minute (afaik). Check it out in your browser at `http://<your omnik ip address>/js/status.js`

The result contains a lot of information, but there is one part we're interested in:
```js
// ... Bunch of data
var webData="NLBN1234567A1234,iv4-V6.5-140-4,V5.2-42819,omnik4000tl2,4000,1920,429,87419,,3,";
// ... Even more data
```

This variable declaration contains your serial number, firmware versions, hardware information, the current power output: 1920, the energy generated today: 429 and the total energy generated: 87419.

This custom component basically requests the URL, looks for the _webData_ part and extracts the values as the following sensors:
- `sensor.solar_power_current` (Watt)
- `sensor.solar_power_today` (kWh)
- `sensor.solar_power_total` (kWh)

> Note: I ran into the problem that my Omnik inverter resets the `solar_power_today` to 0.0 after 21:00. This component therefor caches the value and only resets to 0.0 after midnight.

## References

Got my inspiration from:
- https://community.home-assistant.io/t/omink-inverter-in-home-assistant/102455/36
- https://github.com/heinoldenhuis/home_assistant_omnik_solar (This uses omnikportal.com to get data for your inverter, check it out!)

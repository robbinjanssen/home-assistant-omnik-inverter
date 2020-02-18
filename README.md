# Home Assistant Omnik Inverter
The Omnik Inverter Sensor component will retrieve data from a local Omnik inverter.
It has been tested and developed on an Omnik 4K TL2 and it is currently unknown if it works for other inverters.

The values will be presented as sensors in [Home Assistant](https://home-assistant.io/).

## Requirements

Your Omnik Inverter needs to be connected to your local network, as this custom component will utilise the web interface of the Omnik inverter to read data. All you need to know is the IP address of the Omnik inverter and you are good to go.

## How does it work?

The web interface has a javascript file that contains the actual values. This is updated (afaik) every minute. You can visit it in your browser at http://your_omnik_ip_address/js/status.js

Looking at the data it contains lots of information, but there's one part we're interested in:

```js
// ... Bunch of data
var webData="NLBN1234567A1234,iv4-V6.5-140-4,V5.2-42819,omnik4000tl2,4000,1920,429,87419,,3,";
// ... Even more data.
```

This line contains your serial number, firmware versions, hardware information _and_ the current power output (1920) in watts and the total energy generated today (429) in watts.

This custom component basically requests the URL, looks for the _webData_ part and extracts the values as two sensors.
- `sensor.solar_power_current` (Watt)
- `sensor.solar_power_today` (kWh)

For some reason my Omnik inverter reset the power today to 0.0 after 21:00, so the total power today is cached by the custom component until the 00:00 the next day. 

## Installation

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

## References

Got my inspiration from: https://community.home-assistant.io/t/omink-inverter-in-home-assistant/102455/36
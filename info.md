## Omnik Inverter Sensor Component for Home Assistant.

The Omnik solar sensor component will retrieve data from an Omnik solar inverter.
The values will be presented as sensors (or attributes of sensors) in Home Assistant.

## Configuration

``` YAML
sensor:
  - platform: omnik_inverter
    host: 192.168.100.100
```

### Entities

- `sensor.solar_power_current` (Watt)
- `sensor.solar_power_today` (kWh)
- `sensor.solar_power_total` (kWh)

### Example

![Omnik Inverter Sensor Entities](https://github.com/robbinjanssen/home-assistant-omnik-inverter/blob/master/images/entities.png)

### Documentation

Find the full documentation [here](https://github.com/robbinjanssen/home-assistant-omnik-inverter).
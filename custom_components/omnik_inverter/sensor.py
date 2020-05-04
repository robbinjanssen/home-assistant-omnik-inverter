"""
configuration.yaml

sensor:
  - platform: omnik_inverter
    host: 192.168.100.100
    cache_power_today: true
"""
import logging
from datetime import timedelta
from datetime import datetime

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, POWER_WATT, ENERGY_KILO_WATT_HOUR
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

from urllib.request import urlopen

import re
import pickle

VERSION = '1.2.2'

CONF_CACHE_POWER_TODAY = 'cache_power_today'

BASE_URL = 'http://{0}/js/status.js'
BASE_CACHE_NAME = '.{0}.pickle'

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=500)

SENSOR_TYPES = {
    'powercurrent': ['Solar Power Current', POWER_WATT, 'mdi:weather-sunny'],
    'powertoday': ['Solar Power Today', ENERGY_KILO_WATT_HOUR, 'mdi:flash'],
    'powertotal': ['Solar Power Total', ENERGY_KILO_WATT_HOUR, 'mdi:chart-line'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_CACHE_POWER_TODAY, default=True): cv.boolean
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Solar Portal sensors."""
    host = config.get(CONF_HOST)
    cache = config.get(CONF_CACHE_POWER_TODAY)

    try:
        data = OmnikInverterWeb(host)
    except RuntimeError:
        _LOGGER.error("Unable to fetch data from Omnik Inverter %s", host)
        return False

    entities = []

    for sensor_type in SENSOR_TYPES:
        entities.append(OmnikInverterSensor(data, sensor_type, cache))

    add_devices(entities)


class OmnikInverterWeb(object):
    """Representation of the Omnik Inverter Web."""

    def __init__(self, host):
        """Initialize the inverter."""
        self._host = host
        self.result = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the omnik inverter."""
        dataurl = BASE_URL.format(self._host)
        try:
            fp = urlopen(dataurl)
            r = fp.read()
            fp.close()
        except OSError:
            _LOGGER.error("Unable to fetch data from Omnik Inverter %s", self._host)
            return False

        # Remove strange characters from the result
        result = r.decode('ascii', 'ignore')

        # Find the webData
        if result.find('webData="') != -1:
            matches = re.search(r'(?<=webData=").*?(?=";)', result)
        else:
            matches = re.search(r'(?<=myDeviceArray\[0\]=").*?(?=";)', result)

        # Split the values
        if matches is not None:
            self.result = matches.group(0).split(',')
        else:
            _LOGGER.error("Empty data from Omnik Inverter %s", self._host)

        _LOGGER.debug("Data = %s", self.result)


class OmnikInverterSensor(Entity):
    """Representation of a OmnikInverter sensor from the web data."""

    def __init__(self, data, sensor_type, cache):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self.cache = cache
        self._name = SENSOR_TYPES[self.type][0]
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        self.update()
        self._unique_id = f"{self.data.result[0]}-{self._name}"

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()

        # Get the result data
        result = self.data.result

        if result is None:
          _LOGGER.debug("No data found for %s", self.type)
          return False

        if self.type == 'powercurrent':
            # Update the sensor state
            self._state = int(result[5])
        elif self.type == 'powertoday':
            # Define the cache name
            cacheName = BASE_CACHE_NAME.format(self.type)

            # Prepare the current actual values
            currentValue = int(result[6])
            currentDay = int(datetime.now().strftime('%Y%m%d'))

            # Check if caching is enabled
            if self.cache:
                try:
                    # Fetch the cache from the storage.
                    cache = pickle.load(open(cacheName, 'rb'))

                except (OSError, IOError, EOFError):
                    cache = [0, 0]

                # Extract the cache values
                cacheValue = int(cache[0])
                cacheDay = int(cache[1])

                # If the day has not yet passed, and the current value is bigger then
                # the cached value, then we update the cached value to the current
                # value.
                if currentDay == cacheDay and currentValue >= cacheValue:
                    cacheValue = currentValue
                    cacheDay = currentDay

                # Else if the day has not yet passed but the cache value is bigger then
                # the current value, the inverter might have reset the current value
                # to 0 to early. Therefor the cached value is used as output.
                elif currentDay == cacheDay and cacheValue > currentValue:
                    currentValue = cacheValue

                # Else if the day has passed, but the current value is the same as the
                # cached value, then the inverter has NOT reset the current value to
                # 0 yet. Therefor manually output the value 0.
                elif currentDay > cacheDay and currentValue == cacheValue:
                    currentValue = 0

                # Lastly if the day has passed and the current value does not match
                # the cached value, it is probably reset to 0. So update the cache
                # value to the current value.
                elif currentDay > cacheDay and currentValue != cacheValue:
                    cacheValue = currentValue
                    cacheDay = currentDay

                # Store new stats
                pickle.dump([cacheValue, cacheDay], open(cacheName, 'wb'))

            # Update the sensor state, divide by 100 to make it kWh
            self._state = (currentValue / 100)
        elif self.type == 'powertotal':
            # Update the sensor state, divide by 10 to make it kWh
            self._state = (int(result[7]) / 10)

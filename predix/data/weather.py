
import os
import urllib

import predix.service


class WeatherForecast(object):
    def __init__(self, *args, **kwargs):
        super(WeatherForecast, self).__init__(*args, **kwargs)

        self.uri = os.environ.get('PREDIX_WEATHER_URI')
        if not self.uri:
            raise ValueError("PREDIX_WEATHER_URI environment unset")

        self.zone_id = os.environ.get('PREDIX_WEATHER_ZONE_ID')
        if not self.zone_id:
            raise ValueError("PREDIX_WEATHER_ZONE_ID environment unset")

        self.service = predix.service.Service(self.zone_id)

    def authenticate_as_client(self, client_id, client_secret):
        self.service.uaa.authenticate(client_id, client_secret)

    def get_weather_forecast_days(self, latitude, longitude,
            days=1, frequency=1, reading_type=None):
        """
        Return the weather forecast for a given location.

            results = ws.get_weather_forecast_days(lat, long)
            for w in results['hits']:
                print w['start_datetime_local']
                print w['reading_type'], w['reading_value']

        For description of reading types:
        https://graphical.weather.gov/xml/docs/elementInputNames.php
        """
        params = {}

        # Can get data from NWS1 or NWS3 representing 1-hr and 3-hr
        # intervals.
        if frequency not in [1, 3]:
            raise ValueError("Reading frequency must be 1 or 3")

        params['days'] = days
        params['source'] = 'NWS' + str(frequency)
        params['latitude'] = latitude
        params['longitude'] = longitude

        if reading_type:
            # url encoding will make spaces a + instead of %20, which service
            # interprets as an "and" search which is undesirable
            reading_type = reading_type.replace(' ', '%20')
            params['reading_type'] = urllib.quote_plus(reading_type)

        url = self.uri + '/v1/weather-forecast-days/'
        return self.service._get(url, params=params)

    def get_weather_forecast(self, latitude, longitude, start, end,
            frequency=1, reading_type=None):
        """
        Return the weather forecast for a given location for specific
        datetime specified in UTC format.

            results = ws.get_weather_forecast(lat, long, start, end)
            for w in results['hits']:
                print w['start_datetime_local']
                print w['reading_type'], '=', w['reading_value']

        For description of reading types:
        https://graphical.weather.gov/xml/docs/elementInputNames.php
        """
        params = {}

        # Can get data from NWS1 or NWS3 representing 1-hr and 3-hr
        # intervals.
        if frequency not in [1, 3]:
            raise ValueError("Reading frequency must be 1 or 3")

        params['source'] = 'NWS' + str(frequency)
        params['latitude'] = latitude
        params['longitude'] = longitude
        params['start_datetime_utc'] = start
        params['end_datetime_utc'] = end

        if reading_type:
            # Not using urllib.quote_plus() because its using a + which is
            # being interpreted by service as an and instead of a space.
            reading_type = reading_type.replace(' ', '%20')
            params['reading_type'] = reading_type

        url = self.uri + '/v1/weather-forecast-datetime/'
        return self.service._get(url, params=params)

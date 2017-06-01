
import os
import re
import time
import json
import logging
import datetime
import websocket

import predix.service


class TimeSeries(object):
    """
    Client library for working with the Time Series service.
    """
    # "Constants" for data quality values
    BAD = 0
    UNCERTAIN = 1
    NA = 2
    GOOD = 3

    def __init__(self, read=True, write=True, *args, **kwargs):
        super(TimeSeries, self).__init__(*args, **kwargs)

        self.query_zone_id = os.environ.get('PREDIX_TIMESERIES_QUERY_ZONE_ID')
        self.query_uri = os.environ.get('PREDIX_TIMESERIES_QUERY_URI')
        if read:
            if not self.query_zone_id:
                raise ValueError('PREDIX_TIMESERIES_QUERY_ZONE_ID env unset')

            if not self.query_uri:
                raise ValueError('PREDIX_TIMESERIES_QUERY_URI environment unset')

        self.ingest_zone_id = os.environ.get('PREDIX_TIMESERIES_INGEST_ZONE_ID')
        self.ingest_uri = os.environ.get('PREDIX_TIMESERIES_INGEST_URI')
        if write:
            if not self.ingest_zone_id:
                raise ValueError('PREDIX_TIMESERIES_INGEST_ZONE_ID env unset')

            if not self.ingest_uri:
                raise ValueError('PREDIX_TIMESERIES_INGEST_URI environment unset')

        self.service = predix.service.Service(self.query_zone_id)

        # Store a websocket connection once opened
        self.ws = None

        # Store and forward any datapoints as a single transaction
        self._queue = []

    def __del__(self):
        """
        Destructor to make sure an open websocket connection is closed.
        """
        # No need to delete if not properly initialized
        if not hasattr(self, '_queue'):
            return

        if len(self._queue) > 0:
            logging.warn("%s buffered datapoints in queue lost." %
                    (len(self._queue)))

        if self.ws:
            self.ws.close()

    def authenticate_as_client(self, client_id, client_secret):
        """
        Will authenticate for the given client / secret.
        """
        self.service.uaa.authenticate(client_id, client_secret)

    def get_aggregations(self):
        """
        Returns all of the aggregations in time series.  There is no support
        in the service for filtering or paginations.
        """
        url = self.query_uri + '/v1/aggregations'
        return self.service._get(url)

    def _get_tags(self):
        """
        Returns all of the tags in time series.  There is no support
        in the service for filtering or paginations.
        """
        return self.service._get(self.query_uri + '/v1/tags')

    def get_tags(self):
        """
        Returns a list of the tag names in the timeseries service
        instance.
        """
        return self._get_tags()['results']

    def _get_datapoints(self, params):
        """
        Will make a direct REST call with the given json body payload to
        get datapoints.
        """
        url = self.query_uri + '/v1/datapoints'
        return self.service._get(url, params=params)

    def _post_datapoints(self, body):
        url = self.query_uri + '/v1/datapoints'
        return self.service._post(url, body)

    def get_values(self, *args, **kwargs):
        """
        Convenience method that for simple single tag queries will
        return just the values to be iterated on.
        """
        if isinstance(args[0], list):
            raise ValueError("Can only get_values() for a single tag.")

        response = self.get_datapoints(*args, **kwargs)
        for value in response['tags'][0]['results'][0]['values']:
            yield [datetime.datetime.utcfromtimestamp(value[0]/1000),
                   value[1],
                   value[2]]

    def is_good(self, quality):
        """
        Simple test if data quality is GOOD.
        """
        return quality == ts.GOOD

    def is_bad(self, quality):
        """
        Simple test if data quality value is BAD.
        """
        return quality == ts.BAD

    def get_datapoints(self, tags, start=None, end=None, order=None,
            limit=None, qualities=None, attributes=None, measurement=None,
            aggregations=None, post=False):
        """
        Returns all of the datapoints that match the given query.

            - tags: list or string identifying the name/tag (ie. "temp")
            - start: data after this, absolute or relative (ie. '1w-ago' or
              1494015972386)
            - end: data before this value
            - order: ascending (asc) or descending (desc)
            - limit: only return a few values (ie. 25)
            - qualities: data quality value (ie. [ts.GOOD, ts.UNCERTAIN])
            - attributes: data attributes (ie. {'unit': 'mph'})
            - measurement: tuple of operation and value (ie. ('gt', 30))
            - post: POST query instead of GET (caching implication)

        A few additional observations:
            - allow service to do most data validation
            - order is applied before limit so resultset will differ

        The returned results match what the service response is so you'll
        need to unpack it as appropriate.  Oftentimes what you want for
        a simple single tag query will be:

            response['tags'][0]['results'][0]['values']

        """
        params = {}

        # Documentation says start is required for GET but not POST, but
        # seems to be required all the time, so using sensible default.
        if not start:
            start = '1w-ago'
            logging.info("Defaulting to timeseries data since %s" % (start))

        # Start date can be absolute or relative, only certain legal values
        # but service will throw error if used improperly.  (ms, s, mi, h, d,
        # w, mm, y).  Relative dates must end in -ago.
        params['start'] = start

        # Docs say when making POST with a start that end must also be
        # specified, but this does not seem to be the case.
        if end:
            params['end'] = end

        params['tags'] = []
        if not isinstance(tags, list):
            tags = [tags]

        for tag in tags:
            query = {}
            query['name'] = tag

            # Limit resultset with an integer value
            if limit:
                query['limit'] = int(limit)

            # Order must be 'asc' or 'desc' but will get sensible error
            # from service.
            if order:
                query['order'] = order

            # Filters are complex and support filtering by
            # quality, measurement, and attributes.
            filters = {}

            # Check for the quality of the datapoints
            if qualities is not None:
                if isinstance(qualities, int) or isinstance(qualities, str):
                    qualities = [qualities]

                # Timeseries expects quality to be a string, not integer,
                # so coerce each into a string
                for i, quality in enumerate(qualities):
                    qualities[i] = str(quality)

                filters['qualities'] = {"values": qualities}

            # Check for attributes on the datapoints, expected to be
            # a dictionary of key / value pairs that datapoints must match.
            if attributes is not None:
                if not isinstance(attributes, dict):
                    raise ValueError("Attribute filters must be dictionary.")

                filters['attributes'] = attributes

            # Check for measurements that meets a given comparison operation
            # such as ge, gt, eq, ne, le, lt
            if measurement is not None:
                filters['measurements'] = {
                        'condition': measurement[0],
                        'values': measurement[1]
                        }

            # If we found any filters add them to the query
            if filters:
                query['filters'] = filters

            params['tags'].append(query)

        if post:
            return self._post_datapoints(params)
        else:
            return self._get_datapoints({"query": json.dumps(params)})

    def _get_latest(self, params):
        """
        Will directly pass the given params as parameters
        to the GET endpoint.
        """
        uri = self.query_uri + '/v1/datapoints/latest'
        return self.service._get(uri, params=params)

    def _post_latest(self, body):
        """
        Will directly pass the given body object as the JSON
        payload to a POST call.
        """
        uri = self.query_uri + '/v1/datapoints/latest'
        return self.service._post(uri, body)

    def get_latest(self, tags, post=False):
        """
        Similar to get_datapoints() but will only return the very
        last datapoint ingested for the given tag or tags (if a list).

        If given the optional post parameter will make the call as a POST
        rather than a GET request.  The GET can have an advantage of url
        based response caching and the POST has the advantage of a larger
        and more complex query.
        """
        params = {}
        params['tags'] = tags

        if post:
            return self._post_latest(params)
        else:
            return self._get_latest(params)

    def _get_websocket(self):
        if not self.ws:
            logging.debug("Initializing new websocket connection.")
            headers = {
                'Authorization': self.service._get_bearer_token(),
                'Predix-Zone-Id': self.ingest_zone_id,
                'Content-Type': 'application/json',
            }
            url = self.ingest_uri

            logging.debug("URL=" + str(url))
            logging.debug("HEADERS=" + str(headers))
            self.ws = websocket.create_connection(url, header=headers)

        return self.ws

    def _send_to_timeseries(self, message):
        """
        Establish or reuse socket connection and send
        the given message to the timeseries service.
        """
        logging.debug("MESSAGE=" + str(message))

        ws = self._get_websocket()
        ws.send(json.dumps(message))
        result = ws.recv()

        logging.debug("RESULT=" + str(result))
        return result

    def queue(self, name, value, quality=None, timestamp=None,
            attributes=None):
        """
        To reduce network traffic, you can buffer datapoints and
        then flush() anything in the queue.
        """
        # Get timestamp first in case delay opening websocket connection
        # and it must have millisecond accuracy
        if not timestamp:
            timestamp = int(round(time.time() * 1000))

        # Only specific quality values supported
        if quality not in [self.BAD, self.GOOD, self.NA, self.UNCERTAIN]:
            quality = self.UNCERTAIN

        # Check if adding to queue of an existing tag and add second datapoint
        for point in self._queue:
            if point['name'] == name:
                point['datapoints'].append([timestamp, value, quality])
                return

        # If adding new tag, initialize and set any attributes
        datapoint = {
            "name": name,
            "datapoints": [[timestamp, value, quality]]
        }

        # Attributes are specified for datapoint
        if attributes:
            # Validate rules for attribute keys to provide guidance.
            invalid_value = ':;= '
            has_invalid_value = re.compile(r'[%s]' % (invalid_value)).search
            has_valid_key = re.compile(r'^[\w\.\/\-]+$').search

            for (key, val) in attributes.items():
                # Values cannot be NULL
                if not val:
                    raise ValueError("Attribute (%s) must have value." % (key))

                # Values cannot contain certain arbitrary characters
                if bool(has_invalid_value(val)):
                    raise ValueError("Attribute (%s) cannot contain (%s)." %
                            (key, invalid_value))

                # Attributes have to be alphanumeric-ish
                if not bool(has_valid_key):
                    raise ValueError("Key (%s) not alphanumeric-ish." % (key))

            datapoint['attributes'] = attributes

        self._queue.append(datapoint)
        logging.debug("QUEUE: " + str(len(self._queue)))

    def send(self, name=None, value=None, **kwargs):
        """
        Can accept a name/tag and value to be queued and then send anything in
        the queue to the time series service.  Optional parameters include
        setting quality, timestamp, or attributes.

        Example of sending a batch of values:

            queue('temp', 70.1)
            queue('humidity', 20.4)
            send()

        Example of sending one and flushing queue immediately

            send('temp', 70.3)
            send('temp', 70.4, quality=ts.GOOD, attributes={'unit': 'F'})

        """
        if name and value:
            self.queue(name, value, **kwargs)

        timestamp = int(round(time.time() * 1000))

        # The label "name" or "tag" is sometimes used ambiguously
        msg = {
            "messageId": timestamp,
            "body": self._queue
        }

        self._queue = []

        return self._send_to_timeseries(msg)

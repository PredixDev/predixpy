
import os
import re
import time
import json
import logging
import datetime
import websocket

import predix.config
import predix.service


class TimeSeries(object):
    """
    Client library for working with the Time Series service.

    :param query_uri: URI for Time Series endpoint to execute queries, can be
        derived from environment PREDIX_TIMESERIES_QUERY_URI variable if not
        passed.

    :param ingest_uri: URI for Time Series endpoint to ingest data, can be
        derived from environment PREDIX_TIMESERIES_INGEST_URI variable if not
        passed.

    :param query_zone_id: Predix-Zone-Id for Query Authorization, can be
        derived from environment PREDIX_TIMESERIES_QUERY_ZONE_ID.

    :param ingest_zone_id: Predix-Zone-Id for Ingest Authorization, can be
        derived from environment PREDIX_TIMESERIES_INGEST_ZONE_ID.

    :param read: Whether we expect to be able to query / read data.

    :param write: Whether we expect to be able to ingest / write data.

    Learn more about Predix Time Series:
    https://www.predix.io/services/service.html?id=1177

    """
    # "Constants" for data quality values
    BAD = 0
    UNCERTAIN = 1
    NA = 2
    GOOD = 3

    def __init__(self, read=True, write=True, query_uri=None, ingest_uri=None,
            query_zone_id=None, ingest_zone_id=None, *args, **kwargs):
        """
        Time Series by default will grant the client both read
        and write permissions.  Either can be disabled.
        """
        super(TimeSeries, self).__init__(*args, **kwargs)

        # Not all clients can read and write, so look to arguments on whether
        # to validate permissions during initialization.
        if read:
            self.query_uri = query_uri or self._get_query_uri()
            self.query_zone_id = query_zone_id or self._get_query_zone_id()

        if write:
            self.ingest_uri = ingest_uri or self._get_ingest_uri()
            self.ingest_zone_id = ingest_zone_id or self._get_ingest_zone_id()

        self.zone_id = self.query_zone_id or self.ingest_zone_id
        self.service = predix.service.Service(self.zone_id)

        # Store a websocket connection once opened
        self.ws = None

        # Store in-memory and forward any datapoints as a single transaction
        self._queue = []

    def _get_query_uri(self):
        """
        Returns the URI endpoint for performing queries of a
        Predix Time Series instance from environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_timeseries = services['predix-timeseries'][0]['credentials']
            return predix_timeseries['query']['uri'].partition('/v1')[0]
        else:
            return predix.config.get_env_value(self, 'query_uri')

    def _get_query_zone_id(self):
        """
        Returns the ZoneId for performing queries of a Predix
        Time Series instance from environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_timeseries = services['predix-timeseries'][0]['credentials']
            return predix_timeseries['query']['zone-http-header-value']
        else:
            return predix.config.get_env_value(self, 'query_zone_id')

    def _get_ingest_uri(self):
        """
        Returns the URI endpoint for performing ingestion of data to
        Predix Time Series instance from environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_timeseries = services['predix-timeseries'][0]['credentials']
            return predix_timeseries['ingest']['uri']
        else:
            return predix.config.get_env_value(self, 'ingest_uri')

    def _get_ingest_zone_id(self):
        """
        Returns the ZoneId for ingesting data to a Predix
        Time Series instance from environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            predix_timeseries = services['predix-timeseries'][0]['credentials']
            return predix_timeseries['ingest']['zone-http-header-value']
        else:
            return predix.config.get_env_value(self, 'ingest_zone_id')

    def __del__(self):
        """
        Destructor to make sure an open websocket connection is closed.
        """
        # No need to delete if not properly initialized
        if not hasattr(self, '_queue'):
            return

        if len(self._queue) > 0:
            logging.warning("%s buffered datapoints in queue lost." %
                    (len(self._queue)))

        if self.ws:
            self.ws.close()

    def authenticate_as_client(self, client_id, client_secret):
        """
        Will authenticate for the given client / secret.
        """
        self.service.uaa.authenticate(client_id, client_secret)

    def _get_aggregations(self):
        """
        Returns all of the aggregations in time series.  There is no support
        in the service for filtering or paginations.
        """
        url = self.query_uri + '/v1/aggregations'
        return self.service._get(url)

    def get_aggregations(self):
        """
        Returns all of the aggregations that can be used with the
        Time Series Service.
        """
        return self._get_aggregations()['results']

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
            - attributes: dictionary of key-values (ie. {'unit': 'mph'})
            - measurement: tuple of operation and value (ie. ('gt', 30))
            - aggregations: summary statistics on data results (ie. 'avg')
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
            logging.warning("Defaulting query for data with start date %s" % (start))

        # Start date can be absolute or relative, only certain legal values
        # but service will throw error if used improperly.  (ms, s, mi, h, d,
        # w, mm, y).  Relative dates must end in -ago.
        params['start'] = start

        # Docs say when making POST with a start that end must also be
        # specified, but this does not seem to be the case.
        if end:
            # MAINT: error when end < start which is handled by service
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

            # Handle any additional aggregations of dataset
            if aggregations is not None:
                if not isinstance(aggregations, list):
                    aggregations = [aggregations]

                query['aggregations'] = []
                for aggregation in aggregations:
                    query['aggregations'].append({
                        'sampling': {'datapoints': 1},
                        'type': aggregation })

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
        if isinstance(tags, list):
            params['tags'] = str.join(',', tags)
        elif isinstance(tags, str):
            params['tags'] = tags
        else:
            raise ValueError("Expect to get tags as a str or list")

        if post:
            return self._post_latest(params)
        else:
            return self._get_latest(params)

    def _create_connection(self):
        """
        Create a new websocket connection with proper headers.
        """
        logging.debug("Initializing new websocket connection.")
        headers = {
            'Authorization': self.service._get_bearer_token(),
            'Predix-Zone-Id': self.ingest_zone_id,
            'Content-Type': 'application/json',
        }
        url = self.ingest_uri

        logging.debug("URL=" + str(url))
        logging.debug("HEADERS=" + str(headers))

        # Should consider connection pooling and longer timeouts
        return websocket.create_connection(url, header=headers)

    def _get_websocket(self, reuse=True):
        """
        Reuse existing connection or create a new connection.
        """
        # Check if still connected
        if self.ws and reuse:
            if self.ws.connected:
                return self.ws

            logging.debug("Stale connection, reconnecting.")

        self.ws = self._create_connection()
        return self.ws

    def _send_to_timeseries(self, message):
        """
        Establish or reuse socket connection and send
        the given message to the timeseries service.
        """
        logging.debug("MESSAGE=" + str(message))

        result = None
        try:
            ws = self._get_websocket()
            ws.send(json.dumps(message))
            result = ws.recv()
        except (websocket.WebSocketConnectionClosedException, Exception) as e:
            logging.debug("Connection failed, will try again.")
            logging.debug(e)

            ws = self._get_websocket(reuse=False)
            ws.send(json.dumps(message))
            result = ws.recv()

        logging.debug("RESULT=" + str(result))
        return result

    def queue(self, name, value, quality=None, timestamp=None,
            attributes=None):
        """
        To reduce network traffic, you can buffer datapoints and
        then flush() anything in the queue.

        :param name: the name / label / tag for sensor data

        :param value: the sensor reading or value to record

        :param quality: the quality value, use the constants BAD, GOOD, etc.
            (optional and defaults to UNCERTAIN)

        :param timestamp: the time the reading was recorded in epoch
            milliseconds (optional and defaults to now)

        :param attributes: dictionary for any key-value pairs to store with the
            reading (optional)

        """
        # Get timestamp first in case delay opening websocket connection
        # and it must have millisecond accuracy
        if not timestamp:
            timestamp = int(round(time.time() * 1000))
        else:
            # Coerce datetime objects to epoch
            if isinstance(timestamp, datetime.datetime):
                timestamp = int(round(int(timestamp.strftime('%s')) * 1000))

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

        # Attributes are extra details for a datapoint

        if attributes is not None:
            if not isinstance(attributes, dict):
                raise ValueError("Attributes are expected to be a dictionary.")

            # Validate rules for attribute keys to provide guidance.
            invalid_value = ':;= '
            has_invalid_value = re.compile(r'[%s]' % (invalid_value)).search
            has_valid_key = re.compile(r'^[\w\.\/\-]+$').search

            for (key, val) in list(attributes.items()):
                # Values cannot be empty
                if (val == '') or (val is None):
                    raise ValueError("Attribute (%s) must have a non-empty value." % (key))

                # Values should be treated as a string for regex validation
                val = str(val)

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

        See spec for queue() for complete list of options.

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


import os
import time
import logging
import tempfile
import unittest
import datetime

import predix.admin.app
import predix.admin.cf.spaces

class TestTimeSeries(unittest.TestCase):
    """
    More Testing
    - [ ] Query on multiple tags
    - [ ] Get aggregations
    - [ ] Get values
    """

    @classmethod
    def setUpClass(cls):
        cls.space = predix.admin.cf.spaces.create_temp_space()
        cls.manifest_path = tempfile.mktemp(suffix='.yml', prefix='manifest_')
        print("Created test space {}".format(cls.space.name))
        print("Created manifest {}".format(cls.manifest_path))

        cls.admin = predix.admin.app.Manifest(cls.manifest_path,
                encrypted=True)
        cls.admin.create_uaa(cls.space.name)
        cls.admin.create_client('client-id', cls.space.name)
        cls.admin.create_timeseries()

        cls.app = predix.app.Manifest(cls.manifest_path)

    @classmethod
    def tearDownClass(cls):
        cls.space.delete_space()
        print("Deleted test space %s" % (cls.space.name))

    def test_timeseries_created(self):
        ts = self.app.get_timeseries()
        self.assertIsInstance(ts, predix.data.timeseries.TimeSeries)

    def test_ingest_basics(self):
        ts = self.app.get_timeseries()

        ts.send('TAG1', 15)
        ts.send('TAG1', 20)

        ts.queue('TAG2', 30)
        ts.queue('TAG2', 40)
        ts.send()

        time.sleep(2) # Allow time for ingestion to complete

        tags = ts.get_tags()
        self.assertTrue('TAG1' in tags)
        self.assertTrue('TAG2' in tags)

    def test_ingest_quality(self):
        ts = self.app.get_timeseries()

        ts.send('TAG3', 50, quality=ts.BAD)
        time.sleep(2) # Allow time for ingestion to complete

        res = ts.get_datapoints('TAG3')
        values = res['tags'][0]['results'][0]['values']
        attrs = res['tags'][0]['results'][0]['attributes']
        self.assertEqual('TAG3', res['tags'][0]['name'])
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0][1], 50)
        self.assertEqual(values[0][2], 0)
        self.assertEqual(attrs, {})

    def test_ingest_attributes(self):
        ts = self.app.get_timeseries()

        ts.send('TAG4', 60, attributes={'units': 'F'})
        time.sleep(2) # Allow time for ingestion to complete

        res = ts.get_datapoints('TAG4')
        values = res['tags'][0]['results'][0]['values']
        attrs = res['tags'][0]['results'][0]['attributes']
        self.assertEqual('TAG4', res['tags'][0]['name'])
        self.assertEqual(values[0][2], 1)
        self.assertEqual(attrs, {'units':['F']})

        # Test multiple attributes, including a number
        ts.send('TAG4b', 61, attributes={'units': 'F', 'Number': 1})
        time.sleep(2) # Allow time for ingestion to complete
        res = ts.get_datapoints('TAG4b')
        self.assertEqual('TAG4b', res['tags'][0]['name'])

        # Test we get error if attributes is not a dictionary
        with self.assertRaises(ValueError):
            ts.send('TAG4b', 62, attributes="{'units': 'F'}")

    def test_ingest_timestamp(self):
        ts = self.app.get_timeseries()

        birthday = datetime.datetime(1979, 9, 20)
        ts.send('TAG5', 70, timestamp=birthday)
        ts.send('TAG5', 80)

        time.sleep(2) # Allow time for ingestion to complete

        res = ts.get_datapoints('TAG5', start='50y-ago', end='1y-ago')
        self.assertEqual(res['tags'][0]['stats']['rawCount'], 1)
        res = ts.get_datapoints('TAG5', start='50y-ago', order='asc')
        self.assertEqual(res['tags'][0]['stats']['rawCount'], 2)
        values = res['tags'][0]['results'][0]['values']
        self.assertEqual(values[0][0], 306658800000)

        # Verify can search with epoch dates, not just relative dates

        res = ts.get_datapoints('TAG5', start=292185600000, end=313267200000)
        values = res['tags'][0]['results'][0]['values']
        self.assertEqual(values[0][1], 70)

    def test_query_filter_aggregation(self):
        ts = self.app.get_timeseries()
        tag = 'STACK1'
        values = [-999, -5, 10, 20, 30]
        for val in values:
            ts.send(tag, val)

        time.sleep(5) # Allow time for ingestion to complete

        query = ts.get_datapoints(tag, measurement=('gt', -999), aggregations='sum')
        result = query['tags'][0]['results'][0]['values'][0][1]
        self.assertEqual(result, sum(values[1:]))

    def test_get_latest(self):
        ts = self.app.get_timeseries()
        ts.send('LATEST-1', 1)
        ts.send('LATEST-2', 2)
        time.sleep(2) # Allow time for ingestion

        res = ts.get_latest(['LATEST-1', 'LATEST-2'])
        self.assertEqual(len(res['tags']), 2)
        self.assertEqual(res['tags'][0]['name'], 'LATEST-1')

if __name__ == '__main__':
    if os.getenv('DEBUG'):
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()

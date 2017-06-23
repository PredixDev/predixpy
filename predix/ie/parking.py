
import os
import logging

import predix.service


class ParkingPlanning(object):
    """
    The Parking Planning service provides (in beta) provides simulated data
    collected from street lights installed in specific cities.
    """

    # Constants for a few known bounding-box locations that have good data
    BBOX = {
            'USA': {
                'CA': {
                    'San Diego': '32.715675:-117.161230,32.708498:-117.151681',
                    }
                }
            }

    # Constants for device types
    DEVICE_TYPES = [
            'DATASIM'
            ]

    # Constants for codes representing asset types
    ASSET_TYPES = [
            'CAMERA',
            'ENV_SENSOR',
            'MIC',
            'NODE',
            'OTHERS'
            ]

    # Constants for codes represent event types
    EVENT_TYPES = [
            'HUMIDITY',
            'PEDEVT',
            'PKIN',
            'PKOUT',
            'PRESSURE',
            'TEMPERATURE',
            'TFEVT'
            ]

    # Constants for codes representing media
    MEDIA_TYPES = [
            'AUDIO',
            'IMAGE',
            'VIDEO',
            'OTHERS'
            ]

    def __init__(self):
        ns = 'predix.admin.ie.parking'
        self.zone_id = os.environ.get(ns + '.zone_id')
        if not self.zone_id:
            raise ValueError("%s.zone_id environment unset" % ns)

        self.uri = os.environ.get(ns + '.uri')
        if not self.uri:
            raise ValueError("%s.uri environment unset" % ns)

        self.service = predix.service.Service(self.zone_id)

    def authenticate_as_client(self, client_id, client_secret):
        """
        Will authenticate for the given client / secret.
        """
        self.service.uaa.authenticate(client_id, client_secret)

    def _get_headers(self):
        """
        Returns headers needed for making any service calls.
        """
        # Service will return a 500 if Accepts/Content-Type headers are used.
        headers = {
            'Predix-Zone-Id': self.zone_id,
            'Authorization': self.service._get_bearer_token()
            }
        return headers

    def _get_assets(self, bbox, size=None, page=None, asset_type=None,
            device_type=None, event_type=None, media_type=None):
        """
        Returns the raw results of an asset search for a given bounding
        box.
        """
        uri = self.uri + '/v1/assets/search'
        headers = self._get_headers()

        params = {
                'bbox': bbox,
                }

        # Query parameters

        params['q'] = []
        if device_type:
            if isinstance(device_type, str):
                device_type = [device_type]

            for device in device_type:
                if device not in self.DEVICE_TYPES:
                    logging.warn("Invalid device type: %s" % device)

                params['q'].append("device-type:%s" % device)

        if asset_type:
            if isinstance(asset_type, str):
                asset_type = [asset_type]

            for asset in asset_type:
                if asset not in self.ASSET_TYPES:
                    logging.warn("Invalid asset type: %s" % asset)
                params['q'].append("assetType:%s" % asset)

        if media_type:
            if isinstance(media_type, str):
                media_type = [media_type]

            for media in media_type:
                if media not in self.MEDIA_TYPES:
                    logging.warn("Invalid media type: %s" % media)
                params['q'].append("mediaType:%s" % media)

        if event_type:
            if isinstance(event_type, str):
                event_type = [event_type]

            for event in event_type:
                if event not in self.EVENT_TYPES:
                    logging.warn("Invalid event type: %s" % event)
                params['q'].append("eventTypes:%s" % event)

        # Pagination parameters

        if size:
            params['size'] = size

        if page:
            params['page'] = page

        return self.service._get(uri, params=params, headers=headers)

    def get_assets(self, bbox, **kwargs):
        """
        Query the assets stored in the intelligent environment for a given
        bounding box and query.

        Assets can be filtered by type of asset, event, or media available.

            - device_type=['DATASIM']
            - asset_type=['CAMERA']
            - event_type=['PKIN']
            - media_type=['IMAGE']

        Pagination can be controlled with keyword parameters

            - page=2
            - size=100

        Returns a list of assets stored in a dictionary that describe their:

            - asset-id
            - device-type
            - device-id
            - media-type
            - coordinates
            - event-type

        Additionally there are some _links for additional information.
        """
        response = self._get_assets(bbox, **kwargs)

        # Remove broken HATEOAS _links but identify asset uid first
        assets = []
        for asset in response['_embedded']['assets']:
            asset_url = asset['_links']['self']
            uid = asset_url['href'].split('/')[-1]
            asset['uid'] = uid

            del(asset['_links'])
            assets.append(asset)

        return assets

    def _get_asset(self, asset_uid):
        """
        Returns raw response for an given asset by its unique id.
        """
        uri = self.uri + '/v2/assets/' + asset_uid

        headers = self._get_headers()

        return self.service._get(uri, headers=headers)

    def get_asset(self, asset_uid):
        """
        Return details for a given asset.
        """
        response = self._get_asset(asset_uid)

        del(response['_links'])

        return response


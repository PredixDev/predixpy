
import os
import json
import uuid
import logging
import requests

import predix.service
import predix.security.uaa


class Asset(object):
    """
    Client library for working with the Asset service.
    """
    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)

        self.zone_id = os.environ.get('PREDIX_ASSET_ZONE_ID')
        if not self.zone_id:
            raise ValueError('PREDIX_ASSET_ZONE_ID environment unset')

        self.uri = os.environ.get('PREDIX_ASSET_URI')
        if not self.uri:
            raise ValueError('PREDIX_ASSET_URI environment unset')

        self.service = predix.service.Service(self.zone_id)

    def authenticate_as_client(self, client_id, client_secret):
        """
        Will authenticate for the given client / secret.
        """
        self.service.uaa.authenticate(client_id, client_secret)

    def _get_collections(self):
        """
        Returns the names of all user-defined domain object collections with
        counts for number of domain objects contained in that collection.

        [ { "collection": "volcano", "count": 1 }, ... ]

        """
        uri = self.uri
        return self.service._get(uri)

    def get_collections(self):
        """
        Returns a flat list of the names of collections in the asset
        service.
        """
        collections = []
        for result in self._get_collections():
            collections.append(result['collection'])

        return collections

    def get_collection(self, collection, filter=None, fields=None,
            page_size=None):
        """
        Returns a specific collection from the asset service with
        the given collection endpoint.

        Supports passing through parameters such as...
        - filters such as "name=Vesuvius"
        - fields such as "uri,description"
        - page_size such as "100" (the default)

        """
        params = {}
        if filter:
            params['filter'] = filter
        if fields:
            params['fields'] = fields
        if page_size:
            params['pageSize'] = page_size

        uri = self.uri + '/v1' + collection
        return self.service._get(uri, params=params)

    def post_collection(self, collection, body):
        """
        Creates a new collection.  This is mostly just transport layer
        and passes collection and body along.  It presumes the body
        already has generated.

        The collection is *not* expected to have the id.
        """
        assert isinstance(body, (list)), "POST requires body to be a list"
        assert collection.startswith('/'), "Collections must start with /"
        uri = self.uri + '/v1' + collection
        return self.service._post(uri, body)

    def put_collection(self, collection, body):
        """
        Updates an existing collection.

        The collection being updated *is* expected to include the id.
        """

        uri = self.uri + '/v1' + collection
        return self.service._put(uri, body)

    def delete_collection(self, collection):
        """
        Deletes an existing collection.

        The collection being updated *is* expected to include the id.
        """
        uri = str.join('/', [self.uri, collection])
        return self.service._delete(uri)

    def patch_collection(self, collection, changes):
        """
        Will make specific updates to a record based on JSON Patch
        documentation.

            https://tools.ietf.org/html/rfc6902

        the format of changes is something like:

            [{
                'op': 'add',
                'path': '/newfield',
                'value': 'just added'
            }]

        """
        uri = str.join('/', [self.uri, collection])
        return self.service._patch(uri, changes)

    def get_audit(self):
        """
        Return audit report for asset.  Disabled by default.
        """
        return self.service._get(self.uri + '/v1/system/audit')

    def get_audit_changes(self):
        """
        Return change log for audit.  Disabled by default.
        """
        return self.service._get(self.uri + '/v1/system/audit/changes')

    def get_audit_snapshots(self):
        """
        Return an audit snapshot.  Disabled by default.
        """
        return self.service._get(self.uri + '/v1/system/audit/snapshots')

    def get_scripts(self):
        """
        Return any configured scripts for asset service.
        """
        return self.service._get(self.uri + '/v1/system/scripts')

    def get_messages(self):
        """
        Return any system messages related to asset systems.
        """
        return self.service._get(self.uri + '/v1/system/messages')

    def get_configs(self):
        """
        Return the configuration for the asset service.
        """
        return self.service._get(self.uri + '/v1/system/configs')

    def get_triggers(self):
        """
        Return configured triggers in the asset system.
        """
        return self.service._get(self.uri + '/v1/system/triggers')

    def save(self, collection):
        """
        Save an asset collection to the service.
        """
        assert isinstance(collection, predix.data.asset.AssetCollection), "Expected AssetCollection"
        collection.validate()
        self.put_collection(collection.uri, collection.__dict__) # MAINT: no

class AssetCollection(object):
    """
    User Defined Domain Objects are the customizable collections to represent
    data in the Asset Service.

    This is experimental to provide a base class for a sort of ORM between
    domain objects to marshall and unmarshall between Python and the REST
    endpoints.
    """
    def __init__(self, parent=None, guid=None, *args, **kwargs):
        super(AssetCollection, self).__init__(*args, **kwargs)

        # You have the right to a guid, if you cannot afford a guid...
        if not guid:
            guid = str(uuid.uuid4())

        # By naming collection after classname we get safe URI
        # naming rules as well.
        collection = self.get_collection()

        # There is a no more than 2 forward slash limitation for uri, so
        # collections cannot really be nested deeper than one level.
        self.uri = '/' + str.join('/', [collection, guid])

    def __repr__(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return json.dumps(self.__dict__)

    def get_collection(self):
        return type(self).__name__.lower()

    def validate(self):
        """
        If an asset collection wants any client-side validation the
        object can override this method and it is called anytime
        we're saving.
        """
        return

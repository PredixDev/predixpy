
import os
import urlparse

import predix.config
import predix.security.uaa
import predix.admin.service
import predix.data.timeseries


class TimeSeries(object):
    """
    Time Series provides persistence of data values over time.
    """
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(TimeSeries, self).__init__(*args, **kwargs)
        self.service_name = 'predix-timeseries'
        self.plan_name = plan_name or 'Free'
        self.use_class = predix.data.timeseries.TimeSeries

        self.service = predix.admin.service.PredixService(self.service_name,
                self.plan_name, name=name, uaa=uaa)

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Create an instance of the Time Series Service with the typical
        starting settings.
        """
        self.service.create()

        uri = predix.config.get_env_key(self.use_class, 'ingest_uri')
        os.environ[uri] = self.get_ingest_uri()

        zone_id = predix.config.get_env_key(self.use_class, 'ingest_zone_id')
        os.environ[zone_id] = self.get_ingest_zone_id()

        uri = predix.config.get_env_key(self.use_class, 'query_uri')
        os.environ[uri] = self.get_query_uri()

        zone_id = predix.config.get_env_key(self.use_class, 'query_zone_id')
        os.environ[zone_id] = self.get_query_zone_id()

    def grant_client(self, client_id, read=True, write=True):
        """
        Grant the given client id all the scopes and authorities
        needed to work with the timeseries service.
        """
        scopes = ['openid']
        authorities = ['uaa.resource']

        if write:
            for zone in self.service.settings.data['ingest']['zone-token-scopes']:
                scopes.append(zone)
                authorities.append(zone)

        if read:
            for zone in self.service.settings.data['query']['zone-token-scopes']:
                scopes.append(zone)
                authorities.append(zone)

        self.service.uaa.uaac.update_client_grants(client_id, scope=scopes,
                authorities=authorities)

        return self.service.uaa.uaac.get_client(client_id)

    def get_ingest_zone_id(self):
        """
        Returns the Predix-Zone-Id used for ingesting data with this
        service.
        """
        return self.service.settings.data['ingest']['zone-http-header-value']

    def get_query_zone_id(self):
        """
        Return the Predix-Zone-Id used for queries on data with this
        service.
        """
        return self.service.settings.data['query']['zone-http-header-value']

    def get_ingest_uri(self):
        """
        Return the uri used for ingesting data into time series 
        """
        return self.service.settings.data['ingest']['uri']

    def get_query_uri(self):
        """
        Return the uri used for queries on time series data.
        """
        # Query URI has extra path we don't want so strip it off here
        query_uri = self.service.settings.data['query']['uri']
        query_uri = urlparse.urlparse(query_uri)
        return query_uri.scheme + '://' + query_uri.netloc

    def add_to_manifest(self, manifest):
        """
        Add useful details to the manifest about this service
        so that it can be used in an application.

        :param manifest: An predix.admin.app.Manifest object
            instance that manages reading/writing manifest config
            for a cloud foundry app.
        """
        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variables
        uri = predix.config.get_env_key(self.use_class, 'ingest_uri')
        manifest.add_env_var(uri, self.get_ingest_uri())

        zone_id = predix.config.get_env_key(self.use_class, 'ingest_zone_id')
        manifest.add_env_var(zone_id, self.get_ingest_zone_id())

        uri = predix.config.get_env_key(self.use_class, 'query_uri')
        manifest.add_env_var(uri, self.get_query_uri())

        zone_id = predix.config.get_env_key(self.use_class, 'query_zone_id')
        manifest.add_env_var(zone_id, self.get_query_zone_id())

        manifest.write_manifest()

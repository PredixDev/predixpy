
import os
import urlparse

import predix.app
import predix.security.uaa
import predix.admin.service


class TimeSeries(object):
    """
    Time Series provides persistence of data values over time.
    """
    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        super(TimeSeries, self).__init__(*args, **kwargs)
        self.service_name = 'predix-timeseries'
        self.plan_name = plan_name or 'Free'
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

        uri = self.service.settings.data['ingest']['uri']
        os.environ['PREDIX_TIMESERIES_INGEST_URI'] = uri

        zone = self.get_ingest_zone_id()
        os.environ['PREDIX_TIMESERIES_INGEST_ZONE_ID'] = zone

        uri = self.service.settings.data['query']['uri']
        uri = urlparse.urlparse(uri)
        os.environ['PREDIX_TIMESERIES_QUERY_URI'] = uri.scheme + '://' + uri.netloc

        zone = self.get_query_zone_id()
        os.environ['PREDIX_TIMESERIES_QUERY_ZONE_ID'] = zone

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

    def add_to_manifest(self, manifest_path):
        """
        Add details to the manifest that applications using
        this service may need to consume.
        """
        manifest = predix.app.Manifest(manifest_path)

        # Add this service to list of services
        manifest.add_service(self.service.name)

        # Add environment variables
        manifest.add_env_var('PREDIX_TIMESERIES_INGEST_URI',
                self.service.settings.data['ingest']['uri'])
        manifest.add_env_var('PREDIX_TIMESERIES_INGEST_ZONE_ID',
                self.get_ingest_zone_id())

        # Query URI has extra path we don't want
        uri = self.service.settings.data['query']['uri']
        uri = urlparse.urlparse(uri)
        manifest.add_env_var('PREDIX_TIMESERIES_QUERY_URI',
                uri.scheme + '://' + uri.netloc)
        manifest.add_env_var('PREDIX_TIMESERIES_QUERY_ZONE_ID',
                self.get_query_zone_id())

        manifest.write_manifest()

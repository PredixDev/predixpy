
import logging

import predix.app
import predix.admin.uaa
import predix.admin.acs
import predix.admin.asset
import predix.admin.weather
import predix.admin.cf.spaces
import predix.admin.blobstore
import predix.admin.timeseries
import predix.admin.logstash
import predix.admin.cache
import predix.admin.dbaas


class Manifest(predix.app.Manifest):
    """
    Extends Application Manifest with administrative
    functions for creating and configuring services.
    """
    def __init__(self, *args, **kwargs):
        super(Manifest, self).__init__(*args, **kwargs)

        self.space = predix.admin.cf.spaces.Space()
        self.services = predix.admin.cf.services.Service()

        self.supported = {
            'predix-uaa': predix.admin.uaa.UserAccountAuthentication,
            'predix-acs': predix.admin.acs.AccessControl,
            'predix-asset': predix.admin.asset.Asset,
            'predix-blobstore': predix.admin.blobstore.BlobStore,
            'predix-cache': predix.admin.cache.Cache,
            'predix-dbaas': predix.admin.dbaas.PostgreSQL,
            'predix-timeseries': predix.admin.timeseries.TimeSeries,
            'predix-weather': predix.admin.weather.WeatherForecast,
            'predix-logging': predix.admin.logstash.Logging,
        }

    def create_manifest_from_space(self):
        """
        Populate a manifest file generated from details from the
        cloud foundry space environment.
        """
        space = predix.admin.cf.spaces.Space()

        summary = space.get_space_summary()
        for instance in summary['services']:
            service_type = instance['service_plan']['service']['label']
            name = instance['name']
            if service_type in self.supported:
                service = self.supported[service_type](name=name)
                service.add_to_manifest(self)
            elif service_type == 'us-weather-forecast':
                weather = predix.admin.weather.WeatherForecast(name=name)
                weather.add_to_manifest(self)
            else:
                logging.warning("Unsupported service type: %s" % service_type)

    def lock_to_org_space(self):
        """
        Lock the manifest to the current organization and space regardless of
        Cloud Foundry target.
        """
        self.add_env_var('PREDIX_ORGANIZATION_GUID', self.space.org.guid)
        self.add_env_var('PREDIX_ORGANIZATION_NAME', self.space.org.name)
        self.add_env_var('PREDIX_SPACE_GUID', self.space.guid)
        self.add_env_var('PREDIX_SPACE_NAME', self.space.name)
        self.write_manifest()

    def create_uaa(self, admin_secret, **kwargs):
        """
        Creates an instance of UAA Service.

        :param admin_secret: The secret password for administering the service
            such as adding clients and users.
        """
        uaa = predix.admin.uaa.UserAccountAuthentication(**kwargs)
        if not uaa.exists():
            uaa.create(admin_secret, **kwargs)
            uaa.add_to_manifest(self)
        return uaa

    def create_client(self, client_id=None, client_secret=None, uaa=None):
        """
        Create a client and add it to the manifest.

        :param client_id: The client id used to authenticate as a client
            in UAA.

        :param client_secret: The secret password used by a client to
            authenticate and generate a UAA token.

        :param uaa: The UAA to create client with
        """
        if not uaa:
            uaa = predix.admin.uaa.UserAccountAuthentication()

        # Client id and secret can be generated if not provided as arguments

        if not client_id:
            client_id = uaa._create_id()

        if not client_secret:
            client_secret = uaa._create_secret()

        uaa.create_client(client_id, client_secret)
        uaa.add_client_to_manifest(client_id, client_secret, self)

    def create_timeseries(self, **kwargs):
        """
        Creates an instance of the Time Series Service.
        """
        ts = predix.admin.timeseries.TimeSeries(**kwargs)
        ts.create()

        client_id = self.get_client_id()
        if client_id:
            ts.grant_client(client_id)

        ts.add_to_manifest(self)
        return ts

    def create_asset(self, **kwargs):
        """
        Creates an instance of the Asset Service.
        """
        asset = predix.admin.asset.Asset(**kwargs)
        asset.create()

        client_id = self.get_client_id()
        if client_id:
            asset.grant_client(client_id)

        asset.add_to_manifest(self)
        return asset

    def create_acs(self, **kwargs):
        """
        Creates an instance of the Asset Service.
        """
        acs = predix.admin.acs.AccessControl(**kwargs)
        acs.create()

        client_id = self.get_client_id()
        if client_id:
            acs.grant_client(client_id)

        acs.grant_client(client_id)
        acs.add_to_manifest(self)
        return acs

    def create_weather(self, **kwargs):
        """
        Creates an instance of the Asset Service.
        """
        weather = predix.admin.weather.WeatherForecast(**kwargs)
        weather.create()

        client_id = self.get_client_id()
        if client_id:
            weather.grant_client(client_id)

        weather.grant_client(client_id)
        weather.add_to_manifest(self)
        return weather

    def create_blobstore(self, **kwargs):
        """
        Creates an instance of the BlobStore Service.
        """
        blobstore = predix.admin.blobstore.BlobStore(**kwargs)
        blobstore.create()

        blobstore.add_to_manifest(self)
        return blobstore

    def create_logstash(self, **kwargs):
        """
        Creates an instance of the Logging Service.
        """
        logstash = predix.admin.logstash.Logging(**kwargs)
        logstash.create()
        logstash.add_to_manifest(self)

        logging.info('Install Kibana-Me-Logs application by following GitHub instructions')
        logging.info('git clone https://github.com/cloudfoundry-community/kibana-me-logs.git')

        return logstash

    def create_cache(self, **kwargs):
        """
        Creates an instance of the Cache Service.
        """
        cache = predix.admin.cache.Cache(**kwargs)
        cache.create(**kwargs)
        cache.add_to_manifest(self)
        return cache

    def create_dbaas(self, **kwargs):
        """
        """
        pg = predix.admin.dbaas.PostgreSQL(**kwargs)
        pg.create()
        pg.add_to_manifest(self)
        return pg

    def create_eventhub(self, **kwargs):
        """
        todo make it so the client can be customised to publish/subscribe
        Creates an instance of eventhub service
        """
        eventhub = predix.admin.eventhub.EventHub(**kwargs)
        eventhub.create()
        eventhub.add_to_manifest(self)
        eventhub.grant_client(client_id=self.get_client_id(), **kwargs)
        eventhub.add_to_manifest(self)
        return eventhub


    def get_service_marketplace(self, available=True, unavailable=False,
            deprecated=False):
        """
        Returns a list of service names.  Can return all services, just
        those supported by PredixPy, or just those not yet supported by
        PredixPy.

        :param available: Return the services that are
            available in PredixPy.  (Defaults to True)

        :param unavailable: Return the services that are not yet
            supported by PredixPy.  (Defaults to False)

        :param deprecated: Return the services that are
            supported by PredixPy but no longer available. (True)
        """

        supported = set(self.supported.keys())
        all_services = set(self.space.get_services())

        results = set()
        if available:
            results.update(supported)
        if unavailable:
            results.update(all_services.difference(supported))
        if deprecated:
            results.update(supported.difference(all_services))

        return list(results)

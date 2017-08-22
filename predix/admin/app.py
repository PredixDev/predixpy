
import predix.app
import predix.admin.uaa
import predix.admin.acs
import predix.admin.asset
import predix.admin.weather
import predix.admin.cf.spaces
import predix.admin.blobstore
import predix.admin.timeseries


class Manifest(predix.app.Manifest):
    """
    Extends Application Manifest with administrative
    functions for creating and configuring services.
    """
    def __init__(self, *args, **kwargs):
        super(Manifest, self).__init__(*args, **kwargs)

        self.space = predix.admin.cf.spaces.Space()

        self.supported = {
            'predix-uaa': predix.admin.uaa.UserAccountAuthentication,
            'predix-acs': predix.admin.acs.AccessControl,
            'predix-asset': predix.admin.asset.Asset,
            'predix-blobstore': predix.admin.blobstore.BlobStore,
            'predix-timeseries': predix.admin.timeseries.TimeSeries,
            'predix-weather': predix.admin.weather.WeatherForecast,
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
            if service_type == 'predix-uaa':
                uaa = predix.admin.uaa.UserAccountAuthentication(name=name)
                uaa.add_to_manifest(self)
            elif service_type == 'predix-acs':
                acs = predix.admin.acs.AccessControl(name=name)
                acs.add_to_manifest(self)
            elif service_type == 'predix-asset':
                asset = predix.admin.asset.Asset(name=name)
                asset.add_to_manifest(self)
            elif service_type == 'predix-timeseries':
                timeseries = predix.admin.timeseries.TimeSeries(name=name)
                timeseries.add_to_manifest(self)
            elif service_type == 'predix-blobstore':
                blobstore = predix.admin.blobstore.BlobStore(name=name)
                blobstore.add_to_manifest(self)
            elif service_type == 'us-weather-forecast':
                weather = predix.admin.weather.WeatherForecast(name=name)
                weather.add_to_manifest(self)
            else:
                logging.warn("Unsupported service type: %s" % service_type)

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

    def create_uaa(self, admin_secret):
        """
        Creates an instance of UAA Service.

        :param admin_secret: The secret password for administering the service
            such as adding clients and users.
        """
        uaa = predix.admin.uaa.UserAccountAuthentication()
        if not uaa.exists():
            uaa.create(admin_secret)
            uaa.add_to_manifest(self)
        return uaa

    def create_client(self, client_id, client_secret):
        """
        Create a client and add it to the manifest.

        :param client_id: The client id used to authenticate as a client
            in UAA.

        :param client_secret: The secret password used by a client to
            authenticate and generate a UAA token.
        """
        uaa = predix.admin.uaa.UserAccountAuthentication()
        uaa.create_client(client_id, client_secret)
        uaa.add_client_to_manifest(client_id, client_secret, self)

    def create_timeseries(self):
        """
        Creates an instance of the Time Series Service.
        """
        ts = predix.admin.timeseries.TimeSeries()
        ts.create()

        client_id = self.get_client_id()
        if client_id:
            ts.grant_client(client_id)

        ts.add_to_manifest(self)
        return ts

    def create_asset(self):
        """
        Creates an instance of the Asset Service.
        """
        asset = predix.admin.asset.Asset()
        asset.create()

        client_id = self.get_client_id()
        if client_id:
            asset.grant_client(client_id)

        asset.add_to_manifest(self)
        return asset

    def create_acs(self):
        """
        Creates an instance of the Asset Service.
        """
        acs = predix.admin.acs.AccessControl()
        acs.create()

        client_id = self.get_client_id()
        if client_id:
            acs.grant_client(client_id)

        acs.grant_client(client_id)
        acs.add_to_manifest(self)
        return acs

    def create_weather(self):
        """
        Creates an instance of the Asset Service.
        """
        weather = predix.admin.weather.WeatherForecast()
        weather.create()

        client_id = self.get_client_id()
        if client_id:
            weather.grant_client(client_id)

        weather.grant_client(client_id)
        weather.add_to_manifest(self)
        return weather

    def create_blobstore(self):
        """
        Creates an instance of the BlobStore Service.
        """
        blobstore = predix.admin.blobstore.BlobStore()
        blobstore.create()

        blobstore.add_to_manifest(self)
        return blobstore

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

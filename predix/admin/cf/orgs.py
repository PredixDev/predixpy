
import predix.admin.cf.api


class Org(object):
    """
    Operations and data for Cloud Foundry Organizations.
    """
    def __init__(self, *args, **kwargs):
        super(Org, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()
        self.name = self.api.config.get_organization_name()

    def _get_orgs(self):
        """
        Returns the organizations for the authenticated user.
        """
        return self.api.get('/v2/organizations')

    def get_orgs(self):
        """
        Returns a flat list of the names for the organizations
        user belongs.
        """
        orgs = []
        for resource in self._get_orgs()['resources']:
            orgs.append(resource['entity']['name'])

        return orgs

    def _get_apps(self):
        """
        Returns all of the apps in the organization.
        """
        return self.api.get('/v2/apps')

    def get_apps(self):
        """
        Returns a flat list of the names for the apps in
        the organization.
        """
        apps = []
        for resource in self._get_apps()['resources']:
            apps.append(resource['entity']['name'])

        return apps

    def has_app(self, app_name):
        """
        Simple test to see if we have a name conflict
        for the application.
        """
        return app_name in self.get_apps()

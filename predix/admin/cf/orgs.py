
import predix.admin.cf.api
import logging

class Org(object):
    """
    Operations and data for Cloud Foundry Organizations.
    """
    ROLE_MAP = {
        'user': '/v2/organizations/%s/users',
        'auditor': '/v2/organizations/%s/auditors',
        'manager': '/v2/organizations/%s/managers',
        'billing_manager': '/v2/organizations/%s/billing_managers'
    }
    
    def __init__(self, *args, **kwargs):
        super(Org, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()

        self.name = self.api.config.get_organization_name()
        self.guid = self.api.config.get_organization_guid()

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

    def add_user(self, user_name, role='user'):
        """
        Calls CF's associate user with org. Valid roles include `user`, `auditor`,
        `manager`,`billing_manager`
        """
        role_uri = self._get_role_uri(role=role)
        return self.api.put(path=role_uri, data={'username': user_name})

    def _get_role_uri(self, role):
        try:
            role_uri = self.ROLE_MAP[role]
            return role_uri % self.api.config.get_organization_guid()
        except KeyError:
            logging.error('"%s" role is not a valid role' % role)
            raise

    def remove_user(self, user_name, role):
        """
        Calls CF's remove user with org
        """
        role_uri = self._get_role_uri(role=role)
        return self.api.delete(path=role_uri, data={'username': user_name})


import logging

import predix.admin.cf.api
import predix.admin.cf.orgs
import predix.admin.cf.apps
import predix.admin.cf.services


class Space(object):
    """
    Operations and data for Cloud Foundry Spaces.
    """
    def __init__(self, *args, **kwargs):
        super(Space, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()

        self.name = self.api.config.get_space_name()
        self.guid = self.api.config.get_space_guid()

        self.org = predix.admin.cf.orgs.Org()

    def _get_spaces(self):
        """
        Get the marketplace services.
        """
        guid = self.api.config.get_organization_guid()
        uri = '/v2/organizations/%s/spaces' % (guid)
        return self.api.get(uri)

    def get_spaces(self):
        """
        Return a flat list of the names for spaces in the organization.
        """
        self.spaces = []
        for resource in self._get_org_spaces()['resources']:
            self.spaces.append(resource['entity']['name'])

        return self.spaces

    def get_space_services(self):
        """
        Returns the services available for use in the space.  This may
        not always be the same as the full marketplace.
        """
        uri = '/v2/spaces/%s/services' % (self.guid)
        return self.api.get(uri)

    def create_space(self, space_name):
        """
        Create a new space of the given name.
        """
        body = {
            'name': space_name,
            'organization_guid': self.api.config.get_organization_guid()
        }
        return self.api.post('/v2/spaces', body)

    def delete_space(self, space_name):
        """
        Delete a space of the given name.
        """
        return self.api.delete("/v2/spaces/%s" % (self.guid))

    def get_space_summary(self):
        """
        Returns a summary of apps and services within a given
        cloud foundry space.

        It is the call used by `cf s` or `cf a` for quicker
        responses.
        """
        uri = '/v2/spaces/%s/summary' % (self.guid)
        return self.api.get(uri)

    def _get_apps(self):
        """
        Returns raw results for all apps in the space.
        """
        uri = '/v2/spaces/%s/apps' % (self.guid)
        return self.api.get(uri)

    def get_apps(self):
        """
        Returns a list of all of the apps in the space.
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

    def _get_services(self):
        """
        Return the available services for this space.
        """
        uri = '/v2/spaces/%s/services' % (self.guid)
        return self.api.get(uri)

    def get_services(self):
        """
        Returns a flat list of the service names available
        from the marketplace for this space.
        """
        services = []
        for resource in self._get_services()['resources']:
            services.append(resource['entity']['label'])

        return services

    def _get_instances(self):
        """
        Returns the service instances activated in this space.
        """
        uri = '/v2/spaces/%s/service_instances' % (self.guid)
        return self.api.get(uri)

    def get_instances(self):
        """
        Returns a flat list of the names of services created
        in this space.
        """
        services = []
        for resource in self._get_instances()['resources']:
            services.append(resource['entity']['name'])

        return services

    def has_service_with_name(self, service_name):
        """
        Tests whether a service with the given name exists in
        this space.
        """
        return service_name in self.get_instances()

    def has_service_of_type(self, service_type):
        """
        Tests whether a service instance exists for the given
        service.
        """
        summary = self.get_space_summary()
        for instance in summary['services']:
            if service_type == instance['service_plan']['service']['label']:
                return True

        return False

    def purge(self):
        """
        Remove all services and apps from the space.

        Will leave the space itself, call delete_space() if you
        want to remove that too.

        Similar to `cf delete-space -f <space-name>`.
        """
        logging.warn("Purging all services from space %s" %
                (self.name))

        service = predix.admin.cf.services.Service()
        for service_name in self.get_instances():
            service.purge(service_name)

        apps = predix.admin.cf.apps.App()
        for app_name in self.get_apps():
            apps.delete_app(app_name)

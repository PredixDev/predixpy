
import os
import uuid
import logging

import predix.admin.cf.api
import predix.admin.cf.orgs
import predix.admin.cf.apps
import predix.admin.cf.services

def create_temp_space():
    """
    Create a new temporary cloud foundry space for
    a project.
    """
    # Truncating uuid to just take final 12 characters since space name
    # is used to name services and there is a 50 character limit on instance
    # names.  
    # MAINT: hacky with possible collisions
    unique_name = str(uuid.uuid4()).split('-')[-1]
    admin = predix.admin.cf.spaces.Space()
    res = admin.create_space(unique_name)

    space = predix.admin.cf.spaces.Space(
            guid=res['metadata']['guid'],
            name=res['entity']['name'])
    space.target()

    return space

class Space(object):
    """
    Operations and data for Cloud Foundry Spaces.
    """
    def __init__(self, name=None, guid=None, *args, **kwargs):
        super(Space, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()

        self.name = name or self.api.config.get_space_name()
        self.guid = guid or self.api.config.get_space_guid()

        self.org = predix.admin.cf.orgs.Org()

    def _get_spaces(self):
        """
        Get the marketplace services.
        """
        guid = self.api.config.get_organization_guid()
        uri = '/v2/organizations/%s/spaces' % (guid)
        return self.api.get(uri)

    def target(self):
        """
        Target the current space for any forthcoming Cloud Foundry
        operations.
        """
        # MAINT: I don't like this, but will deal later
        os.environ['PREDIX_SPACE_GUID'] = self.guid
        os.environ['PREDIX_SPACE_NAME'] = self.name
        os.environ['PREDIX_ORGANIZATION_GUID'] = self.org.guid
        os.environ['PREDIX_ORGANIZATION_NAME'] = self.org.name

    def get_spaces(self):
        """
        Return a flat list of the names for spaces in the organization.
        """
        self.spaces = []
        for resource in self._get_spaces()['resources']:
            self.spaces.append(resource['entity']['name'])

        return self.spaces

    def get_space_services(self):
        """
        Returns the services available for use in the space.  This may
        not always be the same as the full marketplace.
        """
        uri = '/v2/spaces/%s/services' % (self.guid)
        return self.api.get(uri)

    def create_space(self, space_name, add_users=True):
        """
        Create a new space with the given name in the current target
        organization.
        """
        body = {
            'name': space_name,
            'organization_guid': self.api.config.get_organization_guid()
        }

        # MAINT: may need to do this more generally later
        if add_users:
            space_users = []
            org_users = self.org.get_users()
            for org_user in org_users['resources']:
                guid = org_user['metadata']['guid']
                space_users.append(guid)

            body['manager_guids'] = space_users
            body['developer_guids'] = space_users

        return self.api.post('/v2/spaces', body)

    def get_developers(self):
        return self.api.get('/v2/spaces/%s/developers' % self.guid)

    def get_managers(self):
        return self.api.get('/v2/spaces/%s/managers' % self.guid)

    def delete_space(self, name=None, guid=None):
        """
        Delete the current space, or a space with the given name
        or guid.
        """

        if not guid:
            if name:
                spaces = self._get_spaces()
                for space in spaces['resources']:
                    if space['entity']['name'] == name:
                        guid = space['metadata']['guid']
                        break
                if not guid:
                    raise ValueError("Space with name %s not found." % (name))
            else:
                guid = self.guid

        logging.warn("Deleting space (%s) and all services." % (guid))

        return self.api.delete("/v2/spaces/%s" % (guid), params={'recursive':
        'true'})

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

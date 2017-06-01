
import logging

import predix.admin.cf.api
import predix.admin.cf.spaces


class Service(object):
    """
    Operations and data for working with Cloud Foundry services.
    """
    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()
        self.space = predix.admin.cf.spaces.Space()

    def get_services(self):
        """
        Get the marketplace services.
        """
        return self.api.get('/v2/services')

    def get_instance_guid(self, service_name):
        """
        Returns the GUID for the service instance with
        the given name.
        """
        summary = self.space.get_space_summary()
        for service in summary['services']:
            if service['name'] == service_name:
                return service['guid']

        raise ValueError("No service with name '%s' found." % (service_name))

    def _get_service_bindings(self, service_name):
        """
        Return the service bindings for the service instance.
        """
        instance = self.get_instance(service_name)
        return self.api.get(instance['service_bindings_url'])

    def delete_service_bindings(self, service_name):
        """
        Remove service bindings to applications.
        """
        instance = self.get_instance(service_name)
        return self.api.delete(instance['service_bindings_url'])

    def _get_service_keys(self, service_name):
        """
        Return the service keys for the given service.
        """
        guid = self.get_instance_guid(service_name)
        uri = "/v2/service_instances/%s/service_keys" % (guid)
        return self.api.get(uri)

    def get_service_keys(self, service_name):
        """
        Returns a flat list of the names of the service keys
        for the given service.
        """
        keys = []
        for key in self._get_service_keys(service_name)['resources']:
            keys.append(key['entity']['name'])

        return keys

    def has_key(self, service_name, key_name):
        """
        Tests if the given service has a key of the given name.
        """
        return key_name in self.get_service_keys(service_name)

    def get_service_key(self, service_name, key_name):
        """
        Returns the service key details.

        Similar to `cf service-key`.
        """
        for key in self._get_service_keys(service_name)['resources']:
            if key_name == key['entity']['name']:
                guid = key['metadata']['guid']

                uri = "/v2/service_keys/%s" % (guid)
                return self.api.get(uri)

        return None

    def create_service_key(self, service_name, key_name):
        """
        Create a service key for the given service.
        """
        if self.has_key(service_name, key_name):
            logging.warn("Reusing existing service key %s" % (key_name))
            return self.get_service_key(service_name, key_name)

        body = {
            'service_instance_guid': self.get_instance_guid(service_name),
            'name': key_name
            }

        return self.api.post('/v2/service_keys', body)

    def delete_service_key(self, service_name, key_name):
        """
        Delete a service key for the given service.
        """
        key = self.get_service_key(service_name, key_name)
        logging.info("Deleting service key %s for service %s" % (key, service_name))
        return self.api.delete(key['metadata']['url'])

    def get_instance(self, service_name):
        """
        Retrieves a service instance with the given name.
        """
        for resource in self.space._get_instances()['resources']:
            if resource['entity']['name'] == service_name:
                return resource['entity']

    def get_service_plans(self):
        """
        Get the available service plans.
        """
        return self.api.get('/v2/service_plans')

    def get_service_plan_for_service(self, service_name):
        """
        Return the service plans available for a given service.
        """
        services = self.get_services()
        for service in services['resources']:
            if service['entity']['label'] == service_name:
                response = self.api.get(service['entity']['service_plans_url'])
                return response['resources']

    def get_service_plan_guid(self, service_name, plan_name):
        """
        Return the service plan GUID for the given service / plan.
        """
        for plan in self.get_service_plan_for_service(service_name):
            if plan['entity']['name'] == plan_name:
                return plan['metadata']['guid']

        return None

    def create_service(self, service_type, plan_name, service_name, params):
        """
        Create a service instance.
        """
        if self.space.has_service_with_name(service_name):
            logging.warn("Service already exists with that name.")
            return self.get_instance(service_name)

        if self.space.has_service_of_type(service_type):
            logging.warn("Service type already exists.")

        guid = self.get_service_plan_guid(service_type, plan_name)
        if not guid:
            raise ValueError("No service plan named: %s" % (plan_name))

        body = {
            'name': service_name,
            'space_guid': self.space.guid,
            'service_plan_guid': guid,
            'parameters': params
            }

        return self.api.post('/v2/service_instances?accepts_incomplete=false',
                body)

    def delete_service(self, service_name, params=None):
        """
        Delete the service of the given name.  It may fail if there are
        any service keys or app bindings.  Use obliterate() if you want
        to delete it all.
        """
        if not self.space.has_service_with_name(service_name):
            logging.warn("Service not found so... succeeded?")
            return True

        guid = self.get_instance_guid(service_name)
        logging.info("Deleting service %s with guid %s" % (service_name, guid))

        # MAINT: this endpoint changes in newer version of api
        return self.api.delete("/v2/service_instances/%s?accepts_incomplete=true" %
            (guid), params=params)

    def purge(self, service_name):
        """
        Remove the service and anything that prevents from its removal such
        as service keys and app bindings.
        """
        return self.delete_service(service_name, params={'recursive': 'true'})

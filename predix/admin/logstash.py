
import os

import predix.config
import predix.admin.service
import predix.admin.cf.spaces

class Logging(object):
    """
    An Elasticsearch ELK distribution to centralize Cloud Foundry log
    aggregation and analysis.

    You need to install the Kibana-Me-Logs application separately to
    make use of the logging service.
    https://docs.predix.io/en-US/content/service/operations/logging/
    """
    def __init__(self, plan_name=None, name=None, *args, **kwargs):
        super(Logging, self).__init__(*args, **kwargs)

        # Service name differs depending on org/space configuration
        self.service_name = self._find_service_name()
        self.plan_name = plan_name or 'free'

        self.service = predix.admin.service.CloudFoundryService(self.service_name, 
                self.plan_name, name=name)

    def _find_service_name(self):
        """
        For cloud operations there is support for multiple pools of resources
        dedicated to logstash.  The service name as a result follows the
        pattern logstash-{n} where n is some number.  We can find it from the
        service marketplace.
        """
        space = predix.admin.cf.spaces.Space()
        services = space.get_services()
        for service in services:
            if service.startswith('logstash'):
                return service

        return 'logstash-3'

    def exists(self):
        """
        Returns whether or not this service already exists.
        """
        return self.service.exists()

    def create(self):
        """
        Creates an instance of the logstash pipeline.
        """
        self.service.create(create_keys=False)

    def add_to_manifest(self, manifest):
        """
        Add to the manifest to make sure it is bound to the
        application.
        """
        manifest.add_service(self.service.name)
        manifest.write_manifest()

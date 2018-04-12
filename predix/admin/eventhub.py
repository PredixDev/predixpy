import os

import predix.config
import predix.security.uaa
import predix.admin.service
import predix.data.eventhub.client


class EventHub(object):
    """
   Event Hub is a publisher/subscriber framework for getting information in, out and around the predix cloud
    """

    def __init__(self, plan_name=None, name=None, uaa=None, *args, **kwargs):
        self.service_name = 'predix-event-hub'
        self.plan_name = plan_name or 'Tiered'
        self.use_class = predix.data.eventhub.client.Eventhub

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

        os.environ[predix.config.get_env_key(self.use_class, 'host')] = self.get_eventhub_host()
        os.environ[predix.config.get_env_key(self.use_class, 'port')] = self.get_eventhub_grpc_port()
        os.environ[predix.config.get_env_key(self.use_class, 'wss_publish_uri')] = self.get_publish_wss_uri()
        os.environ[predix.config.get_env_key(self.use_class, 'zone_id')] = self.get_zone_id()

    def grant_client(self, client_id, publish=False, subscribe=False, publish_protocol=None, publish_topics=None,
                     subscribe_topics=None, scope_prefix='predix-event-hub', **kwargs):
        """
        Grant the given client id all the scopes and authorities
        needed to work with the eventhub service.
        """
        scopes = ['openid']
        authorities = ['uaa.resource']

        zone_id = self.get_zone_id()
        # always must be part of base user scope
        scopes.append('%s.zones.%s.user' % (scope_prefix, zone_id))
        authorities.append('%s.zones.%s.user' % (scope_prefix, zone_id))

        if publish_topics is not None or subscribe_topics is not None:
            raise Exception("multiple topics are not currently available in preidx-py")

        if publish_topics is None:
            publish_topics = ['topic']

        if subscribe_topics is None:
            subscribe_topics = ['topic']

        if publish:
            # we are granting just the default topic
            if publish_protocol is None:
                scopes.append('%s.zones.%s.grpc.publish' % (scope_prefix, zone_id))
                authorities.append('%s.zones.%s.grpc.publish' % (scope_prefix, zone_id))
                scopes.append('%s.zones.%s.wss.publish' % (scope_prefix, zone_id))
                authorities.append('%s.zones.%s.wss.publish' % (scope_prefix, zone_id))

            else:
                scopes.append('%s.zones.%s.%s.publish' % (scope_prefix, zone_id, publish_protocol))
                authorities.append('%s.zones.%s.%s.publish' % (scope_prefix, zone_id, publish_protocol))

            # we are requesting multiple topics
            for topic in publish_topics:
                if publish_protocol is None:
                    scopes.append('%s.zones.%s.%s.grpc.publish' % (scope_prefix, zone_id, topic))
                    scopes.append('%s.zones.%s.%s.wss.publish' % (scope_prefix, zone_id, topic))
                    scopes.append('%s.zones.%s.%s.user' % (scope_prefix, zone_id, topic))
                    authorities.append('%s.zones.%s.%s.grpc.publish' % (scope_prefix, zone_id, topic))
                    authorities.append('%s.zones.%s.%s.wss.publish' % (scope_prefix, zone_id, topic))
                    authorities.append('%s.zones.%s.%s.user' % (scope_prefix, zone_id, topic))
                else:
                    scopes.append('%s.zones.%s.%s.%s.publish' % (scope_prefix, zone_id, topic, publish_protocol))
                    authorities.append('%s.zones.%s.%s.%s.publish' % (scope_prefix, zone_id, topic, publish_protocol))
        if subscribe:
            # we are granting just the default topic
            scopes.append('%s.zones.%s.grpc.subscribe' % (scope_prefix, zone_id))
            authorities.append('%s.zones.%s.grpc.subscribe' % (scope_prefix, zone_id))

            # we are requesting multiple topics
            for topic in subscribe_topics:
                scopes.append('%s.zones.%s.%s.grpc.subscribe' % (scope_prefix, zone_id, topic))
                authorities.append('%s.zones.%s.%s.grpc.subscribe' % (scope_prefix, zone_id, topic))

        self.service.uaa.uaac.update_client_grants(client_id, scope=scopes,
                                                   authorities=authorities)

        return self.service.uaa.uaac.get_client(client_id)

    def get_eventhub_host(self):
        """
        returns the publish grpc endpoint for ingestion.
        """
        for protocol in self.service.settings.data['publish']['protocol_details']:
            if protocol['protocol'] == 'grpc':
                return protocol['uri'][0:protocol['uri'].index(':')]

    def get_eventhub_grpc_port(self):
        for protocol in self.service.settings.data['publish']['protocol_details']:
            if protocol['protocol'] == 'grpc':
                return str(protocol['uri'][(protocol['uri'].index(':') + 1):])

    def get_publish_wss_uri(self):
        """
        returns the publish grpc endpoint for ingestion.

        """
        for protocol in self.service.settings.data['publish']['protocol_details']:
            if protocol['protocol'] == 'wss':
                return protocol['uri']

    def get_zone_id(self):
        return self.service.settings.data['publish']['zone-http-header-value']

    def get_subscribe_uri(self):
        return self.service.settings.data['subscribe']['protocol_details'][0]['uri']

    def make_topic(self, broker_uri, topic_name):
        raise Exception('make topic has not been implemented yet')

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
        manifest.add_env_var(predix.config.get_env_key(self.use_class, 'host'), self.get_eventhub_host())
        manifest.add_env_var(predix.config.get_env_key(self.use_class, 'port'), self.get_eventhub_grpc_port())
        manifest.add_env_var(predix.config.get_env_key(self.use_class, 'wss_publish_uri'), self.get_publish_wss_uri())
        manifest.add_env_var(predix.config.get_env_key(self.use_class, 'zone_id'), self.get_zone_id())

        manifest.write_manifest()

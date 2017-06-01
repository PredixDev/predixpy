
import os
import uuid
import urllib
import logging

import predix.service


class AccessControl(object):
    """
    Use the Access Control service to provide a more powerful authorization
    framework than basic User Account and Authorization (UAA) service.

    Access Control service provides app-specific policies without adding
    overhead to a UAA server that may become the entry point for several apps
    over time.
    """
    def __init__(self):

        self.zone_id = os.environ.get('PREDIX_ACS_ZONE_ID')
        if not self.zone_id:
            raise ValueError('PREDIX_ACS_ZONE_ID environment unset')

        self.uri = os.environ.get('PREDIX_ACS_URI')
        if not self.uri:
            raise ValueError('PREDIX_ACS_URI environment unset')

        self.service = predix.service.Service(self.zone_id)

    def authenticate_as_client(self, client_id, client_secret):
        """
        Will authenticate for the given client / secret.
        """
        self.service.uaa.authenticate(client_id, client_secret)

    def _get_resource_uri(self, guid=None):
        """
        Returns the full path that uniquely identifies
        the resource endpoint.
        """
        uri = self.uri + '/v1/resource'
        if guid:
            uri += '/' + urllib.quote_plus(guid)
        return uri

    def get_resources(self):
        """
        Return all of the resources in the ACS service.
        """
        uri = self._get_resource_uri()
        return self.service._get(uri)

    def get_resource(self, resource_id):
        """
        Returns a specific resource by resource id.
        """
        # resource_id could be a path such as '/asset/123' so quote
        uri = self._get_resource_uri(guid=resource_id)
        return self.service._get(uri)

    def _post_resource(self, body):
        """
        Create new resources and associated attributes.

        Example:

            acs.post_resource([
                {
                    "resourceIdentifier": "masaya",
                    "parents": [],
                    "attributes": [
                        {
                            "issuer": "default",
                            "name": "country",
                            "value": "Nicaragua"
                            }
                        ],
                }
            ])

        The issuer is effectively a namespace, and in policy evaluations you
        identify an attribute by a specific namespace.  Many examples provide
        a URL but it could be any arbitrary string.

        The body is a list, so many resources can be added at the same time.
        """
        assert isinstance(body, (list)), "POST for requires body to be a list"
        uri = self._get_resource_uri()
        return self.service._post(uri, body)

    def delete_resource(self, resource_id):
        """
        Remove a specific resource by its identifier.
        """
        # resource_id could be a path such as '/asset/123' so quote
        uri = self._get_resource_uri(guid=resource_id)
        return self.service._delete(uri)

    def _put_resource(self, resource_id, body):
        """
        Update a resource for the given resource id.  The body is not
        a list but a dictionary of a single resource.
        """
        assert isinstance(body, (dict)), "PUT requires body to be a dict."
        # resource_id could be a path such as '/asset/123' so quote
        uri = self._get_resource_uri(guid=resource_id)
        return self.service._put(uri, body)

    def add_resource(self, resource_id, attributes, parents=[],
            issuer='default'):
        """
        Will add the given resource with a given identifier and attribute
        dictionary.

            example/

                add_resource('/asset/12', {'id': 12, 'manufacturer': 'GE'})
        """
        # MAINT: consider test to avoid adding duplicate resource id
        assert isinstance(attributes, (dict)), "attributes expected to be dict"

        attrs = []
        for key in attributes.keys():
            attrs.append({
                'issuer': issuer,
                'name': key,
                'value': attributes[key]
                })

        body = {
            "resourceIdentifier": resource_id,
            "parents": parents,
            "attributes": attrs,
        }

        return self._put_resource(resource_id, body)

    def _get_subject_uri(self, guid=None):
        """
        Returns the full path that uniquely identifies
        the subject endpoint.
        """
        uri = self.uri + '/v1/subject'
        if guid:
            uri += '/' + urllib.quote_plus(guid)
        return uri

    def get_subjects(self):
        """
        Return all of the subjects in the ACS service.
        """
        uri = self._get_subject_uri()
        return self.service._get(uri)

    def get_subject(self, subject_id):
        """
        Returns a specific subject by subject id.
        """
        # subject_id could be a path such as '/user/j12y' so quote
        uri = self._get_subject_uri(guid=subject_id)
        return self.service._get(uri)

    def _post_subject(self, body):
        """
        Create new subjects and associated attributes.

        Example:

            acs.post_subject([
                {
                    "subjectIdentifier": "/role/evangelist",
                    "parents": [],
                    "attributes": [
                        {
                            "issuer": "default",
                            "name": "role",
                            "value": "developer evangelist",
                        }
                    ]
                }
            ])

        The issuer is effectively a namespace, and in policy evaluations
        you identify an attribute by a specific namespace.  Many examples
        provide a URL but it could be any arbitrary string.

        The body is a list, so many subjects can be added at the same time.
        """
        assert isinstance(body, (list)), "POST requires body to be a list"

        uri = self._get_subject_uri()
        return self.service._post(uri, body)

    def delete_subject(self, subject_id):
        """
        Remove a specific subject by its identifier.
        """
        # subject_id could be a path such as '/role/analyst' so quote
        uri = self._get_subject_uri(guid=subject_id)
        return self.service._delete(uri)

    def _put_subject(self, subject_id, body):
        """
        Update a subject for the given subject id.  The body is not
        a list but a dictionary of a single resource.
        """
        assert isinstance(body, (dict)), "PUT requires body to be dict."

        # subject_id could be a path such as '/asset/123' so quote
        uri = self._get_subject_uri(guid=subject_id)
        return self.service._put(uri, body)

    def add_subject(self, subject_id, attributes, parents=[],
            issuer='default'):
        """
        Will add the given subject with a given identifier and attribute
        dictionary.

            example/

                add_subject('/user/j12y', {'username': 'j12y'})
        """
        # MAINT: consider test to avoid adding duplicate subject id
        assert isinstance(attributes, (dict)), "attributes expected to be dict"

        attrs = []
        for key in attributes.keys():
            attrs.append({
                'issuer': issuer,
                'name': key,
                'value': attributes[key]
                })

        body = {
            "subjectIdentifier": subject_id,
            "parents": parents,
            "attributes": attrs,
        }

        return self._put_subject(subject_id, body)

    def _get_monitoring_heartbeat(self):
        """
        Tests whether or not the ACS service being monitored is alive.
        """
        target = self.uri + '/monitoring/heartbeat'
        response = self.session.get(target)
        return response

    def is_alive(self):
        """
        Will test whether the ACS service is up and alive.
        """
        response = self.get_monitoring_heartbeat()
        if response.status_code == 200 and response.content == 'alive':
            return True

        return False

    def _get_policy_set_uri(self, guid=None):
        """
        Returns the full path that uniquely identifies
        the subject endpoint.
        """
        uri = self.uri + '/v1/policy-set'
        if guid:
            uri += '/' + urllib.quote_plus(guid)
        return uri

    def get_policy_sets(self):
        """
        Return all of the policy sets in the ACS service.
        """
        uri = self._get_policy_set_uri()
        return self.service._get(uri)

    def _put_policy_set(self, policy_set_id, body):
        """
        Will create or update a policy set for the given path.
        """
        assert isinstance(body, (dict)), "PUT requires body to be a dict."
        uri = self._get_policy_set_uri(guid=policy_set_id)
        return self.service._put(uri, body)

    def _get_policy_set(self, policy_set_id):
        """
        Get a specific policy set by id.
        """
        uri = self._get_policy_set_uri(guid=policy_set_id)
        return self.service._get(uri)

    def delete_policy_set(self, policy_set_id):
        """
        Delete a specific policy set by id.  Method is idempotent.
        """
        uri = self._get_policy_set_uri(guid=policy_set_id)
        return self.service._delete(uri)

    def add_policy(self, name, action, resource, subject, condition,
            policy_set_id=None, effect='PERMIT'):
        """
        Will create a new policy set to enforce the given policy details.

        The name is just a helpful descriptor for the policy.

        The action maps to a HTTP verb.

        Policies are evaluated against resources and subjects.  They are
        identified by matching a uriTemplate or attributes.

        Examples:

            resource = {
                "uriTemplate": "/asset/{id}"
                }

            subject: {
                "attributes": [{
                    "issuer": "default",
                    "name": "role"
                    }]
                }

        The condition is expected to be a string that defines a groovy
        operation that can be evaluated.

        Examples:

            condition = "match.single(subject.attributes('default', 'role'),
                'admin')

        """
        # If not given a policy set id will generate one
        if not policy_set_id:
            policy_set_id = str(uuid.uuid4())

        # Only a few operations / actions are supported in policy definitions
        if action not in ['GET', 'PUT', 'POST', 'DELETE']:
            raise ValueError("Invalid action")

        # Defines a single policy to be part of the policy set.
        policy = {
            "name": name,
            "target": {
                "resource": resource,
                "subject": subject,
                "action": action,
                },
            "conditions": [{
                "name": "",
                "condition": condition,
                }],
            "effect": effect,
        }

        # Body of the request is a list of policies
        body = {
            "name": policy_set_id,
            "policies": [policy],
        }

        result = self._put_policy_set(policy_set_id, body)
        return result

    def is_allowed(self, subject_id, action, resource_id, policy_sets=[]):
        """
        Evaluate a policy-set against a subject and resource.

        example/

            is_allowed('/user/j12y', 'GET', '/asset/12')

        """
        body = {
            "action": action,
            "subjectIdentifier": subject_id,
            "resourceIdentifier": resource_id,
        }

        if policy_sets:
            body['policySetsEvaluationOrder'] = policy_sets

        # Will return a 200 with decision
        uri = self.uri + '/v1/policy-evaluation'

        logging.debug("URI=" + str(uri))
        logging.debug("BODY=" + str(body))

        response = self.service._post(uri, body)

        if 'effect' in response:
            if response['effect'] in ['NOT_APPLICABLE', 'PERMIT']:
                return True

        return False

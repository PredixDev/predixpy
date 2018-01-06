
import os
import boto3
import logging

import predix.service
import predix.config


class BlobStore(object):
    """
    The BlobStore is the place to store Binary Large Objects, ie. files that
    could be images, csv files, cad files, pdf files, etc.

    .. important::

       This service will only work from the Predix Cloud -- Firewall will block
       any traffic not originating from within the Predix environment.

    Underlying BlobStore is the AWS S3 service so you will need to be familiar
    with the boto3 library from AWS to learn how to work with buckets.  A few
    methods are provided for common patterns you can use for reference.

    :param host: Host address for blob store.


    """
    def __init__(self, host=None, access_key_id=None, secret_access_key=None,
            bucket_name=None, *args, **kwargs):
        super(BlobStore, self).__init__(*args, **kwargs)

        if not predix.config.is_cf_env():
            raise predix.config.PredixCloudRequiredError()

        self.host = host or self._get_host()
        self.access_key_id = access_key_id or self._get_access_key_id()
        self.secret_access_key = secret_access_key or self._get_secret_access_key()
        self.bucket_name = bucket_name or self._get_bucket_name()

        self.session = boto3.session.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key)

        config = boto3.session.Config(signature_version='s3', s3={
                'addressing_style': 'virtual'})
        self.client = self.session.client('s3', endpoint_url=self.host,
                config=config)

    def _get_host(self):
        """
        Returns the host address for an instance of Blob Store service from
        environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            host = services['predix-blobstore'][0]['credentials']['host']
        else:
            host = predix.config.get_env_value(self, 'host')

        # Protocol may not always be included in host setting
        if 'https://' not in host:
            host = 'https://' + host

        return host

    def _get_access_key_id(self):
        """
        Returns the access key for an instance of Blob Store service from
        environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            return services['predix-blobstore'][0]['credentials']['access_key_id']
        else:
            return predix.config.get_env_value(self, 'access_key_id')

    def _get_secret_access_key(self):
        """
        Returns the secret access key for an instance of Blob Store service from
        environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            return services['predix-blobstore'][0]['credentials']['secret_access_key']
        else:
            return predix.config.get_env_value(self, 'secret_access_key')

    def _get_bucket_name(self):
        """
        Returns the bucket name for an instance of Blob Store service from
        environment inspection.
        """
        if 'VCAP_SERVICES' in os.environ:
            services = json.loads(os.getenv('VCAP_SERVICES'))
            return services['predix-blobstore'][0]['credentials']['bucket_name']
        else:
            return predix.config.get_env_value(self, 'bucket_name')

    def list_buckets(self, *args, **kwargs):
        """
        This method is primarily for illustration and just calls the boto3
        client implementation of list_buckets directly but is a common task for
        first time Predix BlobStore users.
        """
        return self.client.list_buckets(**kwargs)

    def list_objects(self, bucket_name=None, **kwargs):
        """
        This method is primarily for illustration and just calls the 
        boto3 client implementation of list_objects but is a common task
        for first time Predix BlobStore users.
        """
        if not bucket_name: bucket_name = self.bucket_name
        return self.client.list_objects(Bucket=bucket_name, **kwargs)

    def upload_file(self, src_filepath, dest_filename=None, bucket_name=None,
            **kwargs):
        """
        This method is primarily for illustration and just calls the 
        boto3 client implementation of upload_file but is a common task
        for first time Predix BlobStore users.
        """
        if not bucket_name: bucket_name = self.bucket_name
        if not dest_filename: dest_filename = src_filepath
        return self.client.upload_file(src_filepath, bucket_name,
                dest_filename, **kwargs)

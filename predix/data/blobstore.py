
import os
import boto3
import logging

import predix.service
import predix.config


class BlobStore(object):
    """
    **********
    IMPORTANT: This service will only work from the Predix Cloud -- Firewall
    will block any traffic not originating from within the Predix environment.
    **********

    The BlobStore is the place to store Binary Large Objects, ie. files that
    could be images, csv files, cad files, pdf files, etc.

    Underlying BlobStore is the AWS S3 service so you will need to be familiar
    with the boto3 library from AWS to learn how to work with buckets.  A few
    methods are provided for common patterns you can use for reference.
    """
    def __init__(self):

        instance = os.environ.get('CF_INSTANCE_ADDR')
        if not instance:
            raise ValueError("This service can only be used in the Predix Cloud Foundry environment.")

        host = predix.config.get_env_key(self, 'host')
        self.host = os.environ.get(host)
        if not self.host:
            raise ValueError("%s environment unset" % host)

        # Protocol may not be specified in host path
        if 'https://' not in self.host:
            self.host = 'https://' + self.host

        access_key_id = predix.config.get_env_key(self, 'access_key_id')
        self.access_key_id = os.environ.get(access_key_id)
        if not self.access_key_id:
            raise ValueError("%s environment unset" % access_key_id)

        secret_access_key = predix.config.get_env_key(self,
                'secret_access_key')
        self.secret_access_key = os.environ.get(secret_access_key)
        if not self.secret_access_key:
            raise ValueError("%s environment unset" % secret_access_key)

        bucket_name = predix.config.get_env_key(self, 'bucket_name')
        self.bucket_name = os.environ.get(bucket_name)
        if not self.bucket_name:
            raise ValueError("%s environment unset" % bucket_name)

        self.session = boto3.session.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key)
        config = boto3.session.Config(signature_version='s3', s3={
                'addressing_style': 'virtual'})
        self.client = self.session.client('s3', endpoint_url=self.host,
                config=config)

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

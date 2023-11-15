import os
import concurrent.futures
from concurrent.futures import wait

from minio import Minio
from minio.commonconfig import ENABLED, Filter, ComposeSource
from minio.deleteobjects import DeleteObject
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration


class Uploader:

    def __init__(self, config):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=config['max_workers'])
        self.treads = {}
        self.wait_timeout = config['wait_timeout']
        s3 = config['s3']
        secret = os.getenv('SECRET_KEY')
        self.bucket_name = s3['bucket']
        self.minioClient = Minio(s3['server'],
                                 access_key=s3['access_key'],
                                 secret_key=secret,
                                 region=s3['region'],
                                 secure=s3['secure'])

        self.make_bucket(self.bucket_name)

    def remove_bucket(self, bucket):
        objects = self.minioClient.list_objects(bucket, "chunk")
        rem_list = [DeleteObject(x.object_name) for x in objects]
        errors = self.minioClient.remove_objects(bucket, rem_list)
        for error in errors:
            print("error occurred when deleting object", error)

        self.minioClient.remove_bucket(bucket)

    def set_lifecycle(self, bucket):
        config = LifecycleConfig(
            [
                Rule(
                    ENABLED,
                    rule_filter=Filter(prefix="chunk"),
                    rule_id="ExpirationRule",
                    expiration=Expiration(days=1),
                ),
            ],
        )
        self.minioClient.set_bucket_lifecycle(bucket, config)

    def make_bucket(self, name):
        if self.minioClient.bucket_exists(name):
            return
        try:
            self.minioClient.make_bucket(name)
        except Exception as err:
            print(err)

    def submit(self, bucket, file_name, path):
        self.make_bucket(bucket)
        self.set_lifecycle(bucket)
        try:
            self.minioClient.fput_object(bucket, file_name, path)
        except Exception as err:
            print(err)
        os.remove(path)

    def save(self, path, bucket, last, origin_file_name, file_name):
        ft = self.executor.submit(self.submit, bucket, file_name, path)
        if bucket not in self.treads:
            self.treads[bucket] = []
        self.treads[bucket].append(ft)

        if last == 'true':
            wait(self.treads.pop(bucket), self.wait_timeout)
            self.combine(bucket, origin_file_name)
            self.remove_bucket(bucket)

    def combine(self, bucket, file_name):
        objects = self.minioClient.list_objects(bucket, "chunk")
        sources = [ComposeSource(bucket, obj.object_name) for obj in objects]
        result = self.minioClient.compose_object(self.bucket_name, file_name, sources)
        print(f"{result.object_name =}")

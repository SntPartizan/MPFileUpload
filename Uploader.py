import os
from minio import Minio
from minio.commonconfig import ENABLED, Filter, ComposeSource
from minio.deleteobjects import DeleteObject
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration


class Uploader:

    def __init__(self):
        secret = os.getenv('SECRET_KEY')
        self.bucket_name = 'uploaded'
        self.minioClient = Minio('127.0.0.1:9000',
                                 access_key='6VCT5WneTj6RmVEv5z31',
                                 secret_key=secret,
                                 region="test",
                                 secure=False)

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

    def save(self, path, bucket, last, origin_file_name, file_name):

        self.make_bucket(bucket)
        self.set_lifecycle(bucket)
        try:
            self.minioClient.fput_object(bucket, file_name, path)
        except Exception as err:
            print(err)
        os.remove(path)

        if last == 'true':
            self.combine(bucket, origin_file_name)
            self.remove_bucket(bucket)

    def combine(self, bucket, file_name):
        objects = self.minioClient.list_objects(bucket, "chunk")
        sources = [ComposeSource(bucket, obj.object_name) for obj in objects]
        result = self.minioClient.compose_object(self.bucket_name, file_name, sources)
        print(f"{result.object_name =}")

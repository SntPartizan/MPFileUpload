from bottle import route, run, template, post, request
import os
import hashlib
from minio import Minio
from dotenv import load_dotenv
import datetime
from minio.commonconfig import ComposeSource, ENABLED, Filter
from minio.deleteobjects import DeleteObject
from minio.lifecycleconfig import Expiration, Rule, LifecycleConfig

load_dotenv()

secret = os.getenv('SECRET_KEY')

bucket_name = "uploaded"

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio('127.0.0.1:9000',
                    access_key='6VCT5WneTj6RmVEv5z31',
                    secret_key=secret,
                    region="test",
                    secure=False)

proj_dir = os.path.dirname(os.path.abspath(__file__))


def computeMD5hash(to_hash_str):
    m = hashlib.md5()
    m.update(to_hash_str.encode("utf-8"))
    return m.hexdigest()


@route('/')
def index():
    ip = request.remote_addr
    upload_id = "{}{}{}".format(datetime.datetime.now(), ip, request.headers.get('User-Agent'))
    upload_id = computeMD5hash(upload_id)

    return template('index.html', uid=upload_id)


@post("/")
def post():
    file = request.files.get("fileToUpload")
    if file is None:
        return "no file"

    uid = request.params.get('uid')
    last = request.params.get('last')

    origin_file_name = request.params.get('origin')

    upl_dir = os.path.join(proj_dir, "uploads")

    path = os.path.join(upl_dir, f"{uid}_{file.filename}")
    file.save(path, overwrite=True)

    print(uid)
    save(path, uid, file.filename)
    if last == 'true':
        objects = list(minioClient.list_objects(uid, "chunk"))
        combine(uid, objects, origin_file_name)
        remove_bucket(uid, objects)

    return file.filename


def remove_bucket(bucket, objects):
    rem_list = [DeleteObject(x.object_name) for x in objects]
    errors = minioClient.remove_objects(bucket, rem_list)
    for error in errors:
        print("error occurred when deleting object", error)

    minioClient.remove_bucket(bucket)


def make_bucket(name):
    if minioClient.bucket_exists(name):
        return
    try:
        minioClient.make_bucket(name)
    except Exception as err:
        print(err)

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
    minioClient.set_bucket_lifecycle(name, config)


def save(path, bucket, file_name):
    make_bucket(bucket)
    try:
        minioClient.fput_object(bucket, file_name, path)
    except Exception as err:
        print(err)
    os.remove(path)


def combine(bucket, objects, file_name):
    sources = [ComposeSource(bucket, obj.object_name) for obj in objects]
    result = minioClient.compose_object(bucket_name, file_name, sources)
    print(f"{result.object_name =}")


def main():
    if not minioClient.bucket_exists(bucket_name):
        try:
            minioClient.make_bucket(bucket_name)
        except Exception as err:
            print(err)
    run(host='localhost', port=8080)
    # run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()

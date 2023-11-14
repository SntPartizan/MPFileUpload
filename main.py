from bottle import route, run, template, post, request
import os
import hashlib
from minio import Minio
from dotenv import load_dotenv
import datetime
from minio.commonconfig import ComposeSource

load_dotenv()

secret = os.getenv('SECRET_KEY')

bucket_name = "chunks"

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

    upl_dir = os.path.join(proj_dir, "uploads")

    path = os.path.join(upl_dir, file.filename)
    file.save(upl_dir, overwrite=True)

    if last:
        pass

    print(uid)
    save(path, file_name=file.filename, metadata={'uid': uid})

    return file.filename


def save(path, file_name="test", metadata=None):
    try:
        minioClient.fput_object(bucket_name, f"{metadata['uid']}_{file_name}", path, metadata=metadata)
    except Exception as err:
        print(err)


if __name__ == "__main__":

    if not minioClient.bucket_exists(bucket_name):
        try:
            minioClient.make_bucket(bucket_name)
        except Exception as err:
            print(err)

    # l=minioClient.list_objects(bucket_name,"430fff6fa",recursive=True,include_user_meta=True)
    #
    # sources = [
    #     ComposeSource(bucket_name, '430fff6fabf858740b589007a6e30e07_chunk_0'),
    #     ComposeSource(bucket_name, '430fff6fabf858740b589007a6e30e07_chunk_1'),
    #     ComposeSource(bucket_name, '430fff6fabf858740b589007a6e30e07_chunk_2'),
    # ]
    #
    # # Create my-bucket/my-object by combining source object
    # result = minioClient.compose_object(bucket_name, "my-object", sources)
    # print(result.object_name, result.version_id)

    run(host='localhost', port=8080)

from bottle import route, run, template, post, request
import os
import hashlib
from dotenv import load_dotenv
import datetime

from Uploader import Uploader

load_dotenv()

uploader = Uploader()





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
    uploader.save(path, uid, file.filename)
    if last == 'true':
        objects = list(uploader.minioClient.list_objects(uid, "chunk"))
        uploader.combine(uid, objects, origin_file_name)
        uploader.remove_bucket(uid, objects)

    return file.filename












def main():

    run(host='localhost', port=8080)
    # run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()

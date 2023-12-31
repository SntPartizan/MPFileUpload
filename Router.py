import datetime
import hashlib
import os

import bottle
from bottle import run, template, request


def compute_hash(to_hash_str):
    m = hashlib.md5()
    m.update(to_hash_str.encode("utf-8"))
    return m.hexdigest()


class Router:

    def __init__(self, uploader, upload_to, config):
        cf = config['router']
        self.host = cf['host']
        self.port = cf['port']
        self.chunk_size = cf['chunk_size'] * 1024 * 1024
        self.uploader = uploader
        self.upload_to = upload_to
        bottle.route('/', 'GET', self.index)
        bottle.route('/upload', 'POST', self.upload)

        pass

    def index(self):
        ip = request.remote_addr
        upload_id = "{}{}{}".format(datetime.datetime.now(), ip, request.headers.get('User-Agent'))
        upload_id = compute_hash(upload_id)

        return template('index.html', uid=upload_id, chunk_size=self.chunk_size)

    def upload(self):
        file = request.files.get("fileToUpload")
        if file is None:
            return "no file"

        uid = request.params.get('uid')
        params = {
            "bucket": uid,
            "last": request.params.get('last'),
            "origin_file_name": request.params.get('origin'),
            "file_name": file.filename,
        }

        upl_dir = os.path.join(self.upload_to, "uploads")
        if not os.path.exists(upl_dir):
            os.mkdir(upl_dir)

        path = os.path.join(upl_dir, f"{uid}_{file.filename}")
        file.save(path, overwrite=True)
        self.uploader.save(path, **params)

        return file.filename

    def run(self):
        run(host=self.host, port=self.port)

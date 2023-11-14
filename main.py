# This is a sample Python script
from bottle import route, run, template, post, request
import os
from minio import Minio
# from minio.error import  (ResponseError, BucketAlreadyOwnedByYou,
#                          BucketAlreadyExists)

# Initialize minioClient with an endpoint and access/secret keys.
minioClient = Minio('127.0.0.1:9000',
                    access_key='6VCT5WneTj6RmVEv5z31',
                    secret_key='7uCw295YeF3vhnMzT3qqyGtTQovBg9HcYdDFfOEe',
                    region="test",
                    secure=False)


proj_dir = os.path.dirname(os.path.abspath(__file__))

print(proj_dir)

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/')
def index():
    return  template('index.html', name="name")
    return """<form method="post" action="" enctype="multipart/form-data" >
  <div>
    <label for="profile_pic">Choose file to upload</label>
    <input
      type="file"
      id="profile_pic"
      name="profile_pic"
       />
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>"""

@post("/")
def post():
    # r = request
    s = [request.files[x] for x in request.files]
    file = s[0]
    upl_dir = os.path.join(proj_dir , "uploads")

    # file_name = file.name
    path = os.path.join(upl_dir,file.filename)
    file.save(upl_dir, overwrite=True)
    save(path, file_name=file.filename)

    # print(f)
    # print(s[0].name)

    return s[0].name





# Make a bucket with the make_bucket API call.
try:
       minioClient.make_bucket("maylogs", location="test")
except Exception as err:
    print(err)
    pass




def save(path,file_name="test.xml"):
    # Put an object 'pumaserver_debug.log' with contents from 'pumaserver_debug.log'.

    try:
           minioClient.fput_object('maylogs', file_name, path)
    except Exception as err:
           print(err)



run(host='localhost', port=8080)
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


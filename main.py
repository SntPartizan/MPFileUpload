import os

from dotenv import load_dotenv

from Router import Router
from Uploader import Uploader


def main():
    load_dotenv()
    proj_dir = os.path.dirname(os.path.abspath(__file__))
    uploader = Uploader()
    router = Router(uploader=uploader, upload_to=proj_dir)
    router.run(host='localhost', port=8080)


if __name__ == "__main__":
    main()

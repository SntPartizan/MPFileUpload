import os

from dotenv import load_dotenv

from Router import Router
from Uploader import Uploader

import toml


def main():
    load_dotenv()
    app_config = toml.load('config.toml')
    
    proj_dir = os.path.dirname(os.path.abspath(__file__))
    uploader = Uploader(app_config)
    router = Router(uploader=uploader, upload_to=proj_dir, config=app_config)
    router.run()


if __name__ == "__main__":
    main()

import os
import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import argparse
import asyncio
import logging

from configs import *
from tools.file_server import *
from tools.airsim_controller import *
from taskHelper import TaskHelper

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", type=str, default=None)
    parser = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    fh = logging.FileHandler(f"logs/{time.strftime('%Y%m%d%H%M%S')}.log")       
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.propagate = False

    threading.Thread(target=start_file_server, args=(logger,)).start()

    controller = AirSimController(logger, parser.config_file)

    threading.Thread(target=controller.start_server).start()

    task_helper = TaskHelper(logger, parser.config_file)
    await task_helper.run()


if __name__ == "__main__":
    asyncio.run(main())
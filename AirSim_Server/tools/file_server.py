import flask
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import *

def start_file_server(logger:logging.Logger):
    cfg = get_default_config()
    # 使用绝对路径指向项目根目录下的cache/images
    ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), cfg.cache, "images")

    app = flask.Flask(__name__)
    # 禁用Flask默认日志处理器以避免重复输出
    app.logger.handlers = []
    app.logger.propagate = False

    @app.route('/file/<path:filename>', methods=['GET'])
    def get_file(filename):
        logger.info(f"FileServer: Request file: {filename}")
        return flask.send_from_directory(ROOT, filename)

    @app.route('/test', methods=['GET'])
    def test():
        return "test"


    app.run(host='0.0.0.0', port=cfg.server.file_port)


if __name__ == '__main__':
    start_file_server()
#! /usr/bin/env python3

# Hello World web server
# Returns the FQDN of the host it's running on

import os
import sys
import signal
import socket
import logging
import argparse

from functools import partial
from socketserver import TCPServer
from http.server import HTTPServer, BaseHTTPRequestHandler


class Server(TCPServer):

    def server_bind(self):
        """Allow reuse TCP address"""

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, display_text, *args, **kwargs):
        self.display_text = display_text
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Hello from {}\n'.format(self.display_text).encode())

    def log_message(self, message, *args):
        """Send output to logging"""

        logging.info(message % args)

    def log_error(self, message, *args):
        """Send output to logging with level error"""

        logging.error(message % args)


def parse():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('-d', '--display-text', default=os.environ.get('HELLOWEB_DISPLAY_TEXT', socket.getfqdn()), help='Text to return in HTTP response')
    parser.add_argument('-e', '--from-env-var', default=os.environ.get('HELLOWEB_FROM_ENV_VAR'), help='Environment variable to return in HTTP response (overrides --display-text)')
    args = parser.parse_args()

    if args.from_env_var:

        if not args.from_env_var in os.environ:
            parser.error('Variable "{}" not found in environment'.format(args.from_env_var))

        args.display_text = os.environ[args.from_env_var]

    return args


def sigterm_handler(_signo, _stack_frame):
    """Handle SIGTERM in docker containers where PID is 1"""

    sys.exit(0)


def main(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    """main!"""

    # set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Handle SIGTERM in docker containers where PID is 1
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parse()
    server_address = ('', args.port)
    handler = partial(HTTPRequestHandler, args.display_text)
    httpd = Server(server_address, handler)
    logging.info('Listening on {}:{}'.format(*httpd.socket.getsockname()))
    logging.info('HTTP display text: {}'.format(args.display_text))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()


if __name__ == '__main__':
    main()

import argparse

from .app import app
from .version import __version__




def main():
    desc = """
           The Alpha Video & youtube-dl API server.
           """

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        '-p', '--port',
        default=5000,
        type=int,
        help='The port the server will use. The default is: %(default)s',
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        type=str,
        help='The host the server will use. The default is: %(default)s',
    )

    parser.add_argument(
        '--number-processes',
        default=1,
        type=int,
        help=('The number of processes the server will use. The default is: '
              '%(default)s'),
    )

    parser.add_argument('--version', action='store_true',
                        help='Print the version of the server')

    args = parser.parse_args()
    if args.version:
        print(__version__)
        exit(0)

    app.run(args.host, args.port, processes=args.number_processes)

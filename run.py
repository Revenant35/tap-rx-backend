from argparse import ArgumentParser
from src.app import create_app


def create_parser():
    parser = ArgumentParser(
        description="Run the TapRx Backend API"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    parser.add_argument(
        "--use_reloader",
        action="store_true",
        help="Enable the reloader"
    )

    return parser


if __name__ == '__main__':
    parser = create_parser()

    args = parser.parse_args()

    app = create_app()
    app.run(debug=args.debug, use_reloader=args.use_reloader)

import argparse
import os
import pathlib
import sys
from typing import Union

from dotenv import find_dotenv, load_dotenv
from loguru import logger


class Range(argparse.Action):
    """Checks whether a numeric command-line argument satisfies the range bounds.

    Attributes:
        [optional] min (Union[int, float]): The lower bound.
        [optional] max (Union[int, float]): The upper bound.
        *args: Variable length argument list of the argparse parser.
        **kwargs: Arbitrary keyword arguments of the argparse parser.
    """

    def __init__(
        self,
        minimum: Union[int, float] = 0,
        maximum: Union[int, float] = 9000,
        *args,
        **kwargs,
    ):
        self.min = minimum
        self.max = maximum

        kwargs["metavar"] = f"[{self.min}-{self.max}]"
        super(Range, self).__init__(*args, **kwargs)

    def __call__(  # type: ignore
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        value: Union[int, float],
        arg: str,
    ) -> None:
        if not (self.min <= value <= self.max):
            raise argparse.ArgumentTypeError(
                f"Argument '{self.option_strings[0]}' must be between {self.min} and {self.max}"
            )

        setattr(namespace, self.dest, value)


DIR = pathlib.Path(__file__).parent.parent
LOG_COLOR = True
LOG_FILE_DEFAULT = f"{DIR}/log/bot.log"
LOG_ROTATION_SIZE = "256 KB"
LOG_COMPRESSION_FORMAT = "zip"
FIELDS = [
    "id",
    "product",
    "model",
    "price",
    "amount",
    "weight",
    "first_name",
    "last_name",
    "address",
    "telegram_id",
    "timezone",
    "locale",
]

parser = argparse.ArgumentParser(
    "SAP CoIL Telegram Bot for basic SQLAnywhere database management",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--dev",
    action="store_true",
    dest="dev",
    help="run in the development mode using a test bot's token",
)
parser.add_argument(
    "--area",
    type=int,
    minimum=50,
    action=Range,
    default=300,
    dest="area",
    help="thresholded area (in pixels) for the object's detection",
)
parser.add_argument(
    "--color",
    type=int,
    maximum=255,
    action=Range,
    default=196,
    dest="color",
    help="thresholded hue of the approaching object",
)
parser.add_argument(
    "--side",
    type=int,
    minimum=50,
    action=Range,
    default=240,
    dest="side",
    help="side (in pixels) of a detection square for the UI",
)
parser.add_argument(
    "--lang",
    choices=["en", "ru"],
    default="en",
    dest="lang",
    help="language of the UI",
)
parser.add_argument(
    "--pause",
    type=int,
    action=Range,
    default=5,
    dest="pause",
    help="delay (in seconds) before resuming the QR-code monitor",
)
parser.add_argument(
    "--logfile",
    default=LOG_FILE_DEFAULT,
    dest="logfile",
    help="full path to a log file",
)
parser.add_argument(
    "-v",
    "--verbose",
    "--debug",
    action="store_true",
    dest="verbose",
    help="increase verbosity by setting the logger's level to DEBUG",
)
args = parser.parse_args()

logger.configure(
    handlers=[
        dict(
            sink=sys.stderr,
            format="<lvl>{time:YYYY-MM-DD HH:mm:ss!UTC}  | {level: <8} | {name}:{function}:{line}: {message}</lvl>",
            level="DEBUG" if args.verbose else "INFO",
            colorize=LOG_COLOR,
        ),
        dict(
            sink=args.logfile,
            format="{time:YYYY-MM-DD HH:mm:ss!UTC}  | {level: <8} | {name}:{function}:{line}: {message}",
            level="DEBUG" if args.verbose else "INFO",
            rotation=LOG_ROTATION_SIZE,
            compression=LOG_COMPRESSION_FORMAT,
        ),
    ]
)
logger.debug("Running in debug mode")
logger.info('Logging the activity to file: "{}"', args.logfile)

env_prefix = "DEV" if args.dev else "PROD"
logger.debug("Loading environment variables from a .env file")
load_dotenv(find_dotenv(), override=True)
BOT_SKIPUPDATES = True
BOT_TOKEN = os.getenv(f"{env_prefix}_BOT_TOKEN")
DB_UID = os.getenv(f"{env_prefix}_DB_USER")
DB_PASSWORD = os.getenv(f"{env_prefix}_DB_PASSWORD")
DB_TABLE_NAME = os.getenv(f"{env_prefix}_DB_TABLENAME")
logger.success("Successfully loaded the environment variables")
logger.debug('Got minimal area of a potential QR-code: "{}"', args.area)
logger.debug('Got minimal hue of a potential QR-code: "{}"', args.color)
logger.debug('Got the detection square\'s side "{}"', args.side)
logger.debug('Got the UI language: "{}"', args.lang)
logger.debug('Got the delay time: "{}"', args.pause)

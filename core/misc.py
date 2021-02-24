import asyncio

import sqlanydb
from aiogram import Bot, Dispatcher
from aiogram.types.message import ParseMode
from aiogram.utils import executor
from aiogram.utils.exceptions import ValidationError
from loguru import logger

from core import config
from core.packages import PackagesLoader


try:
    bot = Bot(token=config.BOT_TOKEN, validate_token=True, parse_mode=ParseMode.MARKDOWN_V2)
except ValidationError:
    logger.critical("Bot token is invalid. Make sure that you've set a valid token in the .env file")
    quit()

loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)
runner = executor.Executor(dp, skip_updates=config.BOT_SKIPUPDATES)

loader = PackagesLoader()

try:
    logger.debug('Connecting to a SQLA database with UID "{}"', config.DB_UID)
    conn = sqlanydb.connect(uid=config.DB_UID, pwd=config.DB_PASSWORD)
    curs = conn.cursor()
    logger.success(
        'Successfully connected to SQLAnywhere database as "{}". Reading table "{}"',
        config.DB_UID,
        config.DB_TABLE_NAME,
    )
except sqlanydb.InterfaceError:
    logger.exception(
        "Couldn't connect to SQLAnywhere database. "
        'Make sure that you\'ve correctly set the full path to "dbcapi.dll" in the .env file'
    )
    quit()
except (TypeError, sqlanydb.OperationalError):
    logger.exception(
        "Couldn't connect to SQLAnywhere database. "
        "Make sure that you've correctly set your UID and password in the .env file"
    )
    quit()

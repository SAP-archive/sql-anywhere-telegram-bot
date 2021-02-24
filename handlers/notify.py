import asyncio
from datetime import datetime

import pytz
import sqlanydb
from aiogram.utils.exceptions import (
    BotBlocked,
    CantParseEntities,
    ChatNotFound,
    NetworkError,
    UserDeactivated,
)
from loguru import logger
from typing import Dict

from . import constants
from core import config
from core.misc import bot, curs


async def notify_user(row: Dict[str, str]) -> None:
    """Sends a notification about the order contained in :row: to a user with a Telegram ID from :row:.

    Args:
        row (dict): A dict containing full record about the user's order.
    """

    try:
        user_id = row["telegram_id"]
        timestamp = datetime.now(pytz.timezone(row["timezone"])).strftime("%d/%m/%Y %H:%M:%S %Z")

        lang = row.get("locale", "en_US")
        info = constants.MSG_NOTIFY_EN if lang.startswith("en") else constants.MSG_NOTIFY_RU
        info = (
            info.format(
                first_name=row["first_name"],
                timestamp=timestamp,
                id=row["id"],
                address=row["address"],
                product=row["product"],
                model=row["model"],
                price=float(row["price"]),
                amount=row["amount"],
                weight=float(row["weight"]),
            )
            .replace(".", "\.")
            .replace("-", "\-")
        )

        await bot.send_message(user_id, info)
        logger.success("Order notification message has been successfully sent to user {}", user_id)
    except CantParseEntities as ex:
        logger.error(
            'Notification failed. AIOgram couldn\'t properly parse the following text:\n"{}"\n Exception: {}',
            info,
            ex,
        )
    except ChatNotFound:
        logger.error("Notification failed. User {} hasn't started the bot yet", user_id)
    except BotBlocked:
        logger.error("Notification failed. User {} has blocked the bot", user_id)
    except UserDeactivated:
        logger.error("Notification failed. User {}'s account has been deactivated", user_id)
    except NetworkError:
        logger.critical("Could not access https://api.telegram.org/. Check your internet connection")
    except KeyError:
        logger.exception("Got invalid query response. See below for the details")


async def start(address: str, pause_success: int = 5, pause_fail: int = 1) -> None:
    """Checks whether the :address: string contains in the set of all different addresses saved in the table.
    If it does, gets the record containing :address: in its "address" field.
    Sends the record to the notification function.

    Args:
        address (str): The decoded address to check the table with.
        [optional] pause_success (int): Time in seconds to standby for after the notification was sent.
        [optional] pause_fail (int): Time in seconds to standby for after detecting an invalid QR-code.
    """

    try:
        query_addresses = "SELECT address FROM %s.%s;"
        curs.execute(
            query_addresses
            % (
                config.DB_UID,
                config.DB_TABLE_NAME,
            )
        )
        response_addresses = curs.fetchall()
        addresses = set([res[0] for res in response_addresses])
        if not (address in addresses):
            logger.warning('Address "{}" not found among the available addresses. Skipping', address)
            logger.info("Standing by for {} second(s)", pause_fail)
            await asyncio.sleep(pause_fail)
            return
        query = "SELECT * FROM %s.%s WHERE address='%s';"
        curs.execute(
            query
            % (
                config.DB_UID,
                config.DB_TABLE_NAME,
                address,
            )
        )
        response = curs.fetchone()
        logger.debug('Got response for address "{}": "{}"', address, response)
    except sqlanydb.Error:
        logger.exception("Encountered an error while handling query to the database. See below for the details")
        return

    res_row = {}

    for (i, field) in zip(range(len(response)), config.FIELDS):
        res_row[field] = response[i]

    await notify_user(res_row)
    logger.info("Standing by for {} second(s)", pause_success)
    await asyncio.sleep(pause_success)

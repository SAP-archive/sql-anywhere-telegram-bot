#!/usr/bin/env python3
r"""Chat-Bot for Telegram messenger as a test project showcasing a possible SAP SQLAnywhere RDMS implementation.

    This project simulates the following model:
    Suppose we have got an online shop, and a user made an order and activated our shop's bot via Telegram.
    At the start the user can choose the bot's language (English or Russian).  Suppose our user ordered a
    product from a different country and it needs to be delivered.  We've got a warehouse in the user's
    city where the foreign products are delivered first.  In that warehouse we also have got a hardware (a
    server or a Raspberry Pi) with a SAP SQLAnywhere database connection, the Internet connection and a web-cam
    attached. The orders data is expected to be stored in a table (in our case, named "Orders") of the following
    structure:

    +-------------------------------------------------------------------------------------------+
    |                                          Orders                                           |
    +--------------+---------------------------------------------+------------------------------+
    | C O L U M N  | T Y P E                                     | C O M M E N T                |
    +--------------+---------------------------------------------+------------------------------+
    | id           | UNSIGNED INT PRIMARY KEY NOT NULL IDENTITY  | ID of an order               |
    | product      | NVARCHAR(24) NOT NULL                       | Product's name               |
    | model        | NVARCHAR(20)                                | Product's model              |
    | price        | DECIMAL(10,2) NOT NULL                      | Product's price (in Euros)   |
    | amount       | UNSIGNED INT NOT NULL DEFAULT 1             | Product's amount             |
    | weight       | DECIMAL(8,3) NOT NULL                       | Product's weight (in kgs)    |
    | first_name   | NVARCHAR(16) NOT NULL                       | Customer's first name        |
    | last_name    | NVARCHAR(20)                                | Customer's last name         |
    | address      | NVARCHAR(48) NOT NULL                       | Customer's physical address  |
    | telegram_id  | UNSIGNED INT NOT NULL                       | Customer's Telegram ID       |
    | timezone     | NVARCHAR(16) DEFAULT 'UTC'                  | Customer's timezone          |
    | locale       | NVARCHAR(5) DEFAULT 'en_US'                 | Customer's preferred locale  |
    +--------------+---------------------------------------------+------------------------------+

    This script should also be run on the hardware.  It runs the Telegram bot and simultaneously connects to
    the running database and the web-cam.  Then it creates a window with the capture the web-cam's stream and
    awaits for a QR-code to be captured.  Suppose our products are stored in boxes with QR-codes that encode the
    recipients' addresses, and the web-cam can capture it as soon as the boxes arrive at the warehouse.
    Once such QR-code is captured, the script decodes it and acquires an address.  It then searches the
    orders table in the SQLAnywhere database to find a record with the decoded address in the "address" column.
    If the required record was found, meaning that the recipient and his/her order have been identified, the
    script sends a Telegram message to the user with a Telegram ID as in the "telegram_id" column from the
    record.  The message's language depends on the "locale" column; users can change their prefered locale
    using a bot command.

    As a result we have an automatic notification of our client about his/her order delivery status via a
    popular messaging app. It's also worth mentioning that it is just one of many possible problems such bot
    may solve, and it can be easily repurposed for a different setup.


    Copyright 2019-2021 Artemy Gevorkov

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import aiogram
from aiogram.utils.exceptions import NetworkError, Unauthorized
from loguru import logger

from core import misc, qr_cam


async def monitor_camera() -> None:
    logger.debug("Connecting to a web-cam")
    await qr_cam.scan_qr()


async def startup(dp: aiogram.Dispatcher) -> None:
    misc.loop.create_task(monitor_camera())


async def shutdown(dp: aiogram.Dispatcher) -> None:
    logger.debug("Committing all unsaved changes")
    misc.conn.commit()
    logger.debug("Shutting down DB connection")
    misc.curs.close()
    misc.conn.close()
    logger.success("Successfully committed unsaved changes and disconnected from the SQLAnywhere database")

    logger.debug("Shutting down the web-cam")
    qr_cam.free_all()
    logger.success("Successfully shut down the web-cam")


def main():
    misc.loader.load_packages(["handlers"])

    misc.runner.on_startup(startup)
    misc.runner.on_shutdown(shutdown)

    try:
        misc.runner.start_polling()
    except NetworkError:
        logger.critical("Could not access https://api.telegram.org/. Check your internet connection")
    except Unauthorized:
        logger.critical("Bot token is invalid. Make sure that you've set a valid token in the .env file")


if __name__ == "__main__":
    main()

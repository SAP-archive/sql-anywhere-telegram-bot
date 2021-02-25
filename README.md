# SAP SQL Anywhere Telegram Bot Sample

[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/sql-anywhere-telegram-bot)](https://api.reuse.software/info/github.com/SAP-samples/sql-anywhere-telegram-bot)

## Table of Contents

<details>
  <summary>Click to expand</summary>

  - [Description](#description)
    * [Main Features](#main-features)
  - [Requirements](#requirements)
    * [Modules Used](#modules-used)
  - [Download and Installation](#download-and-installation)
    * [Disclaimer](#disclaimer)
    * [Getting started](#getting-started)
    * [Getting Telegram-related Data](#getting-telegram-related-data)
    * [QR-coding the address](#qr-coding-the-address)
    * [Preparing the Database](#preparing-the-database)
    * [Setting the Environment Variables](#setting-the-environment-variables)
    * [Running and Testing Bot](#running-and-testing-bot)
  - [How to obtain support](#how-to-obtain-support)
  - [Contributing](#contributing)
    * [Style Guide](#style-guide)
  - [License](#license)
</details>

## Description

Asynchronous bot for Telegram messaging app utilizing a SAP (Sybase) SQL Anywhere RDMS and Computer Vision elements. It's implied that a machine this bot runs on is connected to a webcam and has got a SAP SQL Anywhere 17 database running. The bot is able to send its users specific messages based on a QR-code the webcam captures from its live video feed.
This particular code simulates delivery notification system but via an instant messenger (Telegram), not e-mail. For the details, please see the comment block at the beginning of [main.py](main.py) file. 
We also tried to thoroughly document the source code, so feel free to browse it.

### Main Features

- Asynchronous HTTP requests
- Detection and decoding QR-codes on the fly
- Detailed and customizable logging system
- Scalability and low imprint on hardware
- Easily repurposable for different tasks involving QR-codes.

## Requirements

Before proceeding, please ensure that all of the following conditions are met:

- Your device has got a webcam connected
- You have got a Telegram account
- [Python 3.7 or later](https://www.python.org/downloads/) is installed on your system
- [SAP SQL Anywhere 17](https://www.sap.com/cmp/td/sap-sql-anywhere-developer-edition-free-trial.html) and [SQL Central](https://wiki.scn.sap.com/wiki/display/SQLANY/SAP+SQL+Anywhere+Database+Client+Download) are installed on your system
- You have a basic understanding of the command line.

### Modules Used

This sample also uses the following open-source modules:

- [sqlanydb](https://github.com/sqlanywhere/sqlanydb) as a driver for SAP SQL Anywhere RDMS
- [AIOgram](https://github.com/aiogram/aiogram) as an asynchronous framework for the [Telegram Bot API](https://core.telegram.org/bots/api)
- [open-cv](https://github.com/skvark/opencv-python) and [numpy](https://numpy.org/) for the computer vision portion
- [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) for QR-code decoding
- [loguru](https://github.com/Delgan/loguru) for extensive logging
- [dotenv](https://github.com/theskumar/python-dotenv) for environment variables setup.

## Download and Installation

The full installation process consists of several steps involving different pieces of software. There's nothing complicated, but we'll try to go through this process step-by-step, explaining it as clearly as possible, so hopefully you'll end up with a minimal working example.

### Disclaimer

__This is merely an example of a possible technical integration of SAP SQL Anywhere RDMS into a Python-based project. The code of this particular sample heavily relies on [Telegram messaging app](https://telegram.org/) and its [Bot API](https://core.telegram.org/bots/api) to function properly. By proceeding, running and using the sample's code, the user becomes__

- __fully responsible for adherence to [Telegram's Terms of Service](https://telegram.org/tos) as well as acceptance of [Telegram's Privacy Policy](https://telegram.org/privacy)__
- __fully aware of the respective privacy regulations.__

__This sample is also provided "as-is" without any guarantee or warranty that raised issues will be answered or addressed in future releases.__

### Getting started

First, clone this repository:

```bat
git clone https://github.com/SAP-samples/sql-anywhere-telegram-bot.git
```

Change directory to this project's root folder. [Create and activate a virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments) (in this case, running on Windows) and install the required modules:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

<!--
_If you're currently using Python 3.9, then (as of October 2020) the `opencv-python` module has no wheel available yet. But if you're on Windows, you can install it via `pipwin`:_

```bat
pipwin install opencv-python
```
-->

### Getting Telegram-related Data

You'll need to know your Telegram ID to store it in the database, so later the bot will be able to send you notifications. Your Telegram ID is just an integer, the quickest way to acquire it is via [@MyIDBot](https://t.me/myidbot): open it in your Telegram app, start it and send it the `/getid` command. It should reply with your ID (say, `123456789`).

You should also create your own Telegram bot. To do that, search for the [@BotFather](https://t.me/botfather) Telegram bot and enter the `/newbot` command to create a new bot. Follow the instructions and provide a screen-name and a username for your bot. The username must, however, be unique and end with "bot"; the screen-name can be whatever you like. You should then receive a message with a new API token generated for your bot (say, `11111:XXXXXXXXXXX`). Now you can find your newly created bot on Telegram based on the username you gave it.

### QR-coding the address

The bot interprets QR-codes on the webcam feed as encoded addresses in our model. Let's turn an address into a QR-code and print it, so we can show it to the webcam later. The QR-code below encodes `WDF 01 BU04 Dietmar-Hopp-Allee 16 69190 Walldorf`:

[![Example QR-code](https://api.qrserver.com/v1/create-qr-code/?data=WDF+01+BU04+Dietmar-Hopp-Allee+16+69190+Walldorf&size=200x200)](https://api.qrserver.com/v1/create-qr-code/?data=WDF+01+BU04+Dietmar-Hopp-Allee+16+69190+Walldorf&size=400)

You can download it by clicking it and print it on a white sheet of paper or just open it on your smartphone. Alternatively, you may encode your preferred address online.

### Preparing the Database

Now when you've got every piece of data, you can create a database and fill all required columns. First, create an additional folder (in this case, named `db`) inside this project's root folder:

```bat
mkdir db
```

Create a database file using `dbinit` (in this case, named `orders.db`; `admin` as UID and `YourPassword` as password __(change it, it's just an example)__):

```bat
dbinit -dba admin,YourPassword -p 4k -z UTF8 -ze UTF8 -zn UTF8 db/orders.db
```

Now you've got a database file `orders.db` located in the `db` folder of this project (you may store this database file wherever you'd like). Open SQL Central and proceed with the following steps:

- right-click on "SQL Anywhere 17" and hit "Connect...",
- fill the "User ID" and "Password" fields with the same values you provided to `dbinit` (in this case, `admin` and `YourPassword` respectively),
- under "Action" choose "Start and connect to a database on this computer",
- provide full path to the database file you've just created (in this case, it's `full/path/to/this/project/db/orders.db`) and hit "Connect".

You're connected to the SQL Anywhere database and can interact with it. Right-click anywhere to open the Interactive SQL window, so you may execute SQL queries in the database.

First, create a table of orders (in our case, named `Orders`):

```sql
CREATE TABLE Orders (
    id UNSIGNED INT PRIMARY KEY NOT NULL IDENTITY,
    product NVARCHAR(24) NOT NULL,
    model NVARCHAR(20),
    price DECIMAL(10,2) NOT NULL,
    amount UNSIGNED INT NOT NULL DEFAULT 1,
    weight DECIMAL(8,3) NOT NULL,
    first_name NVARCHAR(16) NOT NULL,
    last_name NVARCHAR(20),
    address NVARCHAR(48) NOT NULL,
    telegram_id UNSIGNED INT NOT NULL,
    timezone NVARCHAR(16) DEFAULT 'UTC',
    locale NVARCHAR(5) DEFAULT 'en_US'
);
```

Then you can add an example order record to test the bot:

```sql
INSERT INTO "admin"."Orders"(product, model, price, weight, first_name, last_name, address, telegram_id, timezone) VALUES (
    'Lenovo Thinkpad',
    'X220',
    150.00,
    1.725,
    'Jon',
    'Doe',
    'WDF 01 BU04 Dietmar-Hopp-Allee 16 69190 Walldorf',
    123456789,
    'Europe/Berlin'
);
```

where `WDF 01 BU04 Dietmar-Hopp-Allee 16 69190 Walldorf` is the address encoded in the QR-code you printed by following the ["QR-coding the address" section](#qr-coding-the-address), and `123456789` is your Telegram ID sent by [@MyIDBot](https://t.me/myidbot) from the ["Getting Telegram-related Data" section](#getting-telegram-related-data). Obviously, you may customize other values however you like.

Make sure to close the Interactive SQL window afterwards, as it blocks query execution from any other source.

### Setting the Environment Variables

For the sake of convenience we store all required environment variables in a `.env` file. This repository contains a [.env.dist](.env.dist) file filled with dummy data in the root folder, so you'll need to copy it to `.env` file and change its values, as it's currently preset to the example values.

You'll absolutely have to set the `PROD_BOT_TOKEN` variable to the API token sent to you by [@BotFather](https://t.me/botfather), so it looks like this: `PROD_BOT_TOKEN="11111:XXXXXXXXXXX"`.
The `sqlanydb` module also requires the `SQLANY_API_DLL` variable to be set to the full path of `dbcapi.dll`. Unfortunately, SQL Anywhere doesn't create this variable automatically upon installation anymore, hence you have to specify it manually. On Windows this path is usually `C:\Program Files\SQL Anywhere 17\Bin64\dbcapi.dll`. However, if you run the 32-bit version of Python, you should change `Bin64` to `Bin32` in the path above.

So, if you're using the 64-bit version of Python on Windows and all our example values, the variables inside your `.env` file should end up looking like this:

```bash
SQLANY_API_DLL="C:\Program Files\SQL Anywhere 17\Bin64\dbcapi.dll"
PROD_BOT_TOKEN="11111:XXXXXXXXXXX"
PROD_DB_USER="admin"
PROD_DB_PASSWORD="YourPassword"
PROD_DB_TABLENAME="Orders"
```

You may also set the `DEV` variables using different values meant for testing, if you're going to run the bot with the `--dev` flag.

### Running and Testing Bot

Make sure that you still have the virtual environment activated, the QR-code printed, your webcam connected and the SQL Anywhere database connection established. Start the bot by running

```bat
python main.py
```

in the project's root directory. After the `Updates were skipped successfully` log message, a window with your webcam's video stream should appear. Search for the bot you've created with [@BotFather](https://t.me/botfather) and start it. If everything is right, the bot should respond by offering you to select the language.

So now, whenever you show the QR-code encoding your address to your webcam, the bot should alert you with a notification. With the example record from our table, the notification should look like this:

```
Hello, Jon!

As of 25/10/2020 18:47:19 CET, your order 1 has arrived to our base.
We are going to deliver it to your address "WDF 01 BU04 Dietmar-Hopp-Allee 16 69190 Walldorf" no later than in 3 days.

Product Details:
Product: Lenovo Thinkpad
Model: X220
Price: €150.00
Amount: 1
Weight: 1.725 kg
ID: 1
```

You may configure the camera UI via the CLI arguments. To see all configurable options of the bot, run `python main.py --help`.

## How to obtain support

[Create an issue](https://github.com/SAP-samples/sql-anywhere-telegram-bot/issues) in this repository if you find a bug or have questions about the content.
 
For additional support, [ask a question in SAP Community](https://answers.sap.com/questions/ask.html).

## Contributing

If you'd like to contribute to this sample, please follow these steps:

1. [Fork this repository](https://github.com/SAP-samples/sql-anywhere-telegram-bot/fork).
2. Create a branch: `git checkout -b feature/foo`.
3. Make your changes and commit them: `git commit -am 'Add foo feature'`.
4. Push your changes to the branch: `git push origin feature/foo`.
5. Create a new pull request.

__Pull requests are warmly welcome!__

### Style Guide

We try our best sticking to the [PEP 8](https://www.python.org/dev/peps/pep-0008) Style Guide, using [type hints (PEP 484)](https://www.python.org/dev/peps/pep-0484) and providing descriptive [docstrings](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring) adhering to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings). So we check that our code is formatted properly using [Flake8](https://flake8.pycqa.org/en/latest/index.html) and [black](https://github.com/ambv/black) code formatter; the type checking is handled by [mypy](https://github.com/python/mypy).

Install these modules in your virtual environment by running

```bat
python -m pip install -r dev-requirements.txt
```

so you can either run the checks manually, or set up [this great pre-commit](https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/) that will be running it for you.

You may also check out the configuration we use in [pyproject.toml](pyproject.toml) and [setup.cfg](setup.cfg).

## License
Copyright (c) 2021 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSES/Apache-2.0.txt) file.

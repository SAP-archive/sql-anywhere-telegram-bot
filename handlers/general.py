import sqlanydb
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from loguru import logger

from . import constants
from core import config
from core.misc import bot, conn, curs, dp


@dp.message_handler(commands=["start"])
async def cmd_start(message: Message) -> None:
    """Handles the "/start" command from a Telegram user.  Runs when the user first starts the bot.
    Greets the user by his/her full name and allows to choose the interface language.

    Args:
        message (Message): User's Telegram message that is sent to the bot.
    """

    str_greet = constants.MSG_START.format(name=message.from_user.full_name)
    btn_en = InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    btn_ru = InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    inline_kb = InlineKeyboardMarkup().add(btn_en, btn_ru)

    await bot.send_message(message.chat.id, str_greet, reply_markup=inline_kb)
    logger.info("User {} called /start", message.from_user.id)


@dp.message_handler(commands=["lang"])
async def cmd_lang(message: Message) -> None:
    """Handles the "/lang" command from a Telegram user.  Allows the user to change the locale from the chosen one.
    Outputs the message in the language that was initially chosen by the user.

    Args:
        message (Message): User's Telegram message that is sent to the bot.
    """

    query = "SELECT locale FROM %s.%s WHERE telegram_id=%d;"
    curs.execute(
        query
        % (
            config.DB_UID,
            config.DB_TABLE_NAME,
            message.from_user.id,
        )
    )
    (lang,) = curs.fetchone()
    logger.debug('Got user\'s {} current language "{}"', message.from_user.id, lang)
    str_lang = "Please choose your language\." if lang.startswith("en") else "Пожалуйста, выберите язык\."
    btn_en = InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    btn_ru = InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    inline_kb = InlineKeyboardMarkup().add(btn_en, btn_ru)

    await bot.send_message(message.chat.id, str_lang, reply_markup=inline_kb)
    logger.info("User {} called /lang", message.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith("lang"))
async def set_lang(cb_query: CallbackQuery) -> None:
    """Handles the callback that sets the user preferred locale.  Updates the locale in the table.

    Args:
        cb_query (CallbackQuery): User's Telegram callback query that is sent to the bot.
    """

    lang = "en_US" if cb_query.data.endswith("en") else "ru_RU"
    info = "Setting your language..." if lang.startswith("en") else "Настраиваю язык..."
    await bot.answer_callback_query(cb_query.id, text=info)

    try:
        query = "UPDATE %s.%s SET locale='%s' WHERE telegram_id=%d;"
        curs.execute(
            query
            % (
                config.DB_UID,
                config.DB_TABLE_NAME,
                lang,
                cb_query.from_user.id,
            )
        )
        logger.debug("Commiting the changes")
        conn.commit()

    except sqlanydb.Error as ex:
        logger.exception(ex)
        return

    str_setlang = (
        "Language is set to English\.\nCall /lang to change it\."
        if lang.startswith("en")
        else "Ваш язык Русский\.\nВызовите команду /lang, чтобы его изменить\."
    )

    logger.info('User {} set the language to "{}"', cb_query.from_user.id, lang)
    await bot.send_message(cb_query.from_user.id, str_setlang)

import html
import logging
import sys
import traceback

from aiogram import Bot
from aiogram.types import ErrorEvent

from app.config import settings


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if any(getattr(handler, "_app_stdout_handler", False) for handler in root_logger.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler._app_stdout_handler = True
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root_logger.addHandler(handler)


async def on_error(event: ErrorEvent, bot: Bot) -> bool:
    user_input = "Unknown update"

    if event.update.message and event.update.message.from_user:
        user_input = f"Message from {event.update.message.from_user.id}: {event.update.message.text}"
    elif event.update.callback_query and event.update.callback_query.from_user:
        user_input = f"Callback from {event.update.callback_query.from_user.id}: {event.update.callback_query.data}"

    try:
        tb = "".join(traceback.format_exception(event.exception))[-3000:]
        text = (f"<b>Unhandled error</b>\n{html.escape(user_input)}\n"
                f"<pre>{html.escape(tb)}</pre>")
        await bot.send_message(settings.alert_chat_id, text)

    except Exception as e:
        logger.exception("Failed to send alert")

    logging.error(f"Unhandled error ({user_input})\nException details: {event.exception}", exc_info=event.exception)

    return True
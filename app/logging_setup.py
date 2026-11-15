import html
import logging
import sys
import traceback

from aiogram import Bot
from aiogram.types import ErrorEvent

from app.config import settings

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if any(
        getattr(handler, "_app_stdout_handler", False)
        for handler in root_logger.handlers
    ):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler._app_stdout_handler = True
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )
    root_logger.addHandler(handler)


async def on_error(event: ErrorEvent, bot: Bot) -> bool:
    user_input = "Unknown update"

    message = event.update.message
    callback_query = event.update.callback_query
    if message and message.from_user:
        user_input = f"Message from user {message.from_user.id}"
    elif callback_query and callback_query.from_user:
        user_input = f"Callback from user {callback_query.from_user.id}"

    exception = event.exception
    logger.error(
        "Unhandled error (%s)",
        user_input,
        exc_info=(type(exception), exception, exception.__traceback__),
    )

    tb = "".join(traceback.format_exception(exception))[-650:]
    text = (
        f"<b>Unhandled error</b>\n{html.escape(user_input)}\n"
        f"<pre>{html.escape(tb)}</pre>"
    )

    if callback_query:
        try:
            await callback_query.answer("An error occurred", show_alert=True)
        except Exception:
            logger.exception("Failed to answer callback query after an error")

    try:
        await bot.send_message(settings.alert_chat_id, text)
    except Exception:
        logger.exception("Failed to send error alert")

    return True
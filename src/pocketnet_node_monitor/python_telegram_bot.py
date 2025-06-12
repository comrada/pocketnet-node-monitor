import json
from decimal import Decimal

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

from .base_telegram_bot import BaseTelegramBot
from .rpc_client import RpcClient


class PythonTelegramBot(BaseTelegramBot):
    def __init__(self, token: str, rpc_client: RpcClient):
        super().__init__(token, rpc_client)
        self.app = ApplicationBuilder().token(self.token).build()
        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button))

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [
                InlineKeyboardButton("GetWalletInfo", callback_data="getwalletinfo"),
                InlineKeyboardButton("GetStakingInfo", callback_data="getstakinginfo"),
                InlineKeyboardButton("GetStakeReport", callback_data="getstakereport"),
            ],
            [InlineKeyboardButton("GetConnectionCount", callback_data="getconnectioncount")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        rpc_result = await self.rpc_call(query.data)
        await query.edit_message_text(
            text=f"```{json.dumps(rpc_result, indent=2, default=self.custom_serializer)}\n```",
            parse_mode='Markdown'
        )

    @staticmethod
    def custom_serializer(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self):
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

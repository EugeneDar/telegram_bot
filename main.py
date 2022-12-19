TELEGRAM_TOKEN = ''

import logging
import sys
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from enum import Enum


# Enable logging to console
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)

class State(Enum):
    BET_ENTERING = 0
    PLAYING = 1
    NOTHING = 2


async def new_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['balance'] = 500

    await update.message.reply_text(
        "Okay, I created you a new account. You now have 500 schmekels in your balance."
    )


async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not 'balance' in context.chat_data:
        await update.message.reply_text('You don\'t have an account')
        return

    context.chat_data['state'] = State.BET_ENTERING

    await update.message.reply_text('New game started.\nPlease enter your bet numerically:')


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    if not 'balance' in context.chat_data:
        await update.message.reply_text('You don\'t have an account')
        return

    await update.message.reply_text(
        "Your balance: " + str(context.chat_data['balance']) + " schmekels"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    WELCOME_MESSAGE = 'If you have some questions call /help'

    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!" + "\n" + WELCOME_MESSAGE,
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "To call help: /help\n"
        "To see balance: /balance\n"
        "To create new account: /new_account\n"
        "To start new game: /new_game\n"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data['state'] == State.BET_ENTERING:
        if not str.isnumeric(update.message.text):
            await update.message.reply_text('Not a number')
            return

        bet = int(update.message.text)
        context.chat_data['bet'] = bet
        context.chat_data['balance'] -= bet
        await update.message.reply_text('Took your bet')

        # create and save deck

        # distribute cards


    await update.message.reply_text('Sorry, I don\'t know this command')


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("new_account", new_account))
    application.add_handler(CommandHandler("new_game", new_game))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == "__main__":
    TELEGRAM_TOKEN = sys.argv[1]
    main()

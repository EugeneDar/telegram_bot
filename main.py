TELEGRAM_TOKEN = ''

import logging
import sys
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from game import Game
from game import State


# Enable logging to console
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# logger = logging.getLogger(__name__)


async def new_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['balance'] = 500

    context.chat_data['game'] = Game()

    await update.message.reply_text(
        "Okay, I created you a new account. You now have 500 schmekels in your balance."
    )


async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not 'balance' in context.chat_data:
        await update.message.reply_text('You don\'t have an account')
        return

    context.chat_data['game'] = Game()
    context.chat_data['game'].state = State.BET_ENTERING

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
    await update.message.reply_text(
        "To call help: /help\n"
        "To see balance: /balance\n"
        "To create new account: /new_account\n"
        "To start new game: /new_game\n"
        "To read rules: /about_game\n"
    )


async def about_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "In each round you place a bet. If you win, the money is doubled. If you lose, you lose money. In the event of a tie, the bet is returned to you.\n\n"
        "Each card has its own price: cards from 2 to 9 are valued according to the numbers, an ace is valued at 1 or 11 at the discretion of the player, the remaining cards are valued at 10 points.\n\n"
        "You have only two options: take one more card or stop.\n\n"
        "If you have more than 21 points, you automatically lose.\n\n"
        "After you have finished dialing cards, the dealer starts doing it. The dealer doesn't make his own decisions, but simply draws cards until he has less than 17 points.\n\n"
        "Also an important fact is that you only see one of the dealer's cards when you deal."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.chat_data['game'].state == State.BET_ENTERING:
        if not str.isnumeric(update.message.text):
            await update.message.reply_text('Not a number')
            return

        bet = int(update.message.text)

        if bet <= 0:
            await update.message.reply_text('Wrong number')
            return
        if bet > context.chat_data['balance']:
            await update.message.reply_text('You do not have enough money for such a bet')
            return

        context.chat_data['game'].bet = bet
        context.chat_data['balance'] -= bet
        await update.message.reply_text('Took your bet')

        await update.message.reply_text(
            'Dealer cards:\n' + context.chat_data['game'].dealer_cards[0] + ' and another one'
        )

        await update.message.reply_text(
            'Your cards:\n' + Game.cards_to_string(context.chat_data['game'].user_cards)
        )

        await update.message.reply_text('You can now write "more" to take another card or "stop" to stop')

        context.chat_data['game'].state = State.PLAYING
        return

    if context.chat_data['game'].state == State.PLAYING:
        text = update.message.text

        if text.lower() == 'more':

            context.chat_data['game'].user_cards.append(context.chat_data['game'].deck.pop(0))
            await update.message.reply_text(
                'Your cards now:\n' + Game.cards_to_string(context.chat_data['game'].user_cards)
            )

            score = Game.evaluate_hand(context.chat_data['game'].user_cards)
            if score > 21:
                await update.message.reply_text('You lose')
                context.chat_data['game'].state = State.NOTHING

            return

        if text.lower() == 'stop':

            await update.message.reply_text(
                'Dealer cards now:\n' + Game.cards_to_string(context.chat_data['game'].dealer_cards)
            )

            while Game.evaluate_hand(context.chat_data['game'].dealer_cards) < 17:
                context.chat_data['game'].dealer_cards.append(context.chat_data['game'].deck.pop(0))
                await update.message.reply_text(
                    'Dealer cards now:\n' + Game.cards_to_string(context.chat_data['game'].dealer_cards)
                )

            user_score = Game.evaluate_hand(context.chat_data['game'].user_cards)
            dealer_score = Game.evaluate_hand(context.chat_data['game'].dealer_cards)

            if user_score > dealer_score or dealer_score > 21:
                await update.message.reply_text('You win')
                context.chat_data['balance'] += context.chat_data['game'].bet * 2
            elif user_score < dealer_score:
                await update.message.reply_text('You lose')
            else:
                await update.message.reply_text('Draw')
                context.chat_data['balance'] += context.chat_data['game'].bet

            await update.message.reply_text('Your current balance: ' + str(context.chat_data['balance']))

            return

    await update.message.reply_text('Sorry, I don\'t know this command')


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("new_account", new_account))
    application.add_handler(CommandHandler("new_game", new_game))
    application.add_handler(CommandHandler("about_game", about_game))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == "__main__":
    TELEGRAM_TOKEN = sys.argv[1]
    main()

# ==============================================================================
# dicegame.py - Telegram Dice Game Commands
# ==============================================================================
# Fun emoji dice games using Telegram's built-in dice feature.
# Commands: /dice, /dart, /basket, /jackpot, /ball, /football
# Can also be triggered by sending the emoji directly: 🎲, 🎯, 🏀, 🎰, 🎳, ⚽
# ==============================================================================

# ==============================================================================
# dicegame.py - Telegram Dice Game Commands
# ==============================================================================
# Fun emoji dice games using Telegram's built-in dice feature.
# Commands: /dice, /dart, /basket, /jackpot, /ball, /football
# Can also be triggered by sending the emoji directly: 🎲, 🎯, 🏀, 🎰, 🎳, ⚽
# ==============================================================================

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from BlacMusic import app

# Each entry: command name -> (dice emoji, reply phrasing template).
# The template receives (emoji, mention, score) via .format().
_GAMES = {
    "dice": ("🎲", "{0} {1} rolled: {2}"),
    "jackpot": ("🎰", "{0} Hey {1}, your score is: {2}"),
    "dart": ("🎯", "{0} Hey {1}, your score is: {2}"),
    "basket": ("🏀", "{0} Hey {1}, your score is: {2}"),
    "ball": ("🎳", "{0} Hey {1}, your score is: {2}"),
    "football": ("⚽", "{0} Hey {1}, your score is: {2}"),
}


def _make_dice_handler(emoji: str, template: str):
    """Build a command handler that rolls the given dice emoji and replies with the given template."""
    async def handler(bot: Client, message: Message) -> None:
        try:
            await message.delete()
        except Exception:
            pass
        try:
            sent_dice = await bot.send_dice(message.chat.id, emoji)
            score = sent_dice.dice.value
            await message.reply_text(
                template.format(emoji, message.from_user.mention, score),
                quote=True,
            )
        except Exception as e:
            await message.reply_text(f"❌ Error: {e}")
    return handler


# Register one handler per game command, sharing the same implementation.
for _command, (_emoji, _template) in _GAMES.items():
    app.on_message(filters.command(_command))(_make_dice_handler(_emoji, _template))


@app.on_message(filters.dice)
async def dice_emoji_handler(_, message: Message) -> None:
    """React to a dice emoji sent directly (not via a slash command) with its score."""
    try:
        score = message.dice.value
        emoji = message.dice.emoji
        await message.reply_text(f"{emoji} {message.from_user.mention} scored: {score}", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

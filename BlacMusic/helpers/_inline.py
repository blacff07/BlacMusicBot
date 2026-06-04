from pyrogram import types
from BlacMusic import app, config


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data="cancel_dl")]])

    def controls(self, chat_id, status=None, timer=None, remove=False, paused=False):
        keyboard = []
        _is_paused = paused or (status and "ᴘᴀᴜꜱᴇᴅ" in str(status))
        if status:
            keyboard.append([self.ikb(text=status, callback_data=f"controls status {chat_id}")])
        elif timer:
            keyboard.append([self.ikb(text=timer, callback_data=f"controls status {chat_id}")])
        if not remove:
            if not _is_paused:
                keyboard.append([
                    self.ikb(text="« 30", callback_data=f"controls seek_back_30 {chat_id}"),
                    self.ikb(text="« 10", callback_data=f"controls seek_back_10 {chat_id}"),
                    self.ikb(text="10 »", callback_data=f"controls seek_forward_10 {chat_id}"),
                    self.ikb(text="30 »", callback_data=f"controls seek_forward_30 {chat_id}"),
                ])
            keyboard.append([
                self.ikb(text="▷",   callback_data=f"controls resume {chat_id}"),
                self.ikb(text="II",  callback_data=f"controls pause {chat_id}"),
                self.ikb(text="↻",   callback_data=f"controls replay {chat_id}"),
                self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}"),
                self.ikb(text="▢",   callback_data=f"controls stop {chat_id}"),
            ])
            keyboard.append([self.ikb(text="ᴅᴇʟᴇᴛᴇ", callback_data=f"controls close {chat_id}")])
        return self.ikm(keyboard)

    def help_markup(self, _lang, back=False):
        if back:
            rows = [[self.ikb(text="← ʙᴀᴄᴋ", callback_data="help")]]
        else:
            rows = [
                [
                    self.ikb(text="🎵 ᴘʟᴀʏʙᴀᴄᴋ", callback_data="help_playback"),
                    self.ikb(text="⏱️ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="help_controls"),
                ],
                [
                    self.ikb(text="👑 ᴀᴅᴍɪɴꜱ", callback_data="help_admins"),
                    self.ikb(text="🔑 ᴀᴜᴛʜ", callback_data="help_auth"),
                ],
                [
                    self.ikb(text="🚫 ʙʟᴀᴄᴋʟɪꜱᴛ", callback_data="help_blacklist"),
                    self.ikb(text="💡 ᴛɪᴘꜱ", callback_data="help_tips"),
                ],
                [self.ikb(text="← ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start")],
            ]
        return self.ikm(rows)

    def ping_markup(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([
            [
                self.ikb(text="📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
                self.ikb(text="🆘 ꜱᴜᴘᴘᴏʀᴛ",  url=config.SUPPORT_CHAT),
            ],
            [self.ikb(text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                      url=f"https://t.me/{app.username}?startgroup=true")],
        ])

    def play_queued(self, chat_id, item_id, _text):
        return self.ikm([
            [
                self.ikb(text="▷",  callback_data=f"controls resume {chat_id}"),
                self.ikb(text="∣∣", callback_data=f"controls pause {chat_id}"),
                self.ikb(text=">>", callback_data=f"controls skip {chat_id}"),
                self.ikb(text="▣",  callback_data=f"controls stop {chat_id}"),
            ],
            [self.ikb(text="ᴅᴇʟᴇᴛᴇ", callback_data=f"controls close {chat_id}")],
        ])

    def queue_markup(self, chat_id, _text, playing):
        action = "pause" if playing else "resume"
        return self.ikm([[self.ikb(text=_text, callback_data=f"controls {action} {chat_id} q")]])

    def settings_markup(self, lang, admin_only, language, chat_id):
        play_mode = "ᴀᴅᴍɪɴ ᴏɴʟʏ" if admin_only else "ᴇᴠᴇʀʏᴏɴᴇ"
        return self.ikm([
            [
                self.ikb(text=f"ᴘʟᴀʏ ᴍᴏᴅᴇ: {play_mode}", callback_data=f"playmode {chat_id}"),
            ],
            [
                self.ikb(text="← ʙᴀᴄᴋ", callback_data="start"),
            ],
        ])

    def start_key(self, lang, pm=False):
        if pm:
            rows = [
                [
                    self.ikb(text="❓ ʜᴇʟᴘ", callback_data="help"),
                    self.ikb(text="⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings"),
                ],
                [
                    self.ikb(text="📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
                    self.ikb(text="💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
                ],
                [
                    self.ikb(text="➕ ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.username}?startgroup=true"),
                ],
            ]
        else:
            rows = [
                [self.ikb(text="ᴘʟᴀʏ ᴍᴜꜱɪᴄ 🎵", url=f"https://t.me/{app.username}?start=play")],
            ]
        return self.ikm(rows)


buttons = Inline()
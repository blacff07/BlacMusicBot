from pyrogram import types
from BlacMusic import app, config


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data="cancel_dl")]])

    def controls(self, chat_id, status=None, timer=None, remove=False):
        keyboard = []
        if status:
            keyboard.append([self.ikb(text=status, callback_data=f"controls status {chat_id}")])
        elif timer:
            keyboard.append([self.ikb(text=timer, callback_data=f"controls status {chat_id}")])
        if not remove:
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
            rows = [[self.ikb(text="ʙᴀᴄᴋ", callback_data="help_main")]]
        else:
            rows = [
                [
                    self.ikb(text="ᴀᴅᴍɪɴꜱ",      callback_data="help_admins"),
                    self.ikb(text="ᴀᴜᴛʜ",         callback_data="help_auth"),
                    self.ikb(text="ʙʀᴏᴀᴅᴄᴀꜱᴛ",   callback_data="help_broadcast"),
                ],
                [
                    self.ikb(text="ʙʟ-ᴄʜᴀᴛ",     callback_data="help_blchat"),
                    self.ikb(text="ʙʟ-ᴜꜱᴇʀ",     callback_data="help_bluser"),
                    self.ikb(text="ɢ-ʙᴀɴ",        callback_data="help_gban"),
                ],
                [
                    self.ikb(text="ʟᴏᴏᴘ",         callback_data="help_loop"),
                    self.ikb(text="ᴘʟᴀʏ",         callback_data="help_play"),
                    self.ikb(text="ǫᴜᴇᴜᴇ",        callback_data="help_queue"),
                ],
                [
                    self.ikb(text="ꜱᴇᴇᴋ",         callback_data="help_seek"),
                    self.ikb(text="ꜱʜᴜꜰꜰʟᴇ",     callback_data="help_shuffle"),
                    self.ikb(text="ᴘɪɴɢ",         callback_data="help_ping"),
                ],
                [
                    self.ikb(text="ꜱᴛᴀᴛꜱ",        callback_data="help_stats"),
                    self.ikb(text="ꜱᴜᴅᴏ",         callback_data="help_sudo"),
                    self.ikb(text="ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="help_maintenance"),
                ],
                [self.ikb(text="ʙᴀᴄᴋ", callback_data="start")],
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
        return self.ikm([
            [
                self.ikb(text=lang["play_mode"] + " ➜", callback_data=f"controls status {chat_id}"),
                self.ikb(text=admin_only, callback_data="playmode"),
            ],
        ])

    def start_key(self, lang, private=False):
        if private:
            rows = [
                [self.ikb(text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{app.username}?startgroup=true")],
                [
                    self.ikb(text="🆘 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
                    self.ikb(text="👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=f"https://t.me/{config.OWNER_USERNAME}" if config.OWNER_USERNAME else config.SUPPORT_CHAT),
                ],
                [self.ikb(text="📖 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help")],
            ]
        else:
            rows = [
                [self.ikb(text="➕ ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{app.username}?startgroup=true")],
                [self.ikb(text="🆘 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT)],
            ]
        return self.ikm(rows)

    def yt_key(self, link):
        return self.ikm([[
            self.ikb(text="ᴄᴏᴘʏ ʟɪɴᴋ",       copy_text=link),
            self.ikb(text="ᴏᴘᴇɴ ɪɴ ʏᴏᴜᴛᴜʙᴇ", url=link),
        ]])
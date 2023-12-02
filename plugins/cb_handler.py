import asyncio
import os

from bot import (
    LOGGER,
    UPLOAD_AS_DOC,
    UPLOAD_TO_DRIVE,
    delete_all,
    formatDB,
    gDict,
    queueDB,
    showQueue,
    mergeApp
)
from helpers import database
from helpers.utils import UserSettings
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from plugins.mergeVideo import mergeNow
from plugins.mergeVideoAudio import mergeAudio
from plugins.mergeVideoSub import mergeSub
from plugins.streams_extractor import streamsExtractor
from plugins.usettings import userSettings


@Client.on_callback_query()
async def callback_handler(c: Client, cb: CallbackQuery):
    #     await cb_handler.cb_handler(c, cb)
    # async def cb_handler(c: Client, cb: CallbackQuery):
    if cb.data == "merge":
        await cb.message.edit(
            text="Wʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜᴘʟᴏᴀᴅ?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📤 Tᴏ ᴛᴇʟᴇɢʀᴀᴍ", callback_data="to_telegram"
                        ),
                        InlineKeyboardButton("🌫️ Tᴏ ᴅʀɪᴠᴇ", callback_data="to_drive"),
                    ],
                    [InlineKeyboardButton("⛔ Cᴀɴᴄᴇʟ ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_drive":
        try:
            urc = await database.getUserRcloneConfig(cb.from_user.id)
            await c.download_media(
                message=urc, file_name=f"userdata/{cb.from_user.id}/rclone.conf"
            )
        except Exception as err:
            await cb.message.reply_text("Rclone not Found, Unable to upload to drive")
        if os.path.exists(f"userdata/{cb.from_user.id}/rclone.conf") is False:
            await cb.message.delete()
            await delete_all(root=f"downloads/{cb.from_user.id}/")
            queueDB.update(
                {cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}}
            )
            formatDB.update({cb.from_user.id: None})
            return
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="Oᴋᴀʏ ɪ'ʟʟ ᴜᴘʟᴏᴀᴅ ᴛᴏ ᴅʀɪᴠᴇ\nDᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇɴᴀᴍᴇ? Dᴇғᴀᴜʟᴛ ғɪʟᴇ ɴᴀᴍᴇ ɪs **[@blvckangl]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Dᴇғᴀᴜʟᴛ", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rᴇɴᴀᴍᴇ", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cᴀɴᴄᴇʟ ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_telegram":
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="Hᴏᴡ ᴅᴏ ʏᴏ ᴡᴀɴᴛ ᴛᴏ ᴜᴘʟᴏᴀᴅ ғɪʟᴇ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎞️ Vɪᴅᴇᴏ", callback_data="video"),
                        InlineKeyboardButton("📁 Fɪʟᴇ", callback_data="document"),
                    ],
                    [InlineKeyboardButton("⛔ Cᴀɴᴄᴇʟ ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "document":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇɴᴀᴍᴇ? Dᴇғᴀᴜʟᴛ ғɪʟᴇ ɴᴀᴍᴇ ɪs **[@blvckangl]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Dᴇғᴀᴜʟᴛ", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rᴇɴᴀᴍᴇ", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cᴀɴᴄᴇʟ ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "video":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇɴᴀᴍᴇ? Dᴇғᴀᴜʟᴛ ғɪʟᴇ ɴᴀᴍᴇ ɪs **[@blvckangl]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cᴀɴᴄᴇʟ ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data.startswith("rclone_"):
        if "save" in cb.data:
            fileId = cb.message.reply_to_message.document.file_id
            LOGGER.info(fileId)
            await c.download_media(
                message=cb.message.reply_to_message,
                file_name=f"./userdata/{cb.from_user.id}/rclone.conf",
            )
            await database.addUserRcloneConfig(cb, fileId)
        else:
            await cb.message.delete()
        return

    elif cb.data.startswith("rename_"):
        user = UserSettings(cb.from_user.id, cb.from_user.first_name)
        if "YES" in cb.data:
            await cb.message.edit(
                "Cᴜʀʀᴇɴᴛ ғɪʟᴇɴᴀᴍᴇ: **[@blvckangl]_merged.mkv**\n\nSᴇɴᴅ ᴍᴇ ɴᴇᴡ ғɪʟᴇ ɴᴀᴍᴇ ᴡɪᴛʜᴏᴜᴛ ᴇxᴛᴇɴsɪᴏɴ: ʏᴏᴜ ʜᴀᴠᴇ 𝟷 ᴍɪɴᴜᴛᴇ"
            )
            res: Message = await c.listen(cb.message.chat.id, timeout=300)
            if res.text:
                new_file_name = f"downloads/{str(cb.from_user.id)}/{res.text}.mkv"
                await res.delete(True)
            if user.merge_mode == 1:
                await mergeNow(c, cb, new_file_name)
            elif user.merge_mode == 2:
                await mergeAudio(c, cb, new_file_name)
            elif user.merge_mode == 3:
                await mergeSub(c, cb, new_file_name)

            return
        if "NO" in cb.data:
            new_file_name = (
                f"downloads/{str(cb.from_user.id)}/[@blvckangl]_merged.mkv"
            )
            if user.merge_mode == 1:
                await mergeNow(c, cb, new_file_name)
            elif user.merge_mode == 2:
                await mergeAudio(c, cb, new_file_name)
            elif user.merge_mode == 3:
                await mergeSub(c, cb, new_file_name)

    elif cb.data == "cancel":
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("Sucessfully Cancelled")
        await asyncio.sleep(5)
        await cb.message.delete(True)
        return
    
#added new btn feature
    elif cb.data == "continue":
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("Resuming Process in  5 sec")
        await asyncio.sleep(5)
        merged_video_path = await MergeVideo(
        input_file=input_, user_id=cb.from_user.id, message=cb.message, format_="mkv"
        )
        
        
    elif cb.data.startswith("gUPcancel"):
        cmf = cb.data.split("/")
        chat_id, mes_id, from_usr = cmf[1], cmf[2], cmf[3]
        if int(cb.from_user.id) == int(from_usr):
            await c.answer_callback_query(
                cb.id, text="Gᴏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ . . . 🛠", show_alert=False
            )
            gDict[int(chat_id)].append(int(mes_id))
        else:
            await c.answer_callback_query(
                callback_query_id=cb.id,
                text="⚠️ Oᴘᴘs ⚠️ \n I ɢᴏᴛ ᴀ ғᴀʟsᴇ ᴠɪsɪᴛᴏʀ 🚸 !! \n\n 📛 Sᴛᴀʏ ᴀᴛ ʏᴏᴜʀ ʟɪᴍɪᴛs !!📛",
                show_alert=True,
                cache_time=0,
            )
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return

    elif cb.data == "close":
        await cb.message.delete(True)
        try:
            await cb.message.reply_to_message.delete(True)
        except Exception as err:
            pass

    elif cb.data.startswith("showFileName_"):
        id = int(cb.data.rsplit("_", 1)[-1])
        LOGGER.info(
            queueDB.get(cb.from_user.id)["videos"],
            queueDB.get(cb.from_user.id)["subtitles"],
        )
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(id)
        m = await c.get_messages(chat_id=cb.message.chat.id, message_ids=id)
        if queueDB.get(cb.from_user.id)["subtitles"][sIndex] is None:
            try:
                await cb.message.edit(
                    text=f"File Name: {m.video.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 Aᴅᴅ sᴜʙᴛɪᴛʟᴇ",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back")],
                        ]
                    ),
                )
            except:
                await cb.message.edit(
                    text=f"File Name: {m.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 Aᴅᴅ sᴜʙᴛɪᴛʟᴇ",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back")],
                        ]
                    ),
                )
            return
        else:
            sMessId = queueDB.get(cb.from_user.id)["subtitles"][sIndex]
            s = await c.get_messages(chat_id=cb.message.chat.id, message_ids=sMessId)
            try:
                await cb.message.edit(
                    text=f"File Name: {m.video.file_name}\n\nSubtitles: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ ғɪʟᴇ",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ sᴜʙᴛɪᴛʟᴇ",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back")],
                        ]
                    ),
                )
            except:
                await cb.message.edit(
                    text=f"File Name: {m.document.file_name}\n\nSubtitles: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ ғɪʟᴇ",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ Rᴇᴍᴏᴠᴇ sᴜʙᴛɪᴛʟᴇ",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back")],
                        ]
                    ),
                )
            return

    elif cb.data.startswith("addSub_"):
        sIndex = int(cb.data.split(sep="_")[1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        rmess = await cb.message.edit(
            text=f"Sᴇɴᴅ ᴍᴇ ᴀ sᴜʙᴛɪᴛʟᴇ ғɪʟᴇ, ʏᴏᴜ ʜᴀᴠᴇ 𝟷 ᴍɪɴᴜᴛᴇ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Bᴀᴄᴋ", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        subs: Message = await c.listen(
            (cb.message.chat.id,None,None), filters="filters.document", timeout=60
        )
        if subs is not None:
            media = subs.document or subs.video
            if media.file_name.rsplit(".")[-1] not in "srt":
                await subs.reply_text(
                    text=f"Pʟᴇᴀsᴇ ɢᴏ ʙᴀᴄᴋ ғɪʀsᴛ",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 Bᴀᴄᴋ", callback_data=f"showFileName_{vMessId}"
                                )
                            ]
                        ]
                    ),
                    quote=True,
                )
                return
            queueDB.get(cb.from_user.id)["subtitles"][sIndex] = subs.id
            await subs.reply_text(
                f"Added {subs.document.file_name}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 Bᴀᴄᴋ", callback_data=f"showFileName_{vMessId}"
                            )
                        ]
                    ]
                ),
                quote=True,
            )
            await rmess.delete(True)
            LOGGER.info("Aᴅᴅᴇᴅ sᴜʙ ᴛᴏ ʟɪsᴛ")
        return

    elif cb.data.startswith("removeSub_"):
        sIndex = int(cb.data.rsplit("_")[-1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        queueDB.get(cb.from_user.id)["subtitles"][sIndex] = None
        await cb.message.edit(
            text=f"Sᴜʙᴛɪᴛʟᴇ ʀᴇᴍᴏᴠᴇᴅ ɴᴏᴡ ɢᴏ ʙᴀᴄᴋ ᴏʀ sᴇɴᴅ ɴᴇxᴛ ᴠɪᴅᴇᴏ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Bᴀᴄᴋ", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        LOGGER.info("Sᴜʙ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ʟɪsᴛ")
        return

    elif cb.data == "back":
        await showQueue(c, cb)
        return

    elif cb.data.startswith("removeFile_"):
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(
            int(cb.data.split("_", 1)[-1])
        )
        queueDB.get(cb.from_user.id)["videos"].remove(int(cb.data.split("_", 1)[-1]))
        await showQueue(c, cb)
        return

    elif cb.data.startswith("ch@ng3M0de_"):
        uid = cb.data.split("_")[1]
        user = UserSettings(int(uid), cb.from_user.first_name)
        mode = int(cb.data.split("_")[2])
        user.merge_mode = mode
        user.set()
        await userSettings(
            cb.message, int(uid), cb.from_user.first_name, cb.from_user.last_name, user
        )
        return

    elif cb.data == "tryotherbutton":
        await cb.answer(text="Tʀʏ ᴏᴛʜᴇʀ ʙᴜᴛᴛᴏɴ → ☛")
        return

    elif cb.data.startswith("toggleEdit_"):
        uid = int(cb.data.split("_")[1])
        user = UserSettings(uid, cb.from_user.first_name)
        user.edit_metadata = False if user.edit_metadata else True
        user.set()
        await userSettings(
            cb.message, uid, cb.from_user.first_name, cb.from_user.last_name, user
        )
        return
    
    elif cb.data.startswith('extract'):
        edata = cb.data.split('_')[1]
        media_mid = int(cb.data.split('_')[2])
        try:
            if edata == 'audio':
                LOGGER.info('audio')
                await streamsExtractor(c,cb,media_mid,exAudios=True)
            elif edata == 'subtitle':
                await streamsExtractor(c,cb,media_mid,exSubs=True)
            elif edata == 'all':
                await streamsExtractor(c,cb,media_mid,exAudios=True,exSubs=True)
        except Exception as e:
            LOGGER.error(e)

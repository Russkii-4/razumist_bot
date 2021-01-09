import re
import time
import logging
from datetime import datetime, timedelta
from asyncio import sleep
from functools import wraps
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.utils.executor import start_polling
from aiogram.types import ContentType, ChatType
from aiogram.dispatcher.filters import Command, BoundFilter


logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token="1548967936:AAGqYm37VMDR2B2WdxUk1NcuJLjoEkLH6cc")
dp: Dispatcher = Dispatcher(bot=bot)


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)
        me = await bot.get_chat_member(message.chat.id, (await bot.get_me()).id)
        return (user.status == "creator" or user.can_restrict_members) and me.can_restrict_members


class IsBotAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        me = await bot.get_chat_member(message.chat.id, (await bot.get_me()).id)
        return me.can_delete_messages and me.can_restrict_members


async def is_enough_rights(chat_id):
    bot_id = (await bot.get_me()).id
    me = await bot.get_chat_member(chat_id, bot_id)
    return me.can_delete_messages and me.can_restrict_members


def parse(text):
    out = {"seconds": 0, "minutes": 0, "hours": 0, 
           "days": 0, "weeks": 0}

    for i in out.keys():
        pattern = r"\d+\s?{}".format(i[0])
        bar = re.findall(pattern, text)
        if not bar:
            continue
        foo = bar[0].replace(i[0], "")
        out[i] = int(foo)
    result = datetime.timestamp(
            timedelta(seconds=out["seconds"], minutes=out["minutes"], 
            hours=out["hours"], days=out["days"], weeks=out["weeks"])
            + datetime.now()
    )
    return result


@dp.message_handler(IsAdmin(), Command("unmute"), chat_type=ChatType.SUPERGROUP)
async def cmd_mute(message: types.Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("ну и кого мне размутить?")
    if reply.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
        return await message.reply("отказ.")
    try:
        status = (await bot.get_chat_member(message.chat.id, reply.from_user.id)).status 
    except Exception:
        return
    if not status == "restricted":
        return await message.reply("он и так может говорить.")
    permissions = (await bot.get_chat(message.chat.id)).permissions
    await bot.restrict_chat_member(message.chat.id, reply.from_user.id, permissions=permissions)
    await message.reply(f"{reply.from_user.full_name} снова может говорить.")


@dp.message_handler(IsAdmin(), Command("mute"), chat_type=ChatType.SUPERGROUP)
async def cmd_mute(message: types.Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("ну и кого мне мутить?")
    if reply.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
        return await message.reply("отказ.")
    args = message.get_args()
    until_date = max(time.time() + 60, parse(args))
    await bot.restrict_chat_member(message.chat.id, reply.from_user.id, until_date=until_date)
    await message.reply(
        f"*{reply.from_user.full_name}* помещён в карантин на `{datetime.fromtimestamp(until_date)}`.", 
        parse_mode=types.ParseMode.MARKDOWN
    )



@dp.message_handler(IsBotAdmin(), content_types=ContentType.NEW_CHAT_MEMBERS, chat_type=ChatType.SUPERGROUP)
async def process_new_user(message: types.Message):
    text = (
        "Танкист, перед тем чтобы писать в чат, ознакомся с правилами:\n\n"
        "Требования:\n"
        "- Ведите себя адекватно, что бы не пришлось вас утихомиривать мутом на час, сутки, трое суток и тд.\n" 
        "- Не стоит кидаться на всех подряд со словами \"Маму твою ебал\" и тд и тп, если ваше мнение не совпадает со мнением окружающих.\n\n"
        "Запрещено:\n"
        " - Любая реклама, без согласования с `@bella_trice`\n"
        " - Шок контент/порно/политота/религия\n"
        " - Покупка/продажа/обмен аккаунтов, обсуждение \"дешёвой\" голды\n"
        " - Флуд/спам\n\n"
        "*Бан за нарушение от 1 дня до пермача.*\n"
        "Разбан обсуждать не только с глав. админом.\n"
        "Получили мут?\n"
        "*Вопросы ко всем админам*, а не к одному лишь `@FrutoSpidoznic`\n"
        "По этому имейте в наличии 2-3 юзернейма админов, что бы можно было с ними связаться\n\n"
        "Главный администратор:\n"
        "   `@FrutoSpidoznic`\n\n"
        "Модеры:\n"
        "   `@Kopo6ok_Jly4LLIe_Bcex`\n"
        "   `@SnusSong`\n"
        "   `@UltraVkid`\n"
        "   `@Whoecciev`\n"
        "   `@OhMyGetFxcked`\n"
        "   `@Deniso4k`\n"
        "   `@SilenTBoY84`\n"
        "   `@Hyizenberg`\n"
        "   `@Panzerwaffe_potni_B_Pb_lybly_ero`\n"
        "   `@KJIACCHA9I_PA6OTA`\n"
        "   `@SkyS0ng`\n"
        "   `@ithivvothn`\n"
        "   `@CreamKoK`\n"
        "   `@kovol`\n"
        "   `@S3XYPanzerwaffeONLINE`\n"
        "   `@MyNameWasDeleted`\n" 
        "   `@FuckS0ng`\n"
        "   `@Po11n`\n"
        "   `@TToIIIuJIOu_KoK`\n"
        "   `@Solov41`\n"
        "   `@Rammstein_one_loveandPanzerwaffe`\n"
        "   `@Prikerman`\n"
        "   `@SkySong`\n"
        "   `@ithiwothn`\n"
        "   `@SkunsSong`\n"
        "   `@OdmorzadomorzaSong`\n"
        "   `@AHreJl_TBOEu_Me4Tbl`\n"
        "   `@A_Myxa_ToIiIe_BerToJleT`\n"
        "   `@aWong`\n\n"
        "Если вы не прочитали правила и не сохранили список модеров, то это *ваши проблемы*\n\n"
        "Администрация *не имеет права выдавать ПЕРМАЧ* по личной неприязни\n\n"
        "*АДМИНИСТРАЦИЯ ИМЕЕТ ПРАВО ЕБАТЬ ВАШИХ МАМ В ПИЗДАК*"
    )

    for user in message.new_chat_members:
        print(await bot.get_chat_member(message.chat.id, user.id))
        if (await bot.get_chat_member(message.chat.id, user.id)).status == "restricted" or user.id == (await bot.get_me()).id:
            continue
        keyboard = {"inline_keyboard": [[{"text": "прочитал", "callback_data": user.id}]]}
        await message.reply(text, parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
        await bot.restrict_chat_member(message.chat.id, user.id)


@dp.callback_query_handler()
async def callback_worker(call: types.CallbackQuery):
    if call.from_user.id != int(call.data):
        return await call.answer("эта кнопка не для тебя!", show_alert=True)
    permissions = (await bot.get_chat(call.message.chat.id)).permissions
    await bot.restrict_chat_member(call.message.chat.id, call.from_user.id, permissions=permissions)
    await call.message.delete()


if __name__ == "__main__":
    start_polling(
        dispatcher=dp,
        skip_updates=False,
        relax=0.5
     )




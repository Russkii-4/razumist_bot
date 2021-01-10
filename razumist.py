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
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import escape_md


logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token="")
dp: Dispatcher = Dispatcher(bot=bot, storage=MemoryStorage())



def rate_limit(func, limit=2):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        message = args[0]
        try:
            await dp.throttle("sticker", rate=limit)
        except Throttled as t:
            await message_throttled(message, t)

    return wrapper


async def message_throttled(message: types.Message, throttled: Throttled):
    if throttled.exceeded_count == 2:
        await message.reply(f'{message.from_user.full_name}, предупреждение\nне флуди стикерами!')
    if throttled.exceeded_count == 4:
        await message.reply(f'дубина {message.from_user.full_name} нафлудил и отправился в мут на 30 минут')
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+1800)
        await message.delete()


class IsNotAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return not user.status in ("administrator", "creator")


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        user = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return (user.status == "creator" or user.can_restrict_members)


def parse(text):
    time_dict = {"seconds": 0, "minutes": 0, "hours": 0, 
           "days": 0, "weeks": 0}

    for i in time_dict.keys():
        pattern = r"\d+\s?{}".format(i[0])
        match = re.findall(pattern, text)
        if not match:
            continue
        time_dict[i] = int(match[0].replace(i[0], ""))
    result = datetime.timestamp(
            timedelta(seconds=time_dict["seconds"], minutes=time_dict["minutes"], 
            hours=time_dict["hours"], days=time_dict["days"], weeks=time_dict["weeks"])
            + datetime.now()
    )
    reason = re.findall(r"\w+$", text)
    reason = escape_md(reason[0]) if reason else "не указана"
    return result, reason


@dp.message_handler(IsAdmin(), Command("unmute"), chat_type=ChatType.SUPERGROUP)
async def cmd_mute(message: types.Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("ну и кого мне размутить?")
    if reply.from_user.id in [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]:
        return await message.reply("отказ.")
    try:
        status = (await bot.get_chat_member(message.chat.id, reply.from_user.id)).status 
    except Exception as e:
        return await message.reply(e)
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
    until_date, reason = parse(args)
    until_date = max(time.time() + 60, until_date)
    await bot.restrict_chat_member(message.chat.id, reply.from_user.id, until_date=until_date)
    out_time = datetime.fromtimestamp(until_date)
    until_date = f"{out_time.date()} {out_time.time().hour}:{out_time.time().minute}"
    name = escape_md(reply.from_user.full_name)
    text = f"*{name}* помещён в карантин до `{until_date}`\n\nпричина: *{reason}*"
    await message.reply(text, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(content_types=ContentType.NEW_CHAT_MEMBERS, chat_type=ChatType.SUPERGROUP)
async def process_new_user(message: types.Message):
    text = (
        "Танкист, перед тем что бы писать в чат, ознакомся с правилами:\n\n"
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
        "   `@Deniso4k`\n"
        "   `@SilenTBoY84`\n"
        "   `@Hyizenberg`\n"
        "   `@Panzerwaffe_potni_B_Pb_lybly_ero`\n"
        "   `@KJIACCHA9I_PA6OTA`\n"
        "   `@SkyS0ng`\n"
        "   `@S3XYPanzerwaffeONLINE`\n"
        "   `@MyNameWasDeleted`\n" 
        "   `@FuckS0ng`\n"
        "   `@Po11n`\n"
        "   `@TToIIIuJIOu_KoK`\n"
        "   `@SkySong`\n"
        "   `@ithiwothn`\n"
        "   `@SkunsSong`\n"
        "   `@OdmorzadomorzaSong`\n"
        "   `@AHreJl_TBOEu_Me4Tbl`\n"
        "   `@A_Myxa_ToIiIe_BerToJleT`\n"
        "   `@aWong`\n\n"
        "Если вы не прочитали правила и не сохранили список модеров, то это *ваши проблемы*\n\n"
        "Администрация *не имеет права выдавать ПЕРМАЧ* по личной неприязни\n\n"
        "*АДМИНИСТРАЦИЯ ИМЕЕТ ПРАВО ЕБАТЬ ВАШИХ МАМОК В ПИЗДАК*"
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


@dp.message_handler(IsNotAdmin(), content_types=ContentType.STICKER, chat_type=ChatType.SUPERGROUP)
@rate_limit
async def throttled_stickers(message: types.Message):
    pass


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    start_polling(
        relax=0.4,
        dispatcher=dp,
        skip_updates=False,
        on_shutdown=on_shutdown
     )




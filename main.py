from telegram import (
    Bot, 
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    BotCommand, 
    BotCommandScopeChat, 
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import NetworkError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, time
from l10n import lang, localizer, init_localizer, TRANSLATIONS
import pytz
import math
import os
import re
import traceback

from config import (
    BOT_TOKEN, 
    TIMEZONE, 
    ShardInfo, 
    LOCAL_TIMEZONE, 
    POPULAR_TIMEZONES, 
    PER_PAGE, 
    ALL_TIMEZONES, 
    DATABASE_URL
)
from core.db_utils import (
    init_db_sync,
    upsert_chat,
    get_all_chat_ids,
    get_user_language,
    set_user_language,
    get_user_timezone,
    set_user_timezone,
    get_user_notify,
    set_user_notify,
    get_user_notify_mute,
    set_user_notify_mute,
)

from core.logger import logger
from core.shards import (
    get_shard_info, 
    ShardInfoPrint, 
    get_shard_times_land, 
    get_shard_times_end
    )

class SkyShardsBot:
    mShard_info: ShardInfo = None
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.bot = Bot(token=BOT_TOKEN)
        self.db_url = db_url        
        # Инициализируем DB
        init_db_sync(self.db_url)
        #Хранилище настроек в памяти (dict: user_id → dict с настройками)
        self.user_settings: dict[int, dict] = {}        
        logger.info("__init__ SkyShardsBot")
        tz = LOCAL_TIMEZONE
        self.scheduler = AsyncIOScheduler(timezone=tz)
        self.application = Application.builder().token(self.bot.token).build()
        self.refresh_today_shard(tz)   

# ----------------- START COMMAND -----------------
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id             

        #Определяем язык пользователя — читаем из DB и если нет, используем telegram language
        user = update.effective_user
        chat = update.effective_chat
        db_lang = await get_user_language(self.db_url, user_id)
        lang_code = getattr(user, "language_code", None)
        simple_lang = None
        if lang_code:
            simple_lang = "ru" if lang_code.startswith("ru") else "en"
        chosen_lang = db_lang or simple_lang or "en"
        mLg = None
        if chosen_lang == "ru":
            mLg = lang.RU
        else:
            mLg = lang.EN
        init_localizer(mLg)
        if db_lang is None:
            await upsert_chat(self.db_url, user.id, chat.id, chosen_lang)
            await set_user_language(self.db_url, user_id, chosen_lang)
        
        #Ищем часовой пояс пользователя в базе
        tz = await self.update_tz(user_id)    
        
        #Значение настройки напоминаний
        c_notif = await get_user_notify(self.db_url, user_id)
        c_notif_mute = await get_user_notify_mute(self.db_url, user_id)
        await set_user_notify(self.db_url, user_id, c_notif)
        await set_user_notify_mute(self.db_url, user_id, c_notif_mute)

        text = f"/start - user_id={user_id} timezone={tz!r} lang={chosen_lang} notif={c_notif} notif_mute={c_notif_mute}"
        print(text) 
        logger.info(text)

        #Вывод основной информации
        hello_m = localizer.format_message('messages.hello_message')   
        #кнопка ReplyKeyboard
        r_key = await self.get_reply_key(user_id)
        await update.message.reply_text(
            hello_m,
            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True) 
        )
        self.refresh_today_shard(tz) 
        today_shard = ShardInfoPrint(self.mShard_info, tz)
        text_shard = today_shard.print_today_shard()
        await self.bot.send_message(chat_id=user_id, text=text_shard, parse_mode='HTML')

        tz_text = None
        if tz:
            tx1 = localizer.format_message('messages.tz_u_timezone1')  
            tz_text = f"<i>{tx1}: {tz}</i>"            
        else:
            tx1 = localizer.format_message('messages.tz_select')
            tz_text = f"<i>{tx1} <b>/set_timezone</b></i>"
        await self.bot.send_message(chat_id=user_id, text=tz_text, parse_mode='HTML')

# -------------------------------------------------------
    #обновить и вернуть текст кнопки
    async def get_reply_key(self, user_id: int)->list[list[str]]:
        r_key = None
        c_notif = await get_user_notify(self.db_url, user_id)
        if c_notif == True:
            r_key = [[localizer.format_message('BUTTON_TEXTS.b_notify_off')]]  
        else:
            r_key = [[localizer.format_message('BUTTON_TEXTS.b_notify_on')]]
        return r_key
    
    #Включить уведомления об осколках 
    async def notify_on_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        user_id = update.message.from_user.id
        await set_user_notify(self.db_url, user_id, True)
        await set_user_notify_mute(self.db_url, user_id, False)
        await self.update_loc(user_id)
        mess = localizer.format_message('messages.shards_notif_on')  
        r_key = await self.get_reply_key(user_id) 
        await update.message.reply_text(
            mess,
            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
            )  

    #Выключить уведомления об осколках
    async def notify_off_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        user_id = update.message.from_user.id
        await set_user_notify(self.db_url, user_id, False)
        await self.update_loc(user_id)
        mess = localizer.format_message('messages.shards_notif_off')
        r_key = await self.get_reply_key(user_id) 
        await update.message.reply_text(
            mess,
            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
            ) 

    #Выключить все уведомления об осколках
    async def notify_mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):        
        user_id = update.message.from_user.id
        await set_user_notify_mute(self.db_url, user_id, True)
        await set_user_notify(self.db_url, user_id, False)
        await self.update_loc(user_id)
        mess = localizer.format_message('messages.shards_notif_mute')
        r_key = await self.get_reply_key(user_id) 
        await update.message.reply_text(
            mess,
            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
            )        

    #Сменить язык
    async def change_language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        user_id = update.message.from_user.id
        current = await get_user_language(self.db_url, user_id)
        new_lang = 'en' if current == 'ru' else 'ru'
        await set_user_language(self.db_url, user_id, new_lang)        
        await self.update_loc(user_id)         
        #обновить и перерисовать меню
        commands = self.build_bot_commands()
        await self.application.bot.set_my_commands(commands=commands,scope=BotCommandScopeChat(chat_id=user_id))
        #обновить и перерисовать кнопку
        r_key = await self.get_reply_key(user_id) 
        await update.message.reply_text(
            localizer.format_message('messages.settings_lang'),
            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
            )

    #Установить часовой пояс
    async def set_timezone_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            localizer.format_message('messages.tz_select'), 
            reply_markup=self.build_timezone_keyboard(0)
        )

    #Подробная информация об осколках
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        user_id = update.effective_user.id
        await self.update_loc(user_id)
        tz = await self.update_tz(user_id)  
        self.refresh_today_shard(tz) 
        today_shard = ShardInfoPrint(self.mShard_info, tz)
        logger.info(f"/info - {user_id} - {tz}")
        today_shard_text = today_shard.render()
        await self.bot.send_message(chat_id=user_id, text=today_shard_text, parse_mode='HTML')

    #обновить язык из базы
    async def update_loc(self, user_id: int):        
        current = await get_user_language(self.db_url, user_id)
        mLg = None
        if current == 'ru':
            mLg = lang.RU
        else:
            mLg = lang.EN
        init_localizer(mLg)

    #обновить таймзона из базы
    async def update_tz(self, user_id: int) -> str:
        tz = await get_user_timezone(self.db_url, user_id)
        if tz is None:
            tz = LOCAL_TIMEZONE 
        return tz

    #Доступные команды
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        await self.update_loc(user_id)        
        help = localizer.format_message('help_message')
        await self.bot.send_message(chat_id=user_id, text=help, parse_mode='HTML')        

    #О программе
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        await self.update_loc(user_id)   
        help = localizer.format_message('about_message')
        image_path = "image/image.png"
        if os.path.exists(image_path):
            #Если файл найден — отправляем картинку
            with open(image_path, "rb") as photo:
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=help,
                    parse_mode="HTML"
                )
        else:
            await self.bot.send_message(chat_id=user_id, text=help, parse_mode="HTML") 

    #обновление осколков
    def refresh_today_shard(self, tz: str):        
        current_date = datetime.now(pytz.timezone(tz))
        self.mShard_info = get_shard_info(current_date)# + timedelta(days=0)
        return 
    
# ----------------- Напоминания -----------------
    #Ежедневное утреннее уведомление в 11:00 по Asia/Tbilisi
    #Ежедневное утреннее уведомление в 00:00 по America/Los_Angeles
    async def morning_message(self):      
        chat_ids = await get_all_chat_ids(self.db_url)
        if not chat_ids:
            return        
        for chat_id_n in chat_ids:
            try:
                c_notif_mute = await get_user_notify_mute(self.db_url, chat_id_n)
                if c_notif_mute == False:                
                    await set_user_notify(self.db_url, chat_id_n, True)
                    await self.update_loc(chat_id_n)  
                    tz = await self.update_tz(chat_id_n) 
                    self.refresh_today_shard(tz)
                    today_shard = ShardInfoPrint(self.mShard_info, tz)   
                    today_shards = today_shard.print_morning_shard() 
                    r_key = await self.get_reply_key(chat_id_n) 
                    await self.bot.send_message(
                            chat_id=chat_id_n, 
                            text=today_shards,
                            reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True), 
                            parse_mode='HTML'
                            )                   
            except Exception as e:
                logger.warning(f"Failed to send {chat_id_n}: {e}")

    def shard_reminder_format_message(self):           
        realm_names = localizer.get_realm_name2(self.mShard_info.realm)
        main_info = localizer.format_message('messages.darkness_fell')  
        realm = f"<b>{realm_names}</b>" 
        return main_info+realm

    async def shard_reminder_land(self):  
        chat_ids = await get_all_chat_ids(self.db_url)
        if not chat_ids:
            return        
        for chat_id_n in chat_ids:
            try:
                c_notif_mute = await get_user_notify_mute(self.db_url, chat_id_n)
                if c_notif_mute == False:
                    c_notif = await get_user_notify(self.db_url, chat_id_n)                    
                    if c_notif:
                        await self.update_loc(chat_id_n)
                        main_info = self.shard_reminder_format_message()                                    
                        await self.bot.send_message(
                            chat_id=chat_id_n, 
                            text=main_info, 
                            parse_mode='HTML'
                            )
            except Exception as e:
                    logger.warning(f"Failed to send {chat_id_n}: {e}")     

    async def shard_reminder_end(self): 
        chat_ids = await get_all_chat_ids(self.db_url)
        if not chat_ids:
            return        
        for chat_id_n in chat_ids:
            try:
                c_notif_mute = await get_user_notify_mute(self.db_url, chat_id_n)
                if c_notif_mute == False:
                    c_notif = await get_user_notify(self.db_url, chat_id_n)
                    if c_notif:              
                        await self.update_loc(chat_id_n)
                        main_info = self.shard_reminder_format_message()
                        main_info_ = localizer.format_message('messages.darkness_fell_last') 
                        await self.bot.send_message(
                            chat_id=chat_id_n, 
                            text=main_info+'\n'+main_info_, 
                            parse_mode='HTML'
                            )
            except Exception as e:
                    logger.warning(f"Failed to send {chat_id_n}: {e}")  
    
    #Ежедневные сообщения напоминания про осколки в 3 временных рамки
    def setup_schedule(self):
        #очищаем старые напоминания
        try:
            self.scheduler.remove_job('morning_message')
        except Exception:
            pass        
        for i in range(3):
            for kind in ["land", "end"]:
                job_id = f"shard_reminder_{kind}_{i}"
                try:
                    self.scheduler.remove_job(job_id)
                except Exception:
                    pass
        #обновление осколков на текущий день
        tz = TIMEZONE        
        self.refresh_today_shard(tz)

        #Настройка расписания        
        if self.mShard_info.has_shard:
            time_list_land = get_shard_times_land(self.mShard_info, tz)
            time_list_end = get_shard_times_end(self.mShard_info, tz)            
            #время начала осколков
            for i, shard_time in enumerate(time_list_land): 
                self.scheduler.add_job( 
                    self.shard_reminder_land,
                    trigger=CronTrigger(
                        hour=shard_time.hour, 
                        minute=shard_time.minute, 
                        timezone=tz
                        ),
                    id=f'shard_reminder_land_{i}'
                )
            #время до окончания осколков пол часа
            for i, shard_time in enumerate(time_list_end):
                self.scheduler.add_job(
                    self.shard_reminder_end,
                    trigger=CronTrigger(
                        hour=shard_time.hour, 
                        minute=shard_time.minute, 
                        timezone=tz
                        ),
                    id=f'shard_reminder_end_{i}'
                )

        #утреннее уведомление   
        self.scheduler.add_job(
            self.morning_message,
            CronTrigger(hour=0, minute=0, second=50, timezone=tz),#tz = TIMEZONE
            #CronTrigger(hour=13, minute=53, second=00, timezone='Asia/Tbilisi'),
            id='morning_message'  
            )

# -------------------------------------------------------
    def setup_handlers(self):
        # --- Команды (CommandHandlers) ---
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("notify_on", self.notify_on_command))
        self.application.add_handler(CommandHandler("notify_off", self.notify_off_command))        
        self.application.add_handler(CommandHandler("notify_mute", self.notify_mute_command))
        self.application.add_handler(CommandHandler("change_language", self.change_language_command))
        self.application.add_handler(CommandHandler("info", self.info_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("set_timezone", self.set_timezone_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("about", self.about_command))

        # --- CallbackQueryHandlers: самые специфичные PATTERN'ы первыми ---
        #timezone callbacks — все callback.data начинаются с "TZ"
        self.application.add_handler(CallbackQueryHandler(self.timezone_callback, pattern=r'^TZ'))

        #настройки: явный список кнопок настроек, в pattern все значения callback.data
        self.application.add_handler(
            CallbackQueryHandler(
                self.button_handler,
                pattern=r'^(toggle_notify_mute|toggle_lang|toggle_timezone|set_timezone|open_settings)$'
            )
        )
        
        #общий fallback для callback'ов — регистрируется последним
        #этот хендлер будет вызываться, если ни один из выше не подошёл
        self.application.add_handler(CallbackQueryHandler(self.callback_query_handler))

        # обработчик кнопки ReplyKeyboard
        r_key_on_ru = TRANSLATIONS["ru"]["BUTTON_TEXTS"]["b_notify_on"]
        r_key_off_ru = TRANSLATIONS["ru"]["BUTTON_TEXTS"]["b_notify_off"]
        r_key_on_en = TRANSLATIONS["en"]["BUTTON_TEXTS"]["b_notify_on"]
        r_key_off_en = TRANSLATIONS["en"]["BUTTON_TEXTS"]["b_notify_off"]

        all_button_texts = [r_key_on_ru, r_key_off_ru, r_key_on_en, r_key_off_en]
        pattern = "^(" + "|".join(map(re.escape, all_button_texts)) + ")$"
        self.application.add_handler(MessageHandler(filters.TEXT & filters.Regex(pattern), self.reply_button_handler))

        # --- MessageHandlers ---
        #текст для поиска TZ: ловим ТОЛЬКО обычный текст (не команды)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_for_search))
        #общий MessageHandler — сохраняем chat при любых сообщениях, но исключаем служебные StatusUpdate-ы
        self.application.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, self.save_chat_on_message))

    def build_bot_commands(self) -> list[BotCommand]:        
        return [
            BotCommand("start", localizer.format_message('menu.m_start')),
            BotCommand("info", localizer.format_message('menu.m_info')),
            BotCommand("settings", localizer.format_message('menu.m_settings')),
            BotCommand("help", localizer.format_message('menu.m_help')),
            BotCommand("about", localizer.format_message('menu.m_about'))
        ]
    
    #Устанавливаем команды в меню Telegram
    async def set_bot_commands(self):
        try:
            commands = self.build_bot_commands()
            await self.application.bot.set_my_commands(commands)
        except Exception as e:
                logger.warning(f"Failed to install commands: {e}")  

    #Действия при запуске
    async def startup(self, application):        
        self.scheduler.start()

    #Действия при остановке
    async def shutdown(self, application): 
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    #async def error_handler(self, update, context):
    #    if isinstance(context.error, NetworkError):
    #        text = f"Network error, will retry automatically..."
    #        print(text)
    #        logger.warning(text)    

    async def error_handler(update, context):
        err = context.error
        #Тип ошибки и её текст
        logger.error(f"⚠️ Exception type: {type(err)}")
        logger.error(f"⚠️ Exception message: {err}")
        #Если это именно NetworkError
        if isinstance(err, NetworkError):
            logger.warning("🌐 Network error, bot will retry automatically...")
        #Полный traceback (удобно в отладке)
        tb = "".join(traceback.format_exception(type(err), err, err.__traceback__))
        logger.debug("Full traceback:\n%s", tb)
        #Можно также вывести в консоль
        print("⚠️ Exception type:", type(err))
        print("⚠️ Exception message:", err)
        print("Full traceback:\n", tb)        

# ----------------- RUN -----------------
    def run(self):
        self.setup_schedule() 
        self.scheduler.add_job(self.setup_schedule, CronTrigger(hour=0, minute=0, timezone=TIMEZONE))
        self.setup_handlers()
        self.application.add_error_handler(self.error_handler)

        async def on_startup(application):
            await self.startup(application)
            await self.set_bot_commands()
            try:
                await self.application.bot.delete_webhook()
                text = "Webhook successfully removed"
                print(text)
            except Exception as e:
                text = f"Failed to remove webhook: {e}"
                print(text)
                logger.warning(text)          

        async def on_shutdown(application):
            await self.shutdown(application)

        self.application.post_init = on_startup
        self.application.post_shutdown = on_shutdown

        #self.application.bot.delete_webhook()

        print("Start bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)       

# -------------------------------------------------------

# ----------------- МЕНЮ И КНОПКИ НАСТРОЕК -----------------
    #Создаём inline-клавиатуру
    def build_settings_keyboard(
            self, c_notif_mute: bool, 
            lang_code: str | None = None
        ) -> InlineKeyboardMarkup:
        n_mute = localizer.format_message('messages.settings_n_mute')
        n_mute_on = localizer.format_message('messages.settings_n_mute_on')
        notify_mute_text = n_mute_on if c_notif_mute else n_mute
        lang_text = "🌐 RU" if lang_code == "ru" else "🌐 EN"
        timezone_text = localizer.format_message('messages.settings_timezone')  
        keyboard = [
            [
                InlineKeyboardButton(notify_mute_text, callback_data="toggle_notify_mute"),
                InlineKeyboardButton(lang_text, callback_data="toggle_lang")
            ],
            [InlineKeyboardButton(timezone_text, callback_data="toggle_timezone")]
        ]
        return InlineKeyboardMarkup(keyboard)

    #текст настроек
    def create_settings_message(self, c_notif: bool, 
                                c_notif_mute: bool, 
                                user_lang: str | None = None,
                                tz: str | None = None                                
                                ) -> str:
        n_on = localizer.format_message('messages.settings_message_notify_on') 
        n_off = localizer.format_message('messages.settings_message_notify_off')
        settings_notify = localizer.format_message('messages.settings_message_notify') 
        notify_text = n_on if c_notif else n_off

        n_mute_on = localizer.format_message('messages.settings_message_mute_on')
        n_mute_off = localizer.format_message('messages.settings_message_mute_off')
        settings_notify_mute = localizer.format_message('messages.settings_message_mute') 
        notify_mute_text = n_mute_on if c_notif_mute else n_mute_off

        n_l_ru = localizer.format_message('messages.settings_message_lang_ru')
        n_l_en = localizer.format_message('messages.settings_message_lang_en')
        settings_lang = localizer.format_message('messages.settings_message_lang') 
        lang_text = n_l_ru if user_lang == "ru" else n_l_en
        
        settings_tz = localizer.format_message('messages.settings_message_timezone') 
        tz_text = ""
        if tz:
            tz_text = f"{tz}"  
        else:
            tz_text = localizer.format_message('messages.tz_u_timezone2')

        title = localizer.format_message('messages.settings_message_title') 
        
        settings_message = title + settings_notify + notify_text + settings_notify_mute + notify_mute_text + settings_lang + lang_text + settings_tz + tz_text
        return settings_message
    
    #Меню настроек
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id 
        user_lang = await get_user_language(self.db_url, user_id)
        c_notif = await get_user_notify(self.db_url, user_id)
        c_notif_mute = await get_user_notify_mute(self.db_url, user_id)        
        tz = await get_user_timezone(self.db_url, user_id)       
        await self.update_loc(user_id)        
        reply_markup = self.build_settings_keyboard(c_notif_mute, user_lang)  
                 
        settings_message = self.create_settings_message(c_notif, c_notif_mute, user_lang, tz)
        await update.message.reply_text(
            settings_message,
            parse_mode="HTML",  
            reply_markup=reply_markup
        ) 

    #Обработчик кнопки ReplyKeyboard
    async def reply_button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            #удаляет сообщение с текстом кнопки
            await update.message.delete()  
        except:
            pass

        user_id = update.message.from_user.id
        await self.update_loc(user_id)  
        text = update.message.text
        key_on = localizer.format_message('BUTTON_TEXTS.b_notify_on') 
        key_off = localizer.format_message('BUTTON_TEXTS.b_notify_off') 
        r_key_on = [[key_on]] 
        r_key_off = [[key_off]] 
        if text == key_on:
            keyboard = r_key_off          
            await set_user_notify(self.db_url, user_id, True)
            await set_user_notify_mute(self.db_url, user_id, False)
            await self.update_loc(user_id)
            mess = localizer.format_message('messages.shards_notif_on')       
            await update.message.reply_text(
                mess,
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )

        elif text == key_off:
            keyboard = r_key_on
            await set_user_notify(self.db_url, user_id, False)
            await self.update_loc(user_id)
            mess = localizer.format_message('messages.shards_notif_off')
            await update.message.reply_text(
                mess,
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )

    #Обработка кнопок настройки
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        c_notif = await get_user_notify(self.db_url, user_id)
        c_notif_mute = await get_user_notify_mute(self.db_url, user_id)
        await self.update_loc(user_id) 
           
        #Обработка переключателя тихого режима
        if query.data == "toggle_notify_mute":
            if c_notif_mute:
                c_notif_mute = False
                c_notif = True
                await set_user_notify(self.db_url, user_id, c_notif)
                await set_user_notify_mute(self.db_url, user_id, c_notif_mute)
                mess = localizer.format_message('messages.shards_notif_on')
            else:
                c_notif_mute = True
                c_notif = False
                await set_user_notify(self.db_url, user_id, c_notif)
                await set_user_notify_mute(self.db_url, user_id, c_notif_mute)
                mess = localizer.format_message('messages.shards_notif_mute')

            r_key = await self.get_reply_key(user_id) 
            await context.bot.send_message(
                chat_id=user_id,
                text=mess,
                reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
                )

        #Обработка переключателя языка
        elif query.data == "toggle_lang":
            current = await get_user_language(self.db_url, user_id)
            new_lang = 'en' if current == 'ru' else 'ru'
            await set_user_language(self.db_url, user_id, new_lang)

            await self.update_loc(user_id) 

            commands = self.build_bot_commands()
            await self.application.bot.set_my_commands(
                commands=commands,
                scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
            )
            r_key = await self.get_reply_key(user_id) 
            await context.bot.send_message(
                chat_id=user_id,
                text=localizer.format_message('messages.settings_lang'),
                reply_markup=ReplyKeyboardMarkup(r_key, resize_keyboard=True)
                )
        
        #Обработка часового пояса
        elif query.data == "toggle_timezone":
            await query.edit_message_text(
                localizer.format_message('messages.tz_select'), 
                reply_markup=self.build_timezone_keyboard(0)
                )
            await query.answer()
            return

        #Обновление сообщения с настройками
        user_lang = await get_user_language(self.db_url, user_id)
        c_notif = await get_user_notify(self.db_url, user_id)
        c_notif_mute = await get_user_notify_mute(self.db_url, user_id)        
        tz = await get_user_timezone(self.db_url, user_id)
        await self.update_loc(user_id)  
         
        settings_message = self.create_settings_message(c_notif, c_notif_mute, user_lang, tz)

        old_text = query.message.text
        new_text = settings_message
        old_markup = query.message.reply_markup
        new_markup = self.build_settings_keyboard(c_notif_mute, user_lang)  
        if old_text != new_text or old_markup != new_markup:
            await query.edit_message_text(
                text=new_text,
                parse_mode="HTML",
                reply_markup=new_markup
            )
        else:            
            await query.answer()
        #await query.edit_message_text(
        #    settings_message,
        #    parse_mode="HTML",
        #    reply_markup=self.build_settings_keyboard(c_notif_mute, user_lang)  
        #)
        #await query.answer()

# ----------------- TIMEZONE SELECTION -----------------
    def build_timezone_keyboard(
            self, page: int = 0, 
            query: str | None = None
            ) -> InlineKeyboardMarkup:
        #tzs — список строк
        if query:
            q = query.lower()
            tzs = [t for t in ALL_TIMEZONES if q in t.lower()]
        else:
            #при первой странице показываем популярные вверху
            remaining = [t for t in ALL_TIMEZONES if t not in POPULAR_TIMEZONES]
            tzs = POPULAR_TIMEZONES + remaining if page == 0 else remaining

        total = len(tzs)
        pages = math.ceil(total / PER_PAGE) if total > 0 else 1
        page = max(0, min(page, pages - 1))
        start = page * PER_PAGE
        slice_tz = tzs[start:start+PER_PAGE]

        keyboard = []
        for tz in slice_tz:
            keyboard.append([InlineKeyboardButton(tz, callback_data=f"TZ|{tz}")])
         
        nav = []
        if page > 0:
            nav.append(
                InlineKeyboardButton(
                    localizer.format_message('messages.tz_back'), 
                    callback_data=f"TZ_PAGE|{page-1}|{query or ''}"
                )
            )
        if page < pages - 1:
            nav.append(
                InlineKeyboardButton(
                    localizer.format_message('messages.tz_next'), 
                    callback_data=f"TZ_PAGE|{page+1}|{query or ''}"
                )
            )
        nav.append(
            InlineKeyboardButton(
                localizer.format_message('messages.tz_search'), 
                callback_data="TZ_SEARCH"
            )
        )
        keyboard.append(nav)
        keyboard.append([InlineKeyboardButton(
            localizer.format_message('messages.tz_cancel'), 
            callback_data="TZ_CANCEL"
        )])
        return InlineKeyboardMarkup(keyboard)        
   
    async def timezone_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data or ''
        await query.answer()

        if data.startswith("TZ|"):
            tz = data.split("|", 1)[1]
            #сохранить в БД
            await set_user_timezone(self.db_url, query.from_user.id, tz)
            await query.edit_message_text(localizer.format_message('messages.tz_save')+tz)
            return

        if data.startswith("TZ_PAGE|"):
            parts = data.split("|", 2)
            page = int(parts[1])
            q = parts[2] or None
            await query.edit_message_reply_markup(reply_markup=self.build_timezone_keyboard(page, q))
            return

        if data == "TZ_SEARCH":
            #попросим пользователя ввести строку поиска
            await query.edit_message_text(localizer.format_message('messages.tz_set'))
            self.set_user_settings(query.from_user.id, {"awaiting_tz_search": True})
            return

        if data == "TZ_CANCEL":
            await query.edit_message_text(localizer.format_message('messages.tz_cancel2'))
            return

    #Сохраняем/обновляем временные настройки пользователя
    def set_user_settings(self, user_id: int, new_settings: dict):
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id].update(new_settings)
        return

    #Получить или создать временные настройки
    def get_user_settings(self, user_id: int) -> dict:
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        return self.user_settings[user_id]

    #Получить настройки без создания
    def get_existing_user_settings(self, user_id: int) -> dict | None:
        return self.user_settings.get(user_id)
    
    async def handle_text_for_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #обрабатываем как поиск для выбора TZ, если флаг установлен
        if not update.message or not update.effective_user:
            return
        user_id = update.effective_user.id
        text = update.message.text.strip()
        settings = self.get_user_settings(user_id)
        if settings.get("awaiting_tz_search"):
            #сбросим флаг
            settings.pop("awaiting_tz_search", None)
            self.set_user_settings(user_id, settings)
            #покажем результаты поиска
            await update.message.reply_text(
                localizer.format_message('messages.tz_search2'), 
                reply_markup=self.build_timezone_keyboard(0, query=text)
            )
            return
    
    #Сохраняем chat и lang при любом сообщении
    async def save_chat_on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        if user and chat:
            #detect language code from Telegram user (simple mapping)
            lang_code = getattr(user, 'language_code', None)
            simple_lang = None
            if lang_code:
                simple_lang = 'ru' if lang_code.startswith('ru') else 'en'
            await upsert_chat(self.db_url, user.id, chat.id, simple_lang)

    #Обновляем chat_id при callback
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query and query.from_user:
            await upsert_chat(self.db_url, query.from_user.id, query.message.chat.id)
            await query.answer()

# ------------ end class SkyShardsBot--------------------


# -------------------- MAIN -----------------------------
if __name__ == "__main__":

    bot = SkyShardsBot()
    bot.run()   
# -------------------------------------------------------
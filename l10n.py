from typing import Dict, Any
from enum import Enum

class lang(Enum):
    RU = "ru"
    EN = "en"

TRANSLATIONS = {
    "ru": {
        #Типы памяти
        "memory_types": ['Медуза', 'Краб', 'Манта', 'Криль', 'Кит', 'Старейшина'],
        
        "ordinals": ['Первый осколок', 'Второй осколок', 'Последний осколок'],
        
        #Названия областей
        "realm_names": {
            'prairie': 'Полуденная прерия',
            'forest': 'Тайный лес', 
            'valley': 'Долина Триумфа',
            'wasteland': 'Золотая Пустошь',
            'vault': 'Хранилище Знаний'
        },

        #Названия областей2
        "realm_names_2": {
            'prairie': 'Полуденную прерию',
            'forest': 'Тайный лес', 
            'valley': 'Долину Триумфа',
            'wasteland': 'Золотую Пустошь',
            'vault': 'Хранилище Знаний'
        },
        
        #Названия карт
        "map_names": {
            'prairie.butterfly': 'на Поле Бабочек',
            'prairie.village': 'в деревне Прерии',
            'prairie.cave': 'в пещере',
            'prairie.bird': 'в птичьих гнездах',
            'prairie.island': 'на Островах укрытия',
            'forest.brook': 'у лесного ручья',
            'forest.boneyard': 'рядом со сломанным мостом',
            'forest.end': 'в Лесном саду при храме',
            'forest.tree': 'рядом с Домиком на дереве',
            'forest.sunny': 'на Высокой поляне',
            'valley.rink': 'на катке',
            'valley.dreams': 'в Деревушке мечтаний',
            'valley.hermit': 'в Долине отшельника',
            'wasteland.temple': 'рядом с разрушенным храмом',
            'wasteland.battlefield': 'на Поле боя',
            'wasteland.graveyard': 'на Кладбище',
            'wasteland.crab': 'рядом с местом крушения',
            'wasteland.ark': 'рядом с Забытым ковчегом',
            'vault.starlight': 'в Звёздной пустыне',
            'vault.jelly': 'в Бухте Медуз'
        },
        
        #Типы осколков
        "shard_types": {
            "red": "<b>✦ Красный осколок</b>",
            "black": "<b>✦ Черный осколок</b>"
        },
        
        #Текстовые сообщения
        "messages": {
            "hello_message": "Привет! Я буду присылать уведомление о появлении осколков в игре Sky: Children of the Light",
            "p_no_shard": "Сегодня нет осколков",
            "darkness_fell": "✦ Тьма опустилась на ",
            "darkness_fell_last": "<i>(осколки скоро исчезнут)</i>",
            "reward_red": "<b>Награда</b>: {amount} Вознесённые свечи",
            "reward_black": "<b>Награда</b>: 4 тортика свечей",
            "timezone_info": "<i>Время указано для часового пояса: {timezone}</i>",
            "shards_notif_on": "Уведомления об осколках включены",
            "shards_notif_off": "Уведомления об осколках на сегодня остановлены",
            "shards_notif_mute": "Все уведомления отключены",
            "settings_timezone": "Установить часовой пояс",
            "settings_n_on": "♥ Вкл", #❤🕓⏰ 🖤♥ ❤
            "settings_n_off": "💤 Выкл",
            "settings_n_mute": "🔔✨ Mute",#🕯💡🌟 ✨☀️🔅🔆
            "settings_n_mute_on": "🔕 Mute",
            
            #"settings_message": "<b>✦ Настройки ✦</b>\n\n"
            #                    "➜ Уведомления на сегодня (вкл/выкл)\n"
            #                    "➜ Тихий режим\n"
            #                    "➜ Сменить язык (ru/en)\n"
            #                    "➜ Установить часовой пояс",                                
            "settings_message_title":"<b>✦ Настройки ✦</b>\n\n",
            "settings_message_notify":"➜ Уведомления на сегодня ",
            "settings_message_notify_on":"(вкл)   \n",
            "settings_message_notify_off":"(выкл)\n",
            "settings_message_mute":"➜ Тихий режим ",
            "settings_message_mute_on":"(вкл)\n",
            "settings_message_mute_off":"(выкл)\n",
            "settings_message_lang":"➜ Сменить язык ",
            "settings_message_lang_ru":"(ru)\n",
            "settings_message_lang_en":"(en)\n",
            "settings_message_timezone":"➜ Часовой пояс ",

            "settings_lang": "Язык переключен с EN → RU",
            "tz_select":"Выберите часовой пояс:",
            "tz_u_timezone1":"Ваш часовой пояс",
            "tz_u_timezone2":"не задан",
            "tz_back":"‹ Назад",
            "tz_next":"Вперед ›",
            "tz_search":"Поиск",
            "tz_cancel":"Отмена",
            "tz_save":"Часовой пояс сохранен: ",
            "tz_set":"Введите часть названия часового пояса или города (например, 'Los_Angeles' или 'Europe'):",
            "tz_cancel2":"Выбор отменен",
            "tz_search2":"Результаты поиска:"
        },

        #Пункты меню
        "menu": {
            "m_start": "Запустить бота",   
            "m_info": "Информация о текущих Осколках",  
            "m_settings": "Настройки",
            "m_help": "Помощь",
            "m_about": "О программе"        
        },
        
        #Помощник
        "help_message": 
            "<b>✦ Доступные команды ✦</b>\n\n"
            "<b>/start</b> — запуск бота\n"
            "<b>/notify_on</b> — вкл уведомления\n"
            "<b>/notify_off</b> — откл увед. на сегодня\n"
            "<b>/notify_mute</b> — тихий режим\n"
            "<b>/change_language</b> — сменить язык\n"
            "<b>/set_timezone</b> — указать часовой пояс\n"
            "<b>/info</b> — инф о текущих осколках\n"
            "<b>/settings</b> — настройки\n"
            "<b>/help</b> — помощь\n"
            "<b>/about</b> — о программе"
        ,        
        #О программе
        "about_message": 
        "<b>Sky Shards bot</b>\n\n"
            "Вычисляет цвет, время и местоположение <b>Извержения Осколков</b> в игре “Sky: Children of the Light”\n"
            "Бот отправляет уведомления в момент начала падения осколков, помогая быть в курсе событий и успевать реагировать\n\n"
            'Информация основана на вычислениях в веб-приложения <b><a href="https://sky-shards.pages.dev/">Sky Shards</a></b>\n\n'
            "✦✦✦✦✦✦✦✦✦✦✦✦✦\n\n"
            "<b>Бот отправляет два вида уведомлений:</b>\n"
            "• ежедневные уведомления о текущих Осколках в момент обновления дня в Sky\n"
            "• уведомление во время начала Извержения Осколков и за 30 минут до окончания события\n\n"
            "В меню “Настройки” вы можете отключить уведомления на сегодняшний день или включить Тихий режим, "
            "при котором все уведомления от бота будут отключены. Здесь также можно изменить язык и установить часовой пояс\n\n"
            "При первом запуске рекомендуется выбрать локальный часовой пояс для корректной работы уведомлений\n\n"
            "_______\n\n"
            "<i>Бот создан исключительно в информационно-ознакомительных и развлекательных целях</i>\n\n"
            "<i>Данное приложение не связано с ThatGameCompany и Sky: Дети Света</i>\n\n"
            'Разработчик: <b>maratremere</b>\n<b><a href="https://github.com/maratremere/SkyShards_bot">Исходники на GitHub</a></b>'
         
    },
    
    "en": {
        #Memory types
        "memory_types": ['Jellyfish', 'Crab', 'Manta', 'Krill', 'Whale', 'Elder'],
        
        #Ordinals for shards
        "ordinals": ['First shard', 'Second shard', 'Last shard'],
        
        #Realm names
        "realm_names": {
            'prairie': 'Daylight Prairie',
            'forest': 'Hidden Forest', 
            'valley': 'Valley of Triumph',
            'wasteland': 'Golden Wasteland',
            'vault': 'Vault of Knowledge'
        },
        #Названия областей2
        "realm_names_2": {
            'prairie': 'Daylight Prairie',
            'forest': 'Hidden Forest', 
            'valley': 'Valley of Triumph',
            'wasteland': 'Golden Wasteland',
            'vault': 'Vault of Knowledge'
        },
        
        #Map names
        "map_names": {
            'prairie.butterfly': 'Butterfly Fields',
            'prairie.village': 'Village Islands',
            'prairie.cave': 'Cave',
            'prairie.bird': 'Bird Nest',
            'prairie.island': 'Sanctuary Islands',
            'forest.brook': 'Brook',
            'forest.boneyard': 'Boneyard',
            'forest.end': 'Forest Garden',
            'forest.tree': 'Treehouse',
            'forest.sunny': 'Elevated Clearing',
            'valley.rink': 'Ice Rink',
            'valley.dreams': 'Village of Dreams',
            'valley.hermit': 'Hermit Valley',
            'wasteland.temple': 'Broken Temple',
            'wasteland.battlefield': 'Battlefield',
            'wasteland.graveyard': 'Graveyard',
            'wasteland.crab': 'Crab Fields',
            'wasteland.ark': 'Forgotten Ark',
            'vault.starlight': 'Starlight Desert',
            'vault.jelly': 'Jellyfish Cove'
        },
        
        #Shard types
        "shard_types": {
            "red": "<b>✦ Red shard</b>",
            "black": "<b>✦ Black shard</b>"
        },
        
        #Text messages
        "messages": {
            "hello_message": "Hello! I will send you notifications about Shard Eruptions in the game Sky: Children of the Light",
            "p_no_shard": "No shards today",
            "darkness_fell": "✦ Darkness has fallen upon ",
            "darkness_fell_last": "<i>(the shards will soon disappear)</i>",
            "reward_red": "<b>Reward</b>: {amount} Ascended Candles",
            "reward_black": "<b>Reward</b>: 4 Candle Cake",
            "timezone_info": "<i>Time shown in local timezone: {timezone}</i>",
            "shards_notif_on": "Shard notifications are enabled",
            "shards_notif_off": "Shard notifications are disabled for today",
            "shards_notif_mute": "All notifications are disabled",
            "settings_timezone": "Set Timezone",
            "settings_n_on": "⏰ On",
            "settings_n_off": "💤 Off",
            "settings_n_mute": "🔔✨ Mute",
            "settings_n_mute_on": "🔕 Mute",

            #"settings_message": "<b>✦ Settings ✦</b>\n\n"
            #                    "➜ Notifications for today (on/off)\n"
            #                    "➜ Silent mode\n"
            #                    "➜ Change language (ru/en)\n"
            #                    "➜ Set Timezone",                                
            "settings_message_title":"<b>✦ Settings ✦</b>\n\n",
            "settings_message_notify":"➜ Notifications for today ",
            "settings_message_notify_on":"(on)             \n",
            "settings_message_notify_off":"(off)            \n",
            "settings_message_mute":"➜ Silent mode ",
            "settings_message_mute_on":"(on)\n",
            "settings_message_mute_off":"(off)\n",
            "settings_message_lang":"➜ Change language ",
            "settings_message_lang_ru":"(ru)\n",
            "settings_message_lang_en":"(en)\n",
            "settings_message_timezone":"➜ Timezone ",

            "settings_lang": "Language switched from RU → EN",
            "tz_select" : "Select timezone:",
            "tz_u_timezone1" : "Your timezone",
            "tz_u_timezone2" : "not set",
            "tz_back":"‹ Back",
            "tz_next":"Next ›",
            "tz_search":"Search",
            "tz_cancel":"Cancel",
            "tz_save":"Timezone saved: ",
            "tz_set":"Please enter part of a time zone or city name (e.g. 'Los_Angeles' or 'Europe'):",
            "tz_cancel2":"Select cancelled",
            "tz_search2":"Search results:"
        },

        #Menu  items
        "menu": {   
            "m_start": "Start bot",   
            "m_info": "Info about today's Shards",  
            "m_settings": "Settings",
            "m_help": "Help",
            "m_about": "About"         
        },
        
        #Assistant
        "help_message": 
            "<b>✦ Available commands ✦</b>\n\n"
            "<b>/start</b> — launch the bot\n"
            "<b>/notify_on</b> — enable notifications\n"
            "<b>/notify_off</b> — disable notifications for today\n"  
            "<b>/notify_mute</b> — silent mode\n"         
            "<b>/change_language</b>— change language\n"
            "<b>/set_timezone</b> — specify timezone\n"
            "<b>/info</b> — information about today's shards\n"
            "<b>/settings</b> — settings\n"
            "<b>/help</b> — available commands\n"
            "<b>/about</b> — about"
        ,
        
        #About
        "about_message": 
            "<b>Sky Shards Bot</b>\n\n"
            "Calculates the color, timing and location of <b>Shard Eruptions</b> in the game “Sky: Children of the Light“\n"
            "Sends notifications when shards begin to fall, helping stay informed and prepared\n\n"
            'Information is based on calculations from the web app <b><a href="https://sky-shards.pages.dev/">Sky Shards</a></b>\n\n'
            "✦✦✦✦✦✦✦✦✦✦✦✦✦\n\n"
            "<b>The bot sends two types of notifications:</b>\n"
            "• daily notifications about Shards at the start of the new Sky day\n"
            "• notifications when a Shard Eruption begins, and another one 30 minutes before the event ends\n\n"
            "In the “Settings” menu, you can disable notifications for today or enable Silent Mode, "
            "which turns off all notifications from the bot. You can also change the language and set the time zone here\n\n"
            "It is recommended to select your local time zone on the first launch to ensure correct notification times\n\n"
            "_______\n\n"            
            "<i>This bot was created solely for informational, educational, and entertainment purposes</i>\n\n"
            "<i>This application is not affiliated with ThatGameCompany or Sky: Children of the Light</i>\n\n"
            'Developer: <b>maratremere</b>\n<b><a href=\"https://github.com/maratremere/SkyShards_bot">Source on GitHub</a></b>'
        
    }
}

class Localizer:    
    def __init__(self, language: lang = lang.RU):
        self._language = language
        self._translations = TRANSLATIONS[language.value]
        self._initialized = False
    
    def initialize(self, language: lang):
        #обновляем язык и словарь
        self._language = language
        self._translations = TRANSLATIONS[language.value]
        self._initialized = True
    
    @property
    def language(self) -> lang:
        return self._language
    
    @property
    def translations(self) -> Dict[str, Any]:
        return self._translations
    
    def get(self, key: str, default: str = "") -> Any:
        keys = key.split('.')
        value = self._translations
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def format_message(self, key: str, **kwargs) -> str:
        message = self.get(key, key)
        try:
            return message.format(**kwargs)
        except (KeyError, AttributeError):
            return message
        
    def get_ordinal(self, index: int) -> str:
        ordinals = self.get('ordinals', [])
        if index < len(ordinals):
            return ordinals[index]
        #return f"Shard {index + 1}" if self._language == lang.EN else f"Осколок {index + 1}"
        return 
    
    def get_realm_name(self, realm_key: str) -> str:
        return self.get(f'realm_names.{realm_key}', realm_key)
    
    def get_realm_name2(self, realm_key: str) -> str:
        return self.get(f'realm_names_2.{realm_key}', realm_key)

    def get_map_name(self, map_key: str) -> str:
        maps = self.get('map_names', {})
        result = maps.get(map_key, map_key)  
        return result
    
    def get_shard_type(self, is_red: bool) -> str:
        shard_key = "red" if is_red else "black"
        return self.get(f'shard_types.{shard_key}', shard_key)

#Глобальный экземпляр локализатора
localizer = Localizer()

def init_localizer(language: lang):
    global localizer
    localizer.initialize(language)

def get_localizer() -> Localizer:
    return localizer
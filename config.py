#Конфигурация и переменные окружения

import os
from dotenv import load_dotenv

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
import pytz
import logging

# ----------------- TG BOT -----------------
#Загружаем переменные окружения (.env)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Please specify it in the .env file.")
DB_FILE = "core/bot.db"

#Популярные таймзоны
POPULAR_TIMEZONES = [
    'UTC',
    'Europe/London',    
    'Europe/Moscow',
    'America/Los_Angeles',
    'America/New_York',
    'Asia/Tokyo',
    'Asia/Tbilisi',
    'Australia/Sydney'
]

PER_PAGE = 8
ALL_TIMEZONES = pytz.common_timezones


# ----------------- SHARDS -----------------
#Константы для расчета времени событий
LAND_OFFSET = timedelta(minutes=8, seconds=40)  #время после начала до приземления
END_OFFSET = timedelta(hours=4)  #время после начала до окончания
BLACK_SHARD_INTERVAL = timedelta(hours=8)  #интервал между черными осколками
RED_SHARD_INTERVAL = timedelta(hours=6)  #интервал между красными осколками
TIMEZONE = 'America/Los_Angeles'  #Часовой пояс игры
#LOCAL_TIMEZONE = 'Asia/Tbilisi'  #Мой часовой пояс
LOCAL_TIMEZONE = 'Europe/Moscow'
REALMS = ['prairie', 'forest', 'valley', 'wasteland', 'vault'] #названия локаций

class ShardType(Enum):
    BLACK = "black"
    RED = "red"

@dataclass
class ShardOccurrence:
    #Представляет одно появление осколка с временными метками
    start: datetime  #время начала события
    land: datetime   #время приземления осколка
    end: datetime    #время окончания события

@dataclass
class DailyConfig:
    #Конфигурация для конкретного дня
    memory: Optional[int] = None
    memory_by: Optional[str] = None
    variation: Optional[int] = None
    variation_by: Optional[str] = None
    version: Optional[int] = None
    last_modified: Optional[datetime] = None

@dataclass
class ShardConfig:
    #Конфигурация для определенного типа осколков
    no_shard_weekdays: List[int]  #дни недели без осколков (1=пн, 7=вс)
    offset: timedelta  #смещение от начала дня
    interval: timedelta  #интервал между появлениями
    maps: List[str]  #карты для каждой области
    default_reward_ac: Optional[float] = None  #награда по умолчанию(свечи эдема)(Ascended Candles)

@dataclass
class ShardInfo:
    #Полная информация об осколках на определенную дату
    date: datetime
    is_red: bool
    has_shard: bool
    offset: timedelta
    interval: timedelta
    last_end: datetime
    realm: str
    map_name: str
    num_variant: int
    reward_ac: Optional[float]
    occurrences: List[ShardOccurrence]

#Конфигурации для разных групп осколков
SHARDS_INFO = [
    #Группа 0: Черные осколки (сб-вс без осколков)
    ShardConfig(
        no_shard_weekdays=[6, 7],  # сб, вс
        interval=BLACK_SHARD_INTERVAL,
        offset=timedelta(hours=1, minutes=50),
        maps=['prairie.butterfly', 'forest.brook', 'valley.rink', 'wasteland.temple', 'vault.starlight'],
    ),
    #Группа 1: Черные осколки (вс-пн без осколков)
    ShardConfig(
        no_shard_weekdays=[7, 1],  # вс, пн
        interval=BLACK_SHARD_INTERVAL,
        offset=timedelta(hours=2, minutes=10),
        maps=['prairie.village', 'forest.boneyard', 'valley.rink', 'wasteland.battlefield', 'vault.starlight'],
    ),
    #Группа 2: Красные осколки (пн-вт без осколков)
    ShardConfig(
        no_shard_weekdays=[1, 2],  # пн, вт
        interval=RED_SHARD_INTERVAL,
        offset=timedelta(hours=7, minutes=40),
        maps=['prairie.cave', 'forest.end', 'valley.dreams', 'wasteland.graveyard', 'vault.jelly'],
        default_reward_ac=2.0,
    ),
    #Группа 3: Красные осколки (вт-ср без осколков)
    ShardConfig(
        no_shard_weekdays=[2, 3],  # вт, ср
        interval=RED_SHARD_INTERVAL,
        offset=timedelta(hours=2, minutes=20),
        maps=['prairie.bird', 'forest.tree', 'valley.dreams', 'wasteland.crab', 'vault.jelly'],
        default_reward_ac=2.5,
    ),
    #Группа 4: Красные осколки (ср-чт без осколков)
    ShardConfig(
        no_shard_weekdays=[3, 4],  # ср, чт
        interval=RED_SHARD_INTERVAL,
        offset=timedelta(hours=3, minutes=30),
        maps=['prairie.island', 'forest.sunny', 'valley.hermit', 'wasteland.ark', 'vault.jelly'],
        default_reward_ac=3.5,
    ),
]

#Переопределение наград для специальных карт
OVERRIDE_REWARD_AC = {
    'forest.end': 2.5,
    'valley.dreams': 2.5,
    'forest.tree': 3.5,
    'vault.jelly': 3.5,
}

#Количество вариантов для каждой карты
NUM_MAP_VARIANTS = {
    'prairie.butterfly': 3,
    'prairie.village': 3,
    'prairie.bird': 2,
    'prairie.island': 3,
    'forest.brook': 2,
    'forest.end': 2,
    'valley.rink': 3,
    'valley.dreams': 2,
    'wasteland.temple': 3,
    'wasteland.battlefield': 3,
    'wasteland.graveyard': 2,
    'wasteland.crab': 2,
    'wasteland.ark': 4,
    'vault.starlight': 3,
    'vault.jelly': 2,
}

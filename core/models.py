from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Literal
from config import (
    ShardInfo, ShardOccurrence, 
    TIMEZONE, LOCAL_TIMEZONE, 
    SHARDS_INFO, OVERRIDE_REWARD_AC, 
    NUM_MAP_VARIANTS, LAND_OFFSET, 
    END_OFFSET, REALMS
)
from l10n import lang, localizer
import pytz

# ----------------ShardInfoPrint-------------------------
#Основной класс для отображения информации об осколках.    
class ShardInfoPrint:
    #Инициализация компонента информации об осколках.     
    def __init__(self, info: ShardInfo, timezone: str | None = LOCAL_TIMEZONE):             
        self.info = info        
        self.loc = localizer
        self.tz = timezone

    #Форматирует информацию о наградах за осколки
    def _format_shard_rewards(self) -> str:    
        if self.info.is_red:
            #Красные осколки дают вознесенные свечи
            ac_amount = self.info.reward_ac or 0           
            reward_text = self.loc.format_message('messages.reward_red', amount=ac_amount)
            return reward_text
        else:
            #Черные осколки дают тортики свечей
            return self.loc.get('messages.reward_black')
        
    #Форматирует времена появления осколков в локальной временной зоне.
    def _format_shard_times(self) -> List[str]:    
        time_strings = []        
        l_tz = pytz.timezone(self.tz)
        local_tz = datetime.now(l_tz).tzinfo        
        for i, occurrence in enumerate(self.info.occurrences):
            ordinal = self.loc.get_ordinal(i)            
            #Конвертируем время в локальную временную зону
            land_time_local = occurrence.land.astimezone(local_tz).strftime('%H:%M')
            end_time_local = occurrence.end.astimezone(local_tz).strftime('%H:%M')            
            time_strings.append(f"• {ordinal}:   {land_time_local} - {end_time_local}")
            
        return time_strings
    
    #Сообщение об отсутствии осколков
    def _render_no_shard(self) -> str:       
        return self.loc.format_message('messages.p_no_shard')
    
    #Информация о дне с осколками.
    def _render_with_shard(self) -> str:  
        shard_type = self.loc.get_shard_type(self.info.is_red)
        realm_name = self.loc.get_realm_name(self.info.realm)
        map_name = self.loc.get_map_name(self.info.map_name)
        #date_str = self.info.date.strftime('%d.%m.%Y')                
        main_info = f"{shard_type} {map_name} ({realm_name})"
        if self.loc.language == lang.EN:
            main_info = f"{shard_type} in {map_name} ({realm_name})"
        
        #Добавляем информацию о наградах
        rewards_info = self._format_shard_rewards()        
        #Добавляем расписание
        times_info = self._format_shard_times()
        times_str = "\n".join(times_info)        
        #local_tz_name = self.tz
        #timezone_info = self.loc.format_message('messages.timezone_info', timezone=local_tz_name)
        #main_text = f"{main_info}\n{rewards_info}\n\n{times_str}"
        result_parts = [main_info, rewards_info, times_str]
        #result_parts = [main_info, rewards_info, times_str, timezone_info+' (<i>'+date_str+')</i>']
        return "\n\n".join(result_parts)
        #return main_text
    
    #Выводит полную информацию об осколках большим сообщением
    def render(self) -> str:           
        if not self.info.has_shard:
            return self._render_no_shard()
        else:
            return self._render_with_shard()

    #Форматирует информацию о наградах за осколки
    def _shard_rewards(self) -> str:           
        if self.info.is_red:
            #Красные осколки дают вознесенные свечи
            ac_amount = self.info.reward_ac or 0
            return self.loc.format_message('messages.reward_red', amount=ac_amount)
        else:
            #Черные осколки дают тортики свечей
            return self.loc.get('messages.reward_black')
    
    #Выводит информацию об осколках
    def _print_shards(self) -> str:                 
        shard_type = self.loc.get_shard_type(self.info.is_red)
        realm_name = self.loc.get_realm_name(self.info.realm)
        map_name = self.loc.get_map_name(self.info.map_name)   
        main_info = f"{shard_type} {map_name} ({realm_name})"
        if self.loc.language == lang.EN:
            main_info = f"{shard_type} in {map_name} ({realm_name})"        
        #Добавляем информацию о наградах
        rewards_info = self._shard_rewards()
        result = [main_info, rewards_info]                   
        return "\n".join(result)
    
    #Выводит какие и где сегодня осколки, при старте
    def print_today_shard(self) -> str:     
        if not self.info.has_shard:
            return self._render_no_shard()
        else:
            return self._print_shards()
    
    #Форматирует информацию о наградах
    def _format_morning_shard_rewards(self) -> str:    
        if self.info.is_red:
            ac_amount = self.info.reward_ac or 0           
            reward_text = self.loc.format_message('messages.reward_m_red', amount=ac_amount)
            return reward_text
        else:
            return self.loc.format_message('messages.reward_m_black')
        
    #Форматирует времена появления утренних осколков
    def _format_morning_shard_times(self) -> List[str]:    
        time_strings = []        
        l_tz = pytz.timezone(self.tz)
        local_tz = datetime.now(l_tz).tzinfo        
        for i, occurrence in enumerate(self.info.occurrences): # • • • - – — ✦            
            land = occurrence.land.astimezone(local_tz).strftime('%H:%M')
            end = occurrence.end.astimezone(local_tz).strftime('%H:%M')            
            time_strings.append(f"{land}-{end}")            
        return time_strings
    
    #Информация о дне с осколками
    def _print_morning_shards(self) -> str:  
        shard_type = self.loc.get_shard_type(self.info.is_red)
        realm_name = self.loc.get_realm_name(self.info.realm)
        map_name = self.loc.get_map_name(self.info.map_name)

        main_info = f"{shard_type} {map_name} ({realm_name})"
        if self.loc.language == lang.EN:
            main_info = f"{shard_type} in {map_name} ({realm_name})"

        rewards_info = self._format_morning_shard_rewards() 
        times_info = self._format_morning_shard_times()
        times_str = " | ".join(times_info)               

        main_text = f"{main_info}   {rewards_info}\n{times_str}"

        return main_text

    #Выводит утреннее сообщение
    def print_morning_shard(self) -> str:     
        if not self.info.has_shard:
            return self._render_no_shard()
        else:
            return self._print_morning_shards()
# -------------------------------------------------------

# ----------------- FUNCTIONS -----------------
#Главная функция для получения информации об осколках на определенную дату
def get_shard_info(date: datetime) -> ShardInfo:   
    #Args:date: дата для которой нужно получить информацию  
    #Returns:ShardInfo: полная информация об осколках на указанную дату    
    #Конвертируем дату в тихоокеанский часовой пояс и обрезаем до начала дня
    sky_timezone = pytz.timezone(TIMEZONE)
    today = date.astimezone(sky_timezone).replace(hour=0, minute=0, second=0, microsecond=0)
    
    #Получаем день месяца и день недели
    day_of_month = today.day
    day_of_week = today.isoweekday()  # 1=пн, 7=вс
    
    #Определяем тип осколка (красный/черный) на основе четности дня месяца
    is_red = day_of_month % 2 == 1
    
    #Определяем индекс области (0-4 для prairie, forest, valley, wasteland, vault)
    realm_idx = (day_of_month - 1) % 5
    
    #Определяем индекс группы конфигурации осколков
    #Для красных осколков (нечетные дни): группы 2, 3, 4
    #Для черных осколков (четные дни): группы 0, 1
    if day_of_month % 2 == 1:
        info_index = (((day_of_month - 1) // 2) % 3) + 2
    else:
        info_index = (day_of_month // 2) % 2
    
    #Получаем конфигурацию для данной группы
    shard_config = SHARDS_INFO[info_index]
    
    #Проверяем, есть ли осколки в этот день
    has_shard = day_of_week not in shard_config.no_shard_weekdays
    
    #Определяем карту
    map_name = shard_config.maps[realm_idx]
    
    #Определяем награду для красных осколков
    reward_ac = None
    if is_red:
        reward_ac = (OVERRIDE_REWARD_AC.get(map_name) or 
                    shard_config.default_reward_ac)
    
    #Получаем количество вариантов карты
    num_variant = NUM_MAP_VARIANTS.get(map_name, 1)
    
    # Вычисляем время первого появления
    first_start = today + shard_config.offset
    
    #Обработка перехода на летнее/зимнее время (происходит в воскресенье)
    #if day_of_week == 7:        
    #    pass
    
    #Создаем список всех появлений осколков (обычно 3 раза в день)
    occurrences = []
    for i in range(3):
        start = first_start + (shard_config.interval * i)
        land = start + LAND_OFFSET
        end = start + END_OFFSET
        occurrences.append(ShardOccurrence(start=start, land=land, end=end))
    
    return ShardInfo(
        date=date,
        is_red=is_red,
        has_shard=has_shard,
        offset=shard_config.offset,
        interval=shard_config.interval,
        last_end=occurrences[2].end,
        realm=REALMS[realm_idx],
        map_name=map_name,
        num_variant=num_variant,
        reward_ac=reward_ac,
        occurrences=occurrences
    )

#Находит список времени начала осколков
def get_shard_times_land(info: ShardInfo, timezone: str | None = LOCAL_TIMEZONE) -> List[datetime]:
    l_tz = pytz.timezone(timezone)
    local_tz = datetime.now(l_tz).tzinfo
    times = []
    for occurrence in info.occurrences:
        times.append(occurrence.land.astimezone(local_tz))
    return times

#Находит список времени окончания осколков
def get_shard_times_end(info: ShardInfo, timezone: str | None = LOCAL_TIMEZONE) -> List[datetime]:
    #local_tz = datetime.now().astimezone().tzinfo
    l_tz = pytz.timezone(timezone)
    local_tz = datetime.now(l_tz).tzinfo
    times = []
    for occurrence in info.occurrences:
        times.append(occurrence.end.astimezone(local_tz) - timedelta(minutes=30))
    return times

#Находит следующий день с осколками, начиная с указанной даты.
def find_next_shard(from_date: datetime, only: Optional[Literal['black', 'red']] = None) -> ShardInfo:        
    #from_date: дата начала поиска
    #only: искать только определенный тип осколков ('black' или 'red')    
    #Returns: ShardInfo: информация о следующем дне с осколками

    info = get_shard_info(from_date)    
    #Проверяем, есть ли осколки в текущий день
    current_time = datetime.now(pytz.timezone(TIMEZONE))    
    #Если есть осколки сегодня, текущее время до окончания последнего осколка,
    #и тип осколка соответствует требованиям (или требования не заданы)
    if (info.has_shard and 
        current_time < info.last_end and 
        (only is None or (only == 'red') == info.is_red)):
        return info
    else:
        #Ищем в следующем дне с указанной даты.
        next_date = from_date + timedelta(days=1)
        return find_next_shard(next_date, only)
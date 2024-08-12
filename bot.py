import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from config_data.config import Config, load_config
from handlers import base_handlers, other_handlers
from services.services import Services, TimerScheduler

logger = logging.getLogger(__name__)

async def main():

    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot')

    config: Config = load_config()

    storage: MemoryStorage = MemoryStorage()

    bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(other_handlers.router)
    dp.include_router(base_handlers.router)
    
    services = Services(bot=bot, chat_id=1043670115)
    timer_scheduler = TimerScheduler(services)
    timer_scheduler.schedule_tasks()

    await bot.delete_webhook(drop_pending_updates=True) #убрать в продакшене
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')

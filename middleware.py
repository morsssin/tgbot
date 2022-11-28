from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.handler import SkipHandler, CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import DEFAULT_RATE_LIMIT, FSMContext, Dispatcher
from aiogram import types




class Middleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    @staticmethod
    async def on_process_message(message: types.Message, data: dict):
        chat_id = message.chat.id

        # state: FSMContext = data["state"]
        print(f"[MESSAGE] {message.chat.full_name} {message.from_user.mention} - {message.text}")
        
    # async def __call__(self, 
    #                    handler: types.Callable[[types.Message, types.Dict[str, types.Any]], types.Awaitable[types.Any]],
    #                    event: types.Message,
    #                    data: types.Dict[str, types.Any]) -> types.Any:
    #     print(f"[MESSAGE] {message.chat.full_name} {message.from_user.mention} - {message.text}")
    #     self.counter += 1
    #     data['counter'] = self.counter
    #     return await handler(event, data)

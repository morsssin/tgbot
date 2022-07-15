# -*- coding: utf-8 -*-


from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


from aiogram.utils.markdown import text, hbold

import states as st
import keyboards as kb

from config import LEN_TASKS, URL, LOGIN, PASS, DEBUG_MODE
from app import dp, bot

from test_db import test_DB, full_list


### выполненные работы
async def add_work_done (call: types.CallbackQuery(),  state: FSMContext):
    await call.message.answer('Выберите вариант для поиска', reply_markup=kb.add_work_done_kb)
    await st.ToolsStates.find_work_done.set()

async def search_handler(query: types.InlineQuery, state: FSMContext):  
    
    if query.query.split(':')[0] == 'tasks':
        result_list = search_in_list(tdb.works_list, query.query.split(':')[1])

        
    elif query.query.split(':')[0] == 'tools':
        result_list = search_in_list(tdb.tools_list, query.query.split(':')[1])

    articles = [types.InlineQueryResultArticle(id=idx,
                                               title=item,
                                               input_message_content=types.InputTextMessageContent(message_text="%s" % item),
                                               reply_markup = kb.accept_work_done_kb
    ) for idx, item in enumerate(result_list)]
    await query.answer(articles, cache_time=60, is_personal=True)
        
      
async def save_work_done(call: types.CallbackQuery,  state: FSMContext):
    if call.data.split('_')[1] == 'accepted':
        await bot.answer_callback_query(call.id, text='Вариант добавлен', show_alert=True)
                  
    elif call.data.split('_')[1] == 'declined':   
        await bot.answer_callback_query(call.id, text='Вариант отклонен', show_alert=True)
        

def reg_handlers_client(dp : Dispatcher):

    #  ### добавить фото/видео
    # dp.register_callback_query_handler(del_comment,  Text(startswith="cancel_b"), state=st.CommentStates.add_comment)

    ### выполненные работы
    dp.register_callback_query_handler(add_work_done, Text(startswith="todowork"), state="*")
    dp.register_inline_handler(search_handler, state=st.ToolsStates.find_work_done)
    dp.register_callback_query_handler(save_work_done, Text(startswith="work_"), state=st.ToolsStates.find_work_done)


    # ### свернуть задачу
    # dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"))
    # dp.register_callback_query_handler(hide_message,Text(startswith="hide_message"), state=st.ToolsStates.find_work_done) 

    # ### выбрать вариант
    # dp.register_callback_query_handler(state_var, Text(startswith="varb_")) 
    # dp.register_callback_query_handler(state_var_accept, Text(startswith="accept_b"))
    
 
    # dp.register_callback_query_handler(show_options, Text(startswith="show_"))
    # dp.register_callback_query_handler(back_vars, Text(startswith="backvar"))

    
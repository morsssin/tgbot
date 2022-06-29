# -*- coding: utf-8 -*-



def search_in_list (list_: list, val: str):
    list_res = []
    for item in list_:
        if val.lower() in item.lower():
            list_res.append(item)
    return list_res


def get_key(dict_, value):
    for k, v in dict_.items():
        if v == value:
            return k
        
        
async def del_message(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=call.from_user.id, message_id=
    
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await state.reset_state(with_data=False) 


### свернуть задачу
async def hide_message(call: types.CallbackQuery,  state: FSMContext):
    
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

async def mes_to_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mes_id = data.get('mes_to_del')
    try:
        await message.delete()
        await bot.delete_message(chat_id=message.chat.id, message_id=mes_id)
    except:
        pass
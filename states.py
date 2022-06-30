# -*- coding: utf-8 -*-
from aiogram.dispatcher.filters.state import State, StatesGroup

class AuthStates(StatesGroup):
    auth_login_st = State()
    login_entered_st = State()


class CommentStates(StatesGroup):
    add_comment = State()
    
        
class ToolsStates(StatesGroup):
    find_work_done = State()
    save_work_done = State()


class UploadFileState(StatesGroup):
    add_file = State()

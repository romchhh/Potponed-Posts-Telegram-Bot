from aiogram.dispatcher.filters.state import State, StatesGroup

class AddChannelState(StatesGroup):
    waiting_for_channel = State()
      
class Form(StatesGroup):
    content = State()
    media = State()
    description = State()
    url_buttons = State()
    schedule_post = State() 
    
class EditPostState(StatesGroup):
    waiting_for_post = State()
    waiting_for_new_text = State()
    waiting_for_new_buttons = State()
    
class SheduleForm(StatesGroup):
    content = State()
    media = State()
    description = State()
    url_buttons = State()
    schedule_post = State() 
    
class Template(StatesGroup):
    content = State()
    media = State()
    description = State()
    url_buttons = State()
    schedule_post = State() 

class PublishTemplate(StatesGroup):
    content = State()
    media = State()
    description = State()
    url_buttons = State()
    schedule_post = State() 

class ChangeTemplate(StatesGroup):
    content = State()
    media = State()
    description = State()
    url_buttons = State()
    schedule_post = State() 
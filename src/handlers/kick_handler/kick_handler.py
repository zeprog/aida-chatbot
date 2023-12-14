import re
import json
from src.models import User
from src.config import *
from src.buttons import keyboard
import src.utils as utils

### KICK
def kick_user(vk_session, msg, user_id):
  chat_id = msg['peer_id'] - 2000000000
  
  if int(user_id) > 0:
    vk_session.method('messages.removeChatUser', {'user_id': user_id, 'chat_id': chat_id})
  else:
    vk_session.method('messages.removeChatUser', {'member_id': int(user_id), 'chat_id': chat_id})
      
  utils.remove_user_by_id(abs(user_id))
  User().delete_by_id(abs(user_id))

def handle_kick(vk_session, msg, admin_keys, members):
  user_id = None
  chat_id = msg['peer_id'] - 2000000000

  if 'reply_message' in msg:
    fwd = msg['reply_message']
    utils.get_user_by_profile(fwd['from_id'])
    user_id = fwd['from_id']
  else:
    remove_id = re.search(r'(?:id|club)(\d+)', msg['text'])
    if remove_id:
      user_id = int(remove_id.group(1))

  if user_id and user_id != msg['from_id'] and user_id not in admin_keys:
    kick_user(vk_session, msg, user_id)
  else:
    vk_session.method('messages.send', {'chat_id': chat_id, 'message': 'Вы не можете кикнуть самого себя!', 'random_id': 0})
    
# САМОКИК
def selfkick_answer(vk_session, msg):
  vk_session.method('messages.send', {
    'chat_id': msg['peer_id'] - 2000000000,
    'message': 'Исключить члена экипажа?',
    'random_id': 0,
    'keyboard': keyboard,
  })

def selfkick(vk_session, msg, event, user_id, kick_user_id):
  chat_id = msg['peer_id'] - 2000000000

  if user_id not in admin_keys:
    vk_session.method('messages.send', {'chat_id': chat_id, 'message': 'У вас нет уровня доступа для этих команд!', 'random_id': 0})
    return

  payload = json.loads(event.object['message'].get('payload', '{}'))
  if payload.get('id') == '1':
    kick_user(vk_session, msg, kick_user_id)
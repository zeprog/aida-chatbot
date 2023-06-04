import re
import utils
from config import *
from models import User

### ADD WARN
def warn_user(vk_session, msg, user_id, user_name):
  user = utils.get_user_by_id(user_id)
  user.warns += 1
  user.save()

  vk_session.method('messages.send', {
    'chat_id': msg['peer_id'] - 2000000000,
    'message': f'Выдано предупреждение {user_name}. Предупреждений {user.warns}/{max_warns}',
    'random_id': 0
  })

  if user.warns >= max_warns:
    vk_session.method('messages.removeChatUser', {
      'user_id': user_id,
      'chat_id': msg['peer_id'] - 2000000000
    })
    utils.remove_user_by_id(user_id)
    User().delete_by_id(user_id)

def handle_warn(vk_session, msg, admin_keys, members):
  if 'reply_message' in msg:
    fwd = msg['reply_message']
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    if fwd['from_id'] != msg['from_id'] and int(fwd['from_id']) not in admin_keys:
      warn_user(vk_session, msg, fwd['from_id'], fwd['first_name'] + ' ' + fwd['last_name'])
    else:
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете дать предупреждение самому себе!',
        'random_id': 0
      })
  else:
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    warn_id = re.search(r'(?:id|club)(\d+)', msg['text'])
    warn_id = warn_id.group(0)
    warn_id_without_numbers = int(re.findall(r'\d+', warn_id)[0])
    if warn_id_without_numbers != msg['from_id'] and warn_id_without_numbers not in admin_keys:
      warn_user(vk_session, msg, warn_id_without_numbers, utils.get_user_by_id(warn_id_without_numbers).name)
    else:
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете дать предупреждение самому себе!',
        'random_id': 0
      })
      
### REMOVE WARN
def handle_remove_warn(vk_session, msg, members):
  user_id = None
  if 'reply_message' in msg:
    user_id = msg['reply_message']['from_id']
  else:
    id_match = re.search(r'(?:id|club)(\d+)', msg['text'])
    if id_match:
      user_id = int(id_match.group(1))
      
  if user_id is not None:
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    user = utils.get_user_by_id(user_id)
    if user and user.warns > 0:
      user.warns -= 1
      user.save()
      message = f'Предупреждение снято. Предупреждений {user.warns}/{max_warns}'
    else:
      message = 'Предупреждения отсутствуют!'
    vk_session.method('messages.send', {
      'chat_id': msg['peer_id'] - 2000000000,
      'message': message,
      'random_id': 0
    })
    
### REMOVE WARNS
def handle_remove_warns(vk_session, msg, members):
  user_id = None
  warns = 0
  if 'reply_message' in msg:
    user_id = msg['reply_message']['from_id']
  else:
    id_match = re.search(r'(?:id|club)(\d+)', msg['text'])
    if id_match:
      user_id = int(id_match.group(1))
  if user_id is not None:
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    user = utils.get_user_by_id(user_id)
    print(re.findall(r'\d+', msg['text']))
    warns = int(re.findall(r'\d+', msg['text'])[0]) if int(re.findall(r'\d+', msg['text'])[0]) < 5 else None
    print(warns)
    if user and user.warns > 0 and warns != None:
      if user.warns - warns >= 0:
        user.warns -= warns
        user.save()
        message = f'Предупреждения сняты. Предупреждений {user.warns}/{max_warns}'
      else:
        message = 'Число превышает текущее количество предупреждений'
    elif user and user.warns == 0:
      message = 'Предупреждения отсутствуют!'
    elif user and user.warns > 0 and warns == None:
      user.warns = 0
      user.save()
      message = f'Все предупреждения сняты. Предупреждений {user.warns}/{max_warns}'
    vk_session.method('messages.send', {
      'chat_id': msg['peer_id'] - 2000000000,
      'message': message,
      'random_id': 0
    })
    
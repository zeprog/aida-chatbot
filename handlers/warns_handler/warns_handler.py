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
    elif fwd['from_id'] == msg['from_id']:
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете дать предупреждение самому себе!',
        'random_id': 0
      })
    elif int(fwd['from_id']) not in admin_keys:
      vk_session.method('messages.send', {
          'chat_id': msg['peer_id'] - 2000000000,
          'message': 'Вы не можете дать предупреждение руководству!',
          'random_id': 0
        })
  else:
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    warn_id = re.search(r'(?:id|club)(\d+)', msg['text'])
    warn_id = warn_id.group(0)
    warn_id_without_numbers = int(re.findall(r'\d+', warn_id)[0])
    if int(warn_id_without_numbers) != int(msg['from_id']) and int(warn_id_without_numbers) not in admin_keys:
      warn_user(vk_session, msg, warn_id_without_numbers, utils.get_user_by_id(warn_id_without_numbers).name)
    elif int(warn_id_without_numbers) == int(msg['from_id']):
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете дать предупреждение самому себе!',
        'random_id': 0
      })
    elif int(warn_id_without_numbers) in admin_keys:
      vk_session.method('messages.send', {
          'chat_id': msg['peer_id'] - 2000000000,
          'message': 'Вы не можете дать предупреждение руководству!',
          'random_id': 0
        })
      
### REMOVE WARN
def handle_remove_warn(vk_session, msg, members):
  user_ids = []

  if 'reply_message' in msg:
    user_ids = [msg['reply_message']['from_id']]
  else:
    id_matches = re.findall(r'(?:id|club)(\d+)', msg['text'])
    if id_matches:
      user_ids = [int(id) for id in id_matches]

  users_processed = []
  for user_id in user_ids:
    for profile in members['profiles']:
      utils.get_user_by_profile(profile)
    user = utils.get_user_by_id(user_id)
    if user and user.warns > 0:
      user.warns -= 1
      user.save()
      users_processed.append(user.name)

  if users_processed:
    if len(users_processed) > 1:
      users_str = ', '.join(users_processed[:-1]) + ' и ' + users_processed[-1]
    else:
      users_str = users_processed[0]
    message = f'Предупреждение снято для {users_str}.'
  else:
    message = 'Предупреждения отсутствуют!'

  vk_session.method('messages.send', {
    'chat_id': msg['peer_id'] - 2000000000,
    'message': message,
    'random_id': 0
  })
    
### REMOVE WARNS    
def handle_remove_warns(vk_session, msg, members):
  user_ids = None
  warns = 0
  remove_all = False
  
  # Получение ID пользователей из сообщения или ответа
  if 'reply_message' in msg:
    user_ids = [msg['reply_message']['from_id']]
  else:
    id_matches = re.findall(r'(\d+)', msg['text'])
    if id_matches:
      user_ids = list(map(int, id_matches))

  # Получение количества предупреждений для снятия
  matches = re.findall(r'\d+', msg['text'])
  warns = int(matches[0]) if matches and int(matches[0]) < 5 else None
  
  # Если не указаны ID пользователей, снимаем предупреждения у всех
  if user_ids is None:
    remove_all = True
    user_ids = [profile['id'] for profile in members['profiles']]
  # Снятие предупреждений
  removed_users = []
  for user_id in user_ids:
    user = utils.get_user_by_id(user_id)
    if user and user.warns > 0:
      if warns is not None and user.warns - warns >= 0:
        user.warns -= warns
      else:
        user.warns = 0
      user.save()
      removed_users.append(user)
  
  # Отправка сообщения
  if removed_users:
    if remove_all:
      message = 'Все предупреждения сняты!'
    else:
      message = ', '.join([f'Предупреждения сняты для {id.name}, предупреждений {id.warns}/{max_warns}' for id in removed_users])
  else:
    message = 'Предупреждения отсутствуют!'
  
  vk_session.method('messages.send', {
    'chat_id': msg['peer_id'] - 2000000000,
    'message': message,
    'random_id': 0
  })
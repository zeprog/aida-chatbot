import re
import utils
from config import *
from models import User

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
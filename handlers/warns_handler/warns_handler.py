import re
import utils
from config import *
from models import User

def handle_warn(vk_session, msg, admin_keys):
  warn_id = re.search(r'(?:id|club)(\d+)', msg['text'])
  warn_id = warn_id.group(0)
  warn_id_without_numbers = int(re.findall(r'\d+', warn_id)[0])
  fwd_user = utils.get_user_by_id(warn_id_without_numbers)
  if warn_id_without_numbers not in admin_keys:
    if warn_id_without_numbers != fwd_user.vk_id:
      fwd_user.warns += 1
      fwd_user.save()
      
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': f'Выдано предупреждение {fwd_user.name}. Предупреждений {fwd_user.warns}/{max_warns}',
        'random_id': 0
      })
      
      if fwd_user.warns >= max_warns:
        vk_session.method('messages.removeChatUser', {
          'user_id': fwd_user.vk_id,
          'chat_id': msg['peer_id'] - 2000000000
        })
        utils.remove_user_by_id(fwd_user.vk_id)
        User().delete_by_id(fwd_user.vk_id)
    else:
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете дать предупреждение самому себе!',
        'random_id': 0
      })
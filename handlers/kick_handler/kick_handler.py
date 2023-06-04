import re
import utils
from models import User
from config import *

### KICK
def kick_user(vk_session, msg, user_id):
  if int(user_id) > 0:
    vk_session.method('messages.removeChatUser', {
      'user_id': user_id,
      'chat_id': msg['peer_id'] - 2000000000
    })
    utils.remove_user_by_id(user_id)
    User().delete_by_id(user_id)
  else:
    vk_session.method('messages.removeChatUser', {
      'member_id': int(user_id),
      'chat_id': msg['peer_id'] - 2000000000
    })
    utils.remove_user_by_id(-user_id)
    User().delete_by_id(abs(user_id))

def handle_kick(vk_session, msg, admin_keys, members):
  user_id = None

  if 'reply_message' in msg:
    fwd = msg['reply_message']
    if int(fwd['from_id']) > 0:
      for profile in members['profiles']:
        utils.get_user_by_profile(profile)
    else:
      for group in members['groups']:
        utils.get_user_by_profile(group)

    user_id = fwd['from_id']
  else:
    remove_id = re.search(r'(?:id|club)(\d+)', msg['text'])
    remove_id = remove_id.group(0)
    if remove_id:
      remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
      user_id = int(remove_id_without_numbers)

  if user_id is not None and user_id != msg['from_id'] and int(user_id) not in admin_keys:
    kick_user(vk_session, msg, user_id)
  else:
    vk_session.method('messages.send', {
      'chat_id': msg['peer_id'] - 2000000000,
      'message': 'Вы не можете кикнуть самого себя!',
      'random_id': 0
    })
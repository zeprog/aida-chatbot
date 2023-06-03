import re
import utils
from models import User

def handle_kick(vk_session, msg, admin_keys):
  remove_id = re.search(r'(?:id|club)(\d+)', msg['text'])
  remove_id = remove_id.group(0)
  remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
  remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
  fwd_user = utils.get_user_by_id(int(remove_id_without_numbers))
  if int(remove_id_without_numbers) not in admin_keys:
    if int(remove_id_without_numbers) != fwd_user.vk_id:
      if 'id' in msg['text']:
        vk_session.method('messages.removeChatUser', {
          'user_id': remove_id_without_numbers,
          'chat_id': msg['peer_id'] - 2000000000
        })
        utils.remove_user_by_id(fwd_user.vk_id)
        User().delete_by_id(remove_id)
      else:
        vk_session.method('messages.removeChatUser', {
          'member_id': -int(remove_id_without_numbers),
          'chat_id': msg['peer_id'] - 2000000000
        })
        utils.remove_user_by_id(-fwd_user.vk_id)
        User().delete_by_id(remove_id)
    else:
      vk_session.method('messages.send', {
        'chat_id': msg['peer_id'] - 2000000000,
        'message': 'Вы не можете кикнуть самого себя!',
        'random_id': 0
      })
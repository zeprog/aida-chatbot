import re
import vk_api
import utils
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from models import User
from config import *

class MyLongPoll(VkBotLongPoll):
  def listen(self):
    while True:
      try:
        for event in self.check():
          yield event
      except Exception as err:
        print(err)

def handle_kick(vk_session, msg, admin_keys):
  remove_id = re.search(r'(?:id|club)(\d+)', msg['text'])
  remove_id = remove_id.group(0)
  remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
  remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
  print('remove_id_without_numbers ', remove_id_without_numbers)
  fwd_user = utils.get_user_by_id(int(remove_id_without_numbers))
  if int(remove_id_without_numbers) not in admin_keys:
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

def handle_warn(vk_session, msg, admin_keys):
  warn_id = re.search(r'(?:id|club)(\d+)', msg['text'])
  warn_id = warn_id.group(0)
  warn_id_without_numbers = int(re.findall(r'\d+', warn_id)[0])
  if warn_id_without_numbers not in admin_keys:
    fwd_user = utils.get_user_by_id(warn_id_without_numbers)
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

def runVkBot():
  vk_session = vk_api.VkApi(token=token)
  longpoll = VkBotLongPoll(vk_session, group_id=group_id)

  for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
      msg = event.obj.message
      user_id = msg['from_id']
      text = msg['text']
      
      # the remaining logic goes here
      
      if user_id in map(int, admin_keys):
        if 'кик' in text:
          handle_kick(vk_session, msg, admin_keys)
        elif 'пред' in text:
          handle_warn(vk_session, msg, admin_keys)

if __name__ == '__main__':
  runVkBot()
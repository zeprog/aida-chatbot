import vk_api
import utils
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *
from handlers.kick_handler.kick_handler import handle_kick, selfkick_answer, selfkick
from handlers.warns_handler.warns_handler import handle_warn, handle_remove_warn, handle_remove_warns

class MyLongPoll(VkBotLongPoll):
  def listen(self):
    while True:
      try:
        for event in self.check():
          yield event
      except Exception as err:
        print(err)

def handle_action_event(event, vk_session, msg, members):
  if event.object['message']['action']['type'] == 'chat_kick_user':
    selfkick_answer(vk_session, msg)
  elif event.object['message']['action']['type'] == 'chat_invite_user':
    if int(event.object['message']['action']['member_id']) > 0:
      for profile in members['profiles']:
        utils.get_user_by_profile(profile)
    else:
      for group in members['groups']:
        utils.get_user_by_profile(group)

def handle_text_event(event, vk_session, msg, user_id, admin_keys, members):
  text_words = msg['text'].lower().split()
  if 'кик' in text_words:
    handle_kick(vk_session, msg, admin_keys, members)
  elif 'снять' in text_words:
    if 'преды' in text_words:
      handle_remove_warns(vk_session, msg, members)
    elif 'пред' in text_words:
      handle_remove_warn(vk_session, msg, members)
  elif 'пред' in text_words:
    handle_warn(vk_session, msg, admin_keys, members)
  else:
    vk_session.method('messages.send', {
      'chat_id': msg['peer_id'] - 2000000000,
      'message': 'У вас нет уровня доступа для этих команд!',
      'random_id': 0
    })

def runVkBot():
  vk_session = vk_api.VkApi(token=token)
  longpoll = MyLongPoll(vk_session, group_id=group_id)
  
  for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
      msg = event.obj.message
      user_id = msg['from_id']
      members = vk_session.method('messages.getConversationMembers', {'peer_id': msg['peer_id']})

      if 'action' in event.object['message']:
        handle_action_event(event, vk_session, msg, members)
      elif user_id in map(int, admin_keys):
        handle_text_event(event, vk_session, msg, user_id, admin_keys, members)
        
      for profile in members['profiles']:
        if profile['id'] == user_id:
          utils.update_user_name(user_id, profile)

if __name__ == '__main__':
  runVkBot()
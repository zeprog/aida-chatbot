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

def runVkBot():
  vk_session = vk_api.VkApi(token=token)
  longpoll = VkBotLongPoll(vk_session, group_id=group_id)

  for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
      msg = event.obj.message
      user_id = msg['from_id']
      text_words = msg['text'].lower().split()
      # print(msg)
      print(event)
      
      members = vk_session.method('messages.getConversationMembers', {
        'peer_id': msg['peer_id']
      })
      
      # САМОКИК
      if 'action' in event.object['message']:
        if event.object['message']['action']['type'] == 'chat_kick_user':
          kick_user = event.object['message']['from_id']
          selfkick_answer(vk_session, msg)
        if event.object['message']['action']['type'] == 'chat_invite_user':
          if int(event.object['message']['action']['member_id']) > 0:
            for profile in members['profiles']:
              utils.get_user_by_profile(profile)
          else:
            for group in members['groups']:
              utils.get_user_by_profile(group)
      elif 'Исключить' in event.object['message']['text']:
        selfkick(vk_session, msg, event, user_id, kick_user)
      else:
        if user_id in map(int, admin_keys):
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
        # if user_id not in map(int, admin_keys):
          vk_session.method('messages.send', {
            'chat_id': msg['peer_id'] - 2000000000,
            'message': 'У вас нет уровня доступа для этих команд!',
            'random_id': 0
          })
          continue
      
      for profile in members['profiles']:
        if profile['id'] == user_id:
          utils.update_user_name(user_id, profile)

if __name__ == '__main__':
  runVkBot()
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *
from handlers.kick_handler.kick_handler import handle_kick
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

      if user_id not in map(int, admin_keys):
        vk_session.method('messages.send', {
          'chat_id': msg['peer_id'] - 2000000000,
          'message': 'У вас нет уровня доступа для этих команд!',
          'random_id': 0
        })
        continue

      members = vk_session.method('messages.getConversationMembers', {
        'peer_id': msg['peer_id']
      })

      if 'кик' in text_words:
        handle_kick(vk_session, msg, admin_keys, members)
      elif 'снять' in text_words:
        if 'преды' in text_words:
          handle_remove_warns(vk_session, msg, members)
        elif 'пред' in text_words:
          handle_remove_warn(vk_session, msg, members)
      elif 'пред' in text_words:
        handle_warn(vk_session, msg, admin_keys, members)

if __name__ == '__main__':
  runVkBot()
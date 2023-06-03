import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *
from handlers.kick_handler.kick_handler import handle_kick
from handlers.warns_handler.warns_handler import handle_warn

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
      text = msg['text']
      
      members = vk_session.method('messages.getConversationMembers', {
        'peer_id': msg['peer_id']
      })
      
      # the remaining logic goes here
      
      if user_id in map(int, admin_keys):
        if 'кик' in text:
          handle_kick(vk_session, msg, admin_keys, members)
        elif 'пред' in text:
          handle_warn(vk_session, msg, admin_keys, members)
      else:
        vk_session.method('messages.send', {
          'chat_id': msg['peer_id'] - 2000000000,
          'message': 'У вас нет уровня доступа для этих команд!',
          'random_id': 0
        })

if __name__ == '__main__':
  runVkBot()
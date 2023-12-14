import vk_api
from handlers.stats.statistic_handler import fetch_vk_message_statistics
import utils as utils
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *
from handlers.kick_handler.kick_handler import handle_kick, selfkick_answer
from handlers.warns_handler.warns_handler import handle_warn, handle_remove_warn, handle_remove_warns

vk_session = vk_api.VkApi(token=token)

class MyLongPoll(VkBotLongPoll):
  def __init__(self, vk_session, group_id):
    super().__init__(vk_session, group_id)
    self.running = True  # Control the loop with this attribute

  def listen(self):
    while self.running:
      try:
        for event in self.check():
          yield event
      except Exception as err:
        print(err)
        break  # Optional: break on exception

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
  user = utils.get_user_by_id(user_id)
  print(user)
  if(user != None):
    if('аида' in text_words):
      if 'кик' in text_words:
        handle_kick(vk_session, msg, admin_keys, members)
      elif 'снять' in text_words:
        if 'преды' in text_words:
          handle_remove_warns(vk_session, msg, members)
        elif 'пред' in text_words:
          handle_remove_warn(vk_session, msg, members)
      elif 'пред' in text_words:
        handle_warn(vk_session, msg, admin_keys, members)
      elif 'топ' in text_words:
        statistics = fetch_vk_message_statistics(msg['peer_id'], 7)
        print(f"Total messages: {statistics['total_messages']}")
        print(f"Total symbols: {statistics['total_symbols']}")
      else:
        vk_session.method('messages.send', {
          'chat_id': msg['peer_id'] - 2000000000,
          'message': 'Такой команды не существует!',
          'random_id': 0
        })
  else:
    if(msg['from_id'] > 0):
      for profile in members['profiles']:
        utils.get_user_by_profile(profile)
    else:
      for group in members['groups']:
        utils.get_user_by_profile(group)

def runVkBot():
  vk_session = vk_api.VkApi(token=token)
  longpoll = MyLongPoll(vk_session, group_id=group_id)
  for event in longpoll.listen():
    msg = event.obj.message
    members = vk_session.method('messages.getConversationMembers', {'peer_id': msg['peer_id']})
    users = utils.get_all_users()
    if(users == None):
      for profile in members['profiles']:
        utils.create_users_or_groups(profile)
    if event.type == VkBotEventType.MESSAGE_NEW:
      user_id = msg['from_id']

      if 'action' in event.object['message']:
        handle_action_event(event, vk_session, msg, members)
      elif user_id in map(int, admin_keys):
        handle_text_event(event, vk_session, msg, user_id, admin_keys, members)
        
      for profile in members['profiles']:
        if profile['id'] == user_id:
          utils.update_user_name(user_id, profile)

if __name__ == '__main__':
  runVkBot()
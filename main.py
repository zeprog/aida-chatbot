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
    
def runVkBot():
  vk_session = vk_api.VkApi(token=token)
  longpoll = VkBotLongPoll(vk_session, group_id=group_id)

  for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
      msg = event.obj.message
      print('msg', msg, "\n\n")
      user_id = msg['from_id']
      text = msg['text']
      fwd = vk_session.method('messages.getByConversationMessageId', {
        'conversation_message_ids': msg['conversation_message_id'],
        'peer_id': msg['peer_id']
      })
      print('fwd ', fwd, "\n\n")
      
      members = vk_session.method('messages.getConversationMembers', {
        'peer_id': msg['peer_id']
      })
      print('members ', members, "\n\n")
      
      members_id = 0
      for member in members['items']:
        member_id = int(member['member_id'])
        print(type(member_id))
        if member_id == msg['from_id']:
          members_id = int(member_id)
        elif member_id < 0:
          members_id = int(member_id)
          
      for profile in members['profiles']:
        utils.get_user_by_profile(profile)
        
      for group in members['groups']:
        utils.get_group_by_group(group)
        
      print('members_id ', members_id, "\n\n")
      
      if user_id in map(int, admin_keys):
        if 'кик' in text:
          remove_id = re.search(r'(?:id|club)(\d+)', msg['text'])
          remove_id = remove_id.group(0)
          print('remove_id', remove_id)
          remove_id_without_numbers = re.findall(r'\d+', remove_id)[0]
          print('remove_id_without_numbers ', remove_id_without_numbers)
          fwd_user = utils.get_user_by_id(int(remove_id_without_numbers))
          if int(remove_id_without_numbers) not in admin_keys:
            if 'id' in msg['text']:
              vk_session.method('messages.removeChatUser', {
                'user_id': remove_id_without_numbers,
                'chat_id': msg['peer_id'] - 2000000000
              })
              utils.remove_user_by_profile(fwd_user)
              User().delete_by_id(remove_id)
            else:
              vk_session.method('messages.removeChatUser', {
                'member_id': -int(remove_id_without_numbers),
                'chat_id': msg['peer_id'] - 2000000000
              })
              utils.remove_user_by_group(fwd_user)
              User().delete_by_id(remove_id)
          else:
            if int(remove_id_without_numbers) == admin_keys[0]:
              vk_session.method('messages.send', {
                'chat_id': msg['peer_id'] - 2000000000,
                'message': f'Невозможно кикнуть директора Щ.И.Т.а',
                'random_id': 0
              })
            else:
              vk_session.method('messages.send', {
                'chat_id': msg['peer_id'] - 2000000000,
                'message': f'Невозможно кикнуть Скай',
                'random_id': 0
              }) 
        elif 'пред' in text:
          warn_id = re.search(r'(?:id|club)(\d+)', text)
          warn_id = warn_id.group(0)
          warn_id_without_numbers = int(re.findall(r'\d+', warn_id)[0])
          if warn_id_without_numbers not in admin_keys:
            fwd_user = utils.get_user_by_id(warn_id_without_numbers)
            print(fwd_user)
            fwd_user.warns += 1
            fwd_user.save()
            
            user_info = vk_session.method('users.get', {
              'user_id': fwd_user.vk_id
            })
            
            print(user_info)
            
            vk_session.method('messages.send', {
              'chat_id': msg['peer_id'] - 2000000000,
              'message': f'Выдано предупреждение {fwd_user.name}. Предупреждений {fwd_user.warns}/{max_warns}',
              'random_id': 0
            })
            
            if fwd_user.warns == max_warns or fwd_user.warns > max_warns:
              vk_session.method('messages.removeChatUser', {
                'user_id': fwd_user.vk_id,
                'chat_id': msg['peer_id'] - 2000000000
              })
              utils.remove_user_by_profile(fwd_user)
              User().delete_by_id(fwd_user.vk_id)
          else:
            vk_session.method('messages.send', {
              'chat_id': msg['peer_id'] - 2000000000,
              'message': 'Вы не можете руководству сделать предупреждение!',
              'random_id': 0
            })

if __name__ == '__main__':
  runVkBot()
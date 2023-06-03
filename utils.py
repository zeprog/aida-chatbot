from peewee import DoesNotExist
from models import User

def create_user_or_group(profile, is_group=False):
  User.create(
    vk_id=(-int(profile['id']) if is_group else profile['id']),
    warns=0,
    name=profile['name'] if is_group else profile['first_name'] + ' ' + profile['last_name']
  )
  
### GET
def get_user_by_profile(profile, is_group=False):
  try:
    return User.get(User.vk_id == (-int(profile['id']) if is_group else profile['id']))
  except DoesNotExist:
    create_user_or_group(profile, is_group)
    return User.get(User.vk_id == (-int(profile['id']) if is_group else profile['id']))

def get_user_by_id(user_id):
  try:
    return User.get(User.vk_id == user_id)
  except DoesNotExist:
    return 'User not found'


### DELETE
def remove_user_by_id(user_id):
  try:
    user = User.get(User.vk_id == user_id)
    user.delete_instance()
    return 'Пользователь успешно удален из базы данных!'
  except DoesNotExist:
    return 'Пользователь не найден в базе данных!'
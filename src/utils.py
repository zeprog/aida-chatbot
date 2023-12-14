from peewee import DoesNotExist
from models import User

def create_users_or_groups(profile, is_group=False):
  User.create(
    vk_id=(-int(profile['id']) if is_group else profile['id']),
    warns=0,
    name=profile['name'] if is_group else profile['first_name'] + ' ' + profile['last_name']
  )

def create_user_or_group(user_id, is_group=False):
  pass 
  
### GET
def get_user_by_profile(profile, is_group=False):
  try:
    print((-int(profile['id']) if is_group else int(profile['id'])))
    return User.get(User.vk_id == (-int(profile['id']) if is_group else int(profile['id'])))
  except DoesNotExist:
    create_users_or_groups(profile, is_group)
    return User.get(User.vk_id == (-int(profile['id']) if is_group else int(profile['id'])))

def get_user_by_id(user_id):
  try:
    return User.get(User.vk_id == user_id)
  except DoesNotExist:
    return None
  
def get_all_users():
  try:
    return User.get()
  except DoesNotExist:
    return None


### DELETE
def remove_user_by_id(user_id):
  try:
    user = User.get(User.vk_id == user_id)
    user.delete_instance()
    return 'Пользователь успешно удален из базы данных!'
  except DoesNotExist:
    return 'Пользователь не найден в базе данных!'
  
### UPDATE
def update_user_name(user_id, profile, is_group=False):
  user = User.get(User.vk_id == user_id)
  user.name = profile['name'] if is_group else profile['first_name'] + ' ' + profile['last_name']
  user.save()
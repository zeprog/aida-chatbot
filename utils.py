from models import User

### GET
def get_user_by_profile(profile):
  try:
    return User().get(vk_id=profile['id'])
  except:
    User(
      vk_id=profile['id'],
      warns=0,
      name=profile['first_name'] + ' ' + profile['last_name']
    ).save()
    return User().get(vk_id=profile['id'])
  
def get_user_by_id(user_id):
  try:
    return User().get(vk_id=user_id)
  except:
    return 'User not found'
  
def get_group_by_group(group):
  try:
    return User().get(vk_id=-int(group['id']))
  except:
    User(
      vk_id=-int(group['id']),
      warns=0,
      name=group['name']
    ).save()
    return User.get(vk_id=-int(group['id']))
  
  
### DELETE
def remove_user_by_profile(profile):
  try:
    user = User().get(vk_id=profile.vk_id)
    user.delete_instance()
    return 'Пользователь успешно удален из базы данных!'
  except User.DoesNotExist:
    return 'Пользователь не найден в базе данных!'
  
def remove_user_by_group(group):
  try:
    user = User().get(vk_id=-int(group.vk_id))
    user.delete_instance()
    return 'Пользователь успешно удален из базы данных!'
  except User.DoesNotExist:
    return 'Пользователь не найден в базе данных!'
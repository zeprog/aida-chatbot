from unittest.mock import MagicMock, patch
import pytest
from vk_api.bot_longpoll import VkBotEventType
from src.main import MyLongPoll, handle_action_event, runVkBot, handle_text_event

@pytest.fixture
def mock_vk_session():
  return MagicMock()

@pytest.fixture
def mock_vk_api():
  vk_api_mock = MagicMock()
  vk_api_mock.method = MagicMock()
  return vk_api_mock

@pytest.fixture
def mock_long_poll():
  # Mock the MyLongPoll and its listen method
  long_poll_mock = MagicMock()
  long_poll_mock.listen = MagicMock()
  return long_poll_mock

@pytest.fixture
def mock_utils():
  with patch('src.utils') as mock_utils:
    yield mock_utils

@patch('src.main.MyLongPoll.check')
def test_listen(mock_check, mock_vk_session):
  # Setup the mock to yield a value and then raise StopIteration
  mock_check.side_effect = [[], StopIteration]

  long_poll = MyLongPoll(mock_vk_session, 'group_id')
  with pytest.raises(StopIteration):
    next(long_poll.listen())
  
@patch('vk_api.VkApi')
@patch('src.main.MyLongPoll')
def test_runVkBot(mock_long_poll_class, mock_vk_api_class, mock_vk_api, mock_long_poll):
  # Configure the mocks
  mock_vk_api_class.return_value = mock_vk_api
  mock_long_poll_class.return_value = mock_long_poll

  event = MagicMock()
  event.type = VkBotEventType.MESSAGE_NEW
  event.obj.message = {'from_id': 'user_id', 'peer_id': 'peer_id'}
  mock_long_poll.listen.return_value = [event]

  runVkBot()
  # Assertions and verifications
  mock_vk_api.method.assert_called_with('messages.getConversationMembers', {'peer_id': 'peer_id'})

def create_event(action_type, member_id=None):
  event = MagicMock()
  event.object['message']['action']['type'] = action_type
  if member_id is not None:
    event.object['message']['action']['member_id'] = member_id
  return event

@patch('src.handlers.kick_handler.kick_handler.selfkick_answer')
@patch('src.utils.get_user_by_profile')
def test_handle_action_event_chat_kick_user(mock_selfkick_answer, mock_vk_session):
  event = MagicMock()
  event.object = {'message': {'action': {'type': 'chat_kick_user'}}}
  msg = MagicMock()
  members = MagicMock()

  handle_action_event(event, mock_vk_session, msg, members)

  mock_selfkick_answer.method(mock_vk_session, msg)
  mock_selfkick_answer.method.assert_called_with(mock_vk_session, msg)


@patch('src.utils.get_user_by_profile')
def test_handle_action_event_chat_invite_user_positive_member_id(mock_vk_session, mock_utils):
  event = create_event('chat_invite_user', member_id=123)
  msg = MagicMock()
  members = {'groups': [{'id': 123}]}
  handle_action_event(event, mock_vk_session, msg, members)
  member = members['groups'][0]
  mock_utils.get_user_by_profile(member)
  mock_utils.get_user_by_profile.assert_called_with(member)

@patch('src.utils.get_user_by_profile')
def test_handle_action_event_chat_invite_user_negative_member_id(mock_utils, mock_vk_session):
  event = create_event('chat_invite_user', member_id=-123)
  msg = MagicMock()
  members = {'groups': [{'id': -123}]}
  handle_action_event(event, mock_vk_session, msg, members)
  member = members['groups'][0]
  mock_utils.get_user_by_profile(member)
  mock_utils.get_user_by_profile.assert_called_with(member)

@patch('src.handlers.kick_handler.kick_handler.handle_kick')
def test_handle_text_event_kick(mock_handle_kick, mock_vk_session):
  event = MagicMock()
  msg = {'text': 'Кик someone', 'peer_id': 2000000001}
  admin_keys = ['key1', 'key2']
  members = MagicMock()

  handle_text_event(event, mock_vk_session, msg, 'user_id', admin_keys, members)

  mock_handle_kick(mock_vk_session, msg, admin_keys, members)
  mock_handle_kick.assert_called_with(mock_vk_session, msg, admin_keys, members)

@patch('src.handlers.warns_handler.warns_handler.handle_warn')
def test_handle_text_event_warn(mock_handle_warn, mock_vk_session):
  event = MagicMock()
  msg = {'text': 'Пред someone', 'peer_id': 2000000001}
  admin_keys = ['key1', 'key2']
  members = MagicMock()

  handle_text_event(event, mock_vk_session, msg, 'user_id', admin_keys, members)

  mock_handle_warn(mock_vk_session, msg, admin_keys, members)
  mock_handle_warn.assert_called_with(mock_vk_session, msg, admin_keys, members)

@patch('src.handlers.warns_handler.warns_handler.handle_remove_warns')
def test_handle_text_event_remove_warns(mock_handle_remove_warns, mock_vk_session):
  event = MagicMock()
  msg = {'text': 'Снять преды someone', 'peer_id': 2000000001}
  admin_keys = ['key1', 'key2']
  members = MagicMock()

  handle_text_event(event, mock_vk_session, msg, 'user_id', admin_keys, members)

  mock_handle_remove_warns(mock_vk_session, msg, admin_keys, members)
  mock_handle_remove_warns.assert_called_with(mock_vk_session, msg, admin_keys, members)

@patch('src.handlers.warns_handler.warns_handler.handle_remove_warn')
def test_handle_text_event_remove_warn(mock_handle_remove_warn, mock_vk_session):
  event = MagicMock()
  msg = {'text': 'Снять преды someone', 'peer_id': 2000000001}
  admin_keys = ['key1', 'key2']
  members = MagicMock()

  handle_text_event(event, mock_vk_session, msg, 'user_id', admin_keys, members)

  mock_handle_remove_warn(mock_vk_session, msg, admin_keys, members)
  mock_handle_remove_warn.assert_called_with(mock_vk_session, msg, admin_keys, members)

def test_handle_text_event_no_access(mock_vk_session):
  event = MagicMock()
  msg = {'text': 'random text', 'peer_id': 2000000001}
  admin_keys = ['key1', 'key2']
  members = MagicMock()

  handle_text_event(event, mock_vk_session, msg, 'user_id', admin_keys, members)

  mock_vk_session.method.assert_called_with('messages.send', {
    'chat_id': 1,  # 2000000001 - 2000000000
    'message': 'У вас нет уровня доступа для этих команд!',
    'random_id': 0
  })
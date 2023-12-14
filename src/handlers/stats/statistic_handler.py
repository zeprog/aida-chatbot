import json
import vk_api
import datetime
from models import Model
from config import *

def fetch_vk_message_statistics(peer_id, number_of_days):
  # Initialize VK session with your access token
  vk_session = vk_api.VkApi(token=access_token)
  vk = vk_session.get_api()

  # Define the time range
  end_date = datetime.datetime.now()
  if not isinstance(number_of_days, int):
      raise ValueError("number_of_days must be an integer")
  start_date = end_date - datetime.timedelta(days=number_of_days)
  start_timestamp = int(start_date.timestamp())
  end_timestamp = int(end_date.timestamp())

  # Initialize counters
  total_messages = 0
  total_symbols = 0

  # Fetch and analyze messages
  offset = 0
  while True:
      response = vk.messages.getHistory(peer_id=peer_id, offset=offset, start_time=start_timestamp, end_time=end_timestamp)
      messages = response['items']
      if not messages:
          break

      for message in messages:
          total_messages += 1
          total_symbols += len(message['text'])

      offset += len(messages)
  return {"total_messages": total_messages, "total_symbols": total_symbols}
import json

def get_button(color, text):
  return {
    "action": {
      'type': 'text',
      "payload": "{\"id\": \"" + "1" + "\"}",
      "label": f"{text}"
    },
    "color": f"{color}"
  }
  
keyboard = {
  "one_time": False,
  "inline": True,
  "buttons": [
    [get_button('negative', 'Исключить')]
  ]
}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))
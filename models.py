from peewee import *

db = SqliteDatabase('data.db')

class User(Model):
  class Meta:
    database = db
    db_table = 'Users'
  vk_id = TextField(default='')
  warns = IntegerField()
  name = TextField(default='')
  nick = TextField(default='')
  
if __name__ == '__main__':
  db.create_tables([User])
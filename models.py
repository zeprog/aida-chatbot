from peewee import Model, SqliteDatabase, TextField, IntegerField

db = SqliteDatabase('data.db')

class User(Model):
  """
  User model for database.
  """
  vk_id = TextField(default='')
  warns = IntegerField(default=0)
  name = TextField(default='')
  nick = TextField(default='')

  class Meta:
    database = db
    db_table = 'Users'

if __name__ == '__main__':
  try:
    db.create_tables([User])
    print("Tables created successfully.")
  except Exception as e:
    print(f"Error occurred while creating tables: {e}")
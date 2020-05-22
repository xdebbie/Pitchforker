from peewee import SqliteDatabase, TextField, DoubleField, DateField, Model

# create the database file
db = SqliteDatabase('albums.db')


class BaseModel(Model):
    class Meta:
        database = db


class Pitchfork(BaseModel):
    url = TextField()
    pubdate = DateField()
    score = DoubleField()
    year = DateField()
    label = TextField()
    genre = TextField()
    title = TextField()
    artist = TextField()
    album = TextField()


if __name__ == "__main__":
    db.connect()
    db.create_tables([Pitchfork])
    db.close()

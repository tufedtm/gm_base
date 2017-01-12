import peewee

db = peewee.SqliteDatabase('gm_base.db')


class Magazine(peewee.Model):
    title = peewee.CharField()
    title_full = peewee.CharField(null=True)
    info = peewee.TextField()

    class Meta:
        database = db


class Item(peewee.Model):
    """
    title - PCGames2006First
    title2 - PCGames2006Second+
    """
    title = peewee.CharField()
    title2 = peewee.CharField(null=True)
    path = peewee.CharField()
    head = peewee.TextField(null=True)
    text = peewee.TextField(null=True)
    parent = peewee.ForeignKeyField('self', null=True)
    magazine = peewee.ForeignKeyField(Magazine)

    class Meta:
        database = db


class Image(peewee.Model):
    item = peewee.ForeignKeyField(Item)
    image = peewee.CharField()

    class Meta:
        database = db


class File(peewee.Model):
    item = peewee.ForeignKeyField(Item)
    title = peewee.CharField()
    file = peewee.CharField()

    class Meta:
        database = db

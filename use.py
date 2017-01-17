import os

from models import db, Magazine, Item, Image, File
from parsers import PCGamesV1, PCGamesV2

db.create_tables([Magazine, Item, Image, File])

with db.atomic():
    p = 'E:\pc игры\pc игры 2004 1'
    for directory in os.listdir(p):
        PCGamesV1(f'{p}\\{directory}').save_items()

with db.atomic():
    p = 'E:\pc игры\pc игры 2004 2'
    for directory in os.listdir(p):
        PCGamesV2(f'{p}\\{directory}').save_items()

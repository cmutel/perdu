# -*- coding: utf-8 -*-
from . import base_dir
from .utils import sha256
from peewee import (
    BlobField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
)
from pathlib import Path


db_filepath = base_dir / "perdu-uploads.db"
database = SqliteDatabase(str(db_filepath))

abspath = lambda x: str(x.absolute()) if isinstance(x, Path) else x


class PathField(TextField):
    def db_value(self, value):
        return super().db_value(abspath(value))

    def python_value(self, value):
        return Path(value)


class File(Model):
    filepath = PathField()
    name = TextField()
    sha256 = TextField(unique=True)
    kind = TextField()

    def save(self, *args, **kwargs):
        self.sha256 = sha256(self.filepath)
        super().save(*args, **kwargs)

    def get_sha(self):
        self.sha256 = sha256(self.filepath)

    class Meta:
        database = database


database.create_tables([File], safe=True)

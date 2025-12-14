from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlmodel import  Field, Session, SQLModel, create_engine,select
from conf import settings
engine = create_engine(settings.url)

class MysqlNote(SQLModel,table=True):
    __tablename__='notes'
    id: int | None = Field(default=None,primary_key=True)
    title: str = Field(sa_column=Text)
    note: str = Field(sa_column=LONGTEXT)
    # tags: str = Field(sa_column=LONGTEXT)
    images_url: str = Field(sa_column=LONGTEXT)

    @classmethod
    def query(cls, title):
        with Session(engine) as session:
            statement = select(cls).where(cls.title == title)
            hero = session.exec(statement).first()
            print(hero)
        return hero

    def insert(self):
        with Session(engine) as session:
            session.add(self)
            session.commit()
        return self

    @classmethod
    def query_all(cls):
        with Session(engine) as session:
            statement = select(cls)
            heroes = session.exec(statement).all()
        return heroes

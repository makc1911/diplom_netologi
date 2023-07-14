import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
# from config import db_url_object
from config import DSN

# схема БД
metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    users_id = sq.Column(sq.Integer, primary_key=True)
# добавление записи в бд
engine = sq.create_engine(DSN)
# Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def add_user(engine, profile_id, users_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, users_id=users_id)
        session.add(to_bd)
        session.commit()

# извлечение записей из БД

def check_user(engine, profile_id, users_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id,
                                               Viewed.users_id == users_id).first()
        return True if from_bd else False
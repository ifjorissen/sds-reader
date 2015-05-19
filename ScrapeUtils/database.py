import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db')
Session = sessionmaker()
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                          autoflush=False,
#                                          bind=engine))


Base = declarative_base(bind=engine)
# Base.query = db_session.query_property()

def init_db():
    import datamodel
    Base.metadata.create_all()

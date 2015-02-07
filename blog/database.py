from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from multiprocessing.util import register_after_fork
from blog import app

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
register_after_fork(engine, engine.dispose)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

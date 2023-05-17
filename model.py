from pandas import DatetimeTZDtype
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

Base = declarative_base()

#Create the the table
class eventsdb(Base):
    __tablename__ = 'tb_events'  
    event_id = Column(Integer, primary_key=True)  
    event_type  = Column(String)
    customer_id = Column(Integer)
    timestamp = Column(DateTime)
    prev_timestamp = Column(DateTime)
    new_session = Column(Integer)
    time = Column(Float)
    increment = Column(Integer)
    session_id = Column(String)

       
    def start():
        string_connection = "postgresql://"+ config.db_user + ":" + config.db_password + "@" + config.db_hostname + ":" + config.db_port + "/"+ config.db_name
        print (string_connection)
        db_string = string_connection
        engine = create_engine(db_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        print ('\nTable created on database')
        return session, engine


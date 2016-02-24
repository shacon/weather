from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from weather_app import Base


class Locale(Base):
    __tablename__ = 'locale'

    zip_code = Column(Integer, primary_key=True)
    date = Column(DateTime)


class Forecast(Base):
    __tablename__ = 'forecast'

    id = Column(Integer, primary_key=True)
    period = Column(Integer)
    text = Column(String(500))

    locale_id = Column(Integer, ForeignKey('locale.zip_code'))
    locale = relationship("Locale", backref=backref("forecasts", order_by=id))



# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy.ext.declarative import declarative_base


# def init_db():

#     Base.metadata.create_all(bind=engine)

# init_db()

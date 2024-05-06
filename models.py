from sqlalchemy import Column, Integer, Float

from database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    current_value_counter = Column(Integer)
    pressure_value = Column(Float)
    status = Column(Integer)


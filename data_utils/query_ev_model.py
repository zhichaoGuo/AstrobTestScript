from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Data(Base):
    # 此处填数据表名称
    __tablename__ = 'places_xml_s231_f1_mea'
    id = Column(Integer, primary_key=True, autoincrement=True)
    place_id = Column(String(64), nullable=False)
    CategoryId = Column(String(64))
    version = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    xml = Column(String(64), nullable=False)
    line_index = Column(Integer, nullable=False)


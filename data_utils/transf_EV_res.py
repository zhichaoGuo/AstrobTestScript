import os.path
import threading

from sqlalchemy import create_engine
import xml.etree.ElementTree as ET

from sqlalchemy.orm import sessionmaker

from QueryXmlEVCase.DataInfo import EVInfo
from Utils import PathUtils
from query_ev_model import Base, Data


def run():
    engine = create_engine("mysql+pymysql://root:astrob@127.0.0.1:3306/here_ev_xml")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    data_path = "E:\\PLACES_XML_PREMIUM_231F1_WVM_DPLAP\\MEA_231F0\\"
    all_version_path = PathUtils.get_path_all_dir(data_path)
    for version_path in all_version_path:
        t = threading.Thread(target=parse_version_2_sql, args=(version_path, session,))
        t.setDaemon(True)
        t.start()


def parse_version_2_sql(version_path, session):
    all_country_path = PathUtils.get_path_all_dir(version_path)
    for country_path in all_country_path:
        for xml_path in PathUtils.get_path_all_xml(country_path):
            xml_data = parse_xml_data(version_path, country_path, xml_path)
            session.add_all(xml_data)
            session.commit()


def parse_xml_data(version_path, country_path, xml_path):
    tag = EVInfo.tag
    xml_data = []
    f = open(xml_path, encoding='utf-8')
    tree = ET.parse(f)
    root = tree.getroot()
    line_index = 1
    for node_place in root.findall(f'{tag}Place'):
        line_index += 1
        place_id = node_place.find(f'{tag}Identity').find(f'{tag}PlaceId').text
        category_id = ''
        try:
            for node_category in node_place.find(f'{tag}Content').find(f'{tag}Base').find(
                    f'{tag}CategoryList').findall(f'{tag}Category'):
                if node_category.get('categorySystem') != 'navteq-lcms':
                    continue
                category_id = node_category.find(f'{tag}CategoryId').text
        except Exception as err:
            print(err)
        xml_data.append(Data(place_id=place_id,
                             CategoryId=category_id,
                             version=os.path.basename(version_path),
                             country=os.path.basename(country_path),
                             xml=os.path.basename(xml_path),
                             line_index=line_index))
    f.close()
    return xml_data


def main():
    # engine = create_engine("mysql+pymysql://root:astrob@127.0.0.1:3306/here_ev_xml")
    # 此处填数据库名字
    # 在query_ev_model.py Data.__tablename__ 填数据表名称
    engine = create_engine("mssql+pymssql://sa:astrob@192.168.1.102/here_ev_xml")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    tag = EVInfo.tag
    # 此处填版本路径
    version_paths = ["E:\\PLACES_XML_PREMIUM_231F1_WVM_DPLAP\\MEA_231F0\\TQS2",
                     "E:\\PLACES_XML_PREMIUM_231F1_WVM_DPLAP\\MEA_231F0\\TQS3",
                     "E:\\PLACES_XML_PREMIUM_231F1_WVM_DPLAP\\MEA_231F0\\TQS4",
                     "E:\\PLACES_XML_PREMIUM_231F1_WVM_DPLAP\\MEA_231F0\\TQS5"]
    for version_path in version_paths:
        all_country_path = PathUtils.get_path_all_dir(version_path)
        for country_path in all_country_path:
            for xml_path in PathUtils.get_path_all_xml(country_path):
                xml_data = []
                f = open(xml_path, encoding='utf-8')
                tree = ET.parse(f)
                root = tree.getroot()
                line_index = 1
                for node_place in root.findall(f'{tag}Place'):
                    line_index += 1
                    place_id = node_place.find(f'{tag}Identity').find(f'{tag}PlaceId').text
                    category_id = ''
                    try:
                        for node_category in node_place.find(f'{tag}Content').find(f'{tag}Base').find(
                                f'{tag}CategoryList').findall(f'{tag}Category'):
                            if node_category.get('categorySystem') != 'navteq-lcms':
                                continue
                            category_id = node_category.find(f'{tag}CategoryId').text
                    except Exception as err:
                        print(err)
                    xml_data.append(Data(place_id=place_id,
                                         CategoryId=category_id,
                                         version=os.path.basename(version_path),
                                         country=os.path.basename(country_path),
                                         xml=os.path.basename(xml_path),
                                         line_index=line_index))
                f.close()
                session.add_all(xml_data)
                session.commit()
    session.close()


if __name__ == '__main__':
    main()

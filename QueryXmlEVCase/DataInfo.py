from xml.etree.ElementTree import Element

from Utils import LogUtils


class EVInfo:
    # Excel表格的表头顺序由此定义
    AllAttr = ['CountryCode',
               'BaseText',
               'FullStreetName',
               'HouseNumber',
               'PostalCode',
               'StandardNumber',
               'Open24x7Flag',
               'OpenTime',
               'ConnectorType',
               'NumberOfPorts',
               'MaxPowerLevel',
               'Level5',
               'Level4',
               'Level3',
               'Level2',
               'GeoPosition_Display_lat',
               'GeoPosition_Display_lon',
               'GeoPosition_Routing_lat',
               'GeoPosition_Routing_lon',
               'linkPvid',
               'PointAddressPvid',
               'MapVersion',
               'MapId',
               'AdminLevel5Id',
               'AdminLevel4Id',
               'AdminLevel3Id',
               'AdminLevel2Id',
               'XML_PATH',
               'Line_Index',
               'PlaceID']

    tag = '{http://places.maps.here.com/pds}'

    def __init__(self, ele: Element):
        for attr in self.AllAttr:
            setattr(self, attr, '')
        tag = self.tag
        # =<LocationList>=======================================================================
        # _<LocationList>_____<Location>_______________________________________________________

        node_location = ele.find(f'{tag}LocationList').find(f'{tag}Location')

        # _<LocationList>_____<Location>____<Address>__________________________________________

        nodes_parsed = node_location.find(f'{tag}Address').find(f'{tag}ParsedList').findall(f'{tag}Parsed')
        for node_parsed in nodes_parsed:
            if node_parsed.find(f'{tag}FullStreetName') is not None:
                self.FullStreetName = node_parsed.find(f'{tag}FullStreetName').text
            if node_parsed.find(f'{tag}HouseNumber') is not None:
                self.HouseNumber = node_parsed.find(f'{tag}HouseNumber').text
            if node_parsed.find(f'{tag}CountryCode') is not None:
                self.CountryCode = node_parsed.find(f'{tag}CountryCode').text
            if node_parsed.find(f'{tag}PostalCode') is not None:
                self.PostalCode = node_parsed.find(f'{tag}PostalCode').text
            if node_parsed.find(f'{tag}Admin') is not None:
                admin_level = node_parsed.find(f'{tag}Admin').find(f'{tag}AdminLevel')
                if admin_level.find(f'{tag}Level2') is not None:
                    self.Level2 = admin_level.find(f'{tag}Level2').text
                if admin_level.find(f'{tag}Level3') is not None:
                    self.Level3 = admin_level.find(f'{tag}Level3').text
                if admin_level.find(f'{tag}Level4') is not None:
                    self.Level4 = admin_level.find(f'{tag}Level4').text
                if admin_level.find(f'{tag}Level5') is not None:
                    self.Level5 = admin_level.find(f'{tag}Level5').text
            # 对于多个parsed信息，如果后一个的default language不是ture，会覆盖掉前一个
            if node_parsed.get('defaultLanguage') == 'true':
                break


        # _<LocationList>_____<Location>____<GeoPositionList>__________________________________

        nodes_GeoPosition = node_location.find(f'{tag}GeoPositionList').findall(f'{tag}GeoPosition')
        for node_GeoPosition in nodes_GeoPosition:
            if node_GeoPosition.get('type').upper() == 'ROUTING':
                self.GeoPosition_Routing_lat = node_GeoPosition.find(f'{tag}Latitude').text
                self.GeoPosition_Routing_lon = node_GeoPosition.find(f'{tag}Longitude').text
            elif node_GeoPosition.get('type').upper() == 'DISPLAY':
                self.GeoPosition_Display_lat = node_GeoPosition.find(f'{tag}Latitude').text
                self.GeoPosition_Display_lon = node_GeoPosition.find(f'{tag}Longitude').text
            else:
                LogUtils.warning('GeoPositionList type [%s] has miss match!' % node_GeoPosition.get('type').upper())

        # _<LocationList>_____<Location>____<MapReferenceList>__________________________________

        node_Map = node_location.find(f'{tag}MapReferenceList').find(f'{tag}MapReference').find(f'{tag}Map')
        self.MapVersion = node_Map.get('version')
        self.linkPvid = node_Map.find(f'{tag}Link').get('linkPvid')
        if node_Map.find(f'{tag}PointAddressPvid') is not None:
            self.PointAddressPvid = node_Map.find(f'{tag}PointAddressPvid').text

        # _<LocationList>_____<Location>____<AdditionalData>____________________________________

        nodes_AdditionalData = node_location.findall(f'{tag}AdditionalData')
        for node_AdditionalData in nodes_AdditionalData:
            if node_AdditionalData.get('key') == 'AdminLevel5Id':
                self.AdminLevel5Id = node_AdditionalData.text
            elif node_AdditionalData.get('key') == 'AdminLevel4Id':
                self.AdminLevel4Id = node_AdditionalData.text
            elif node_AdditionalData.get('key') == 'AdminLevel3Id':
                self.AdminLevel3Id = node_AdditionalData.text
            elif node_AdditionalData.get('key') == 'AdminLevel2Id':
                self.AdminLevel2Id = node_AdditionalData.text
            elif node_AdditionalData.get('key') == 'MapId':
                self.MapId = node_AdditionalData.text
            else:
                pass
        # =<Identity>======================================================================
        node_Identity = ele.find(f'{tag}Identity')
        if node_Identity is not None:
            node_PlaceID = node_Identity.find(f'{tag}PlaceId')
            if node_PlaceID is not None:
                self.PlaceID = node_PlaceID.text
        # =<Content>=======================================================================
        # _<Content>_____<Base>____________________________________________________________

        node_Base = ele.find(f'{tag}Content').find(f'{tag}Base')
        self.BaseText = node_Base.find(f'{tag}NameList').find(f'{tag}Name').find(f'{tag}TextList').find(
            f'{tag}Text').find(
            f'{tag}BaseText').text
        for category in node_Base.find(f'{tag}CategoryList').findall(f'{tag}Category'):
            if category.get('categorySystem').lower() == 'navteq-lcms':
                self.lcms_CategoryId = category.find(f'{tag}CategoryId').text  # 这个怎么没有
            elif category.get('categorySystem').lower() == 'navteq-poi':
                self.poi_CategoryId = category.find(f'{tag}CategoryId').text  # 这个怎么没有
            else:
                pass
        # _<Content>_____<Base>____<ContactList>__________________________________________

        node_contactlist = node_Base.find(f'{tag}ContactList')
        if node_contactlist is not None:
            nodes_contact = node_contactlist.findall(f'{tag}Contact')
            for node_contact in nodes_contact:
                if node_contact.get('type').upper() == 'PHONE':
                    try:
                        self.StandardNumber += node_contact.find(f'{tag}AdditionalContactInfo').find(
                            f'{tag}StandardNumber').text + '\n'
                    except Exception as err:
                        LogUtils.error(
                            '有PHONE节点但是无法找到AdditionalContactInfo-StandardNumber：[country:%s,lat:%s,lon:%s]' % (
                                self.CountryCode, self.GeoPosition_Display_lat, self.GeoPosition_Display_lon))

        # _<Content>_____<Extended>________________________________________________________

        node_extended = ele.find(f'{tag}Content').find(f'{tag}Extended')
        if node_extended is not None:
            node_hours_of_operation_list = node_extended.find(f'{tag}HoursOfOperationList')
            if node_hours_of_operation_list is not None:
                nodes_hours_of_operation = node_hours_of_operation_list.findall(f'{tag}HoursOfOperation')
                for node_hours_of_operation in nodes_hours_of_operation:
                    node_Open24x7Flag = node_hours_of_operation.find(f'{tag}Open24x7Flag')
                    if node_Open24x7Flag is not None:
                        self.Open24x7Flag = node_Open24x7Flag.text
                    node_OperatingTimeList = node_hours_of_operation.find(f'{tag}OperatingTimeList')
                    if node_OperatingTimeList is not None:
                        nodes_OperatingTime = node_OperatingTimeList.findall(f'{tag}OperatingTime')
                        for node_OperatingTime in nodes_OperatingTime:
                            opentime = ''
                            closetime = ''
                            node_OpeningTime = node_OperatingTime.find(f'{tag}OpeningTime')
                            if node_OpeningTime is not None:
                                opentime = node_OpeningTime.text
                            node_ClosingTime = node_OperatingTime.find(f'{tag}ClosingTime')
                            if node_ClosingTime is not None:
                                closetime = node_ClosingTime.text
                            self.OpenTime += node_OperatingTime.get('dayOfweek') + f':{opentime}-{closetime}\n'

        # _<Content>_____<Rich>____________________________________________________________

        for attr in ele.find(f'{tag}Content').find(f'{tag}Rich').find(f'{tag}AdditionalAttributeList').findall(
                f'{tag}AdditionalAttribute'):
            if attr.get('attributeType').upper() == 'PORT':
                for attrs in attr.findall(f'{tag}Attribute'):
                    if attrs.get('key') == 'ConnectorType':
                        if attrs.text:
                            self.ConnectorType += attrs.text
                    elif attrs.get('key') == 'NumberOfPorts':
                        if attrs.text:
                            self.NumberOfPorts += attrs.text
                    elif attrs.get('key') == 'MaxPowerLevel':
                        if attrs.text:
                            self.MaxPowerLevel += attrs.text
                    else:
                        pass
                self.ConnectorType += '\n'
                self.NumberOfPorts += '\n'
                self.MaxPowerLevel += '\n'

    def load_xml_path(self, xml_path: str):
        self.XML_PATH = xml_path

    def load_line_index(self, line_index: int):
        self.Line_Index = line_index
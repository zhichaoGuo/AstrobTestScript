from xml.etree.ElementTree import Element


class EVChargePoint:
    AllAttr = [
        'CountryCode',
        'POI_Name',
        'Contact',  # 组合
        'TotalNumberOfConnectors',
        'ConnectorTypeName',  # 组合
        'CustomerConnectorName',  # 组合
        'NumberOfConnectors',  # 组合
        'MaxPowerLevel',  # 组合
        'Voltage',  # 组合
        'NumberOfPhases',  # 组合
        'Flow',  # 组合
        'House_Number',
        'StreetName',
        'PlaceLevel2',
        'PlaceLevel3',
        'PlaceLevel4',
        'Entry_Point_Lat',
        'Entry_Point_Lon',
        'Display_Point_Lat',
        'Display_Point_Lat',
        'Open_24_Hours',
        'Private_Access',
        'HoursOfOperation',  # 组合
        'POI_Entity_ID'
    ]


    def __init__(self, ele: Element):
        for attr in self.AllAttr:
            setattr(self, attr, '')
        node_identity = ele.find('Identity')
        self.POI_Entity_ID = node_identity.find('POI_Entity_ID').text
        self.POI_Name = get_name(node_identity.find('Names'))
        node_locations = ele.find('Locations')

        nodes_location = node_locations.findall('Location')
        for node_location in nodes_location:
            node_type = node_location.get('Type')
            if node_type == 'Entry Point':
                (self.House_Number,
                 self.StreetName,
                 self.PlaceLevel2,
                 self.PlaceLevel3,
                 self.PlaceLevel4,
                 self.CountryCode,
                 self.Entry_Point_Lat,
                 self.Entry_Point_Lon) = parse_entry_point(node_location)
            elif node_type == 'Display Location':
                self.Display_Point_Lat, self.Display_Point_Lon = parse_display_point(node_location)
            else:
                print('解析Location节点失败，存在未知类型：%s' % node_type)
        node_contacts = ele.find('Contacts')
        if node_contacts:
            self.Contact = get_contact(node_contacts)
        node_fuels = ele.find('Products_Services').find('Fuels')
        if len(node_fuels.findall('Electric')) > 1:
            raise AttributeError('[%s]Fuels节点具有不止一个Electric子节点！' % self.POI_Entity_ID)
        node_electric = node_fuels.find('Electric')
        self.TotalNumberOfConnectors = node_electric.get('TotalNumberOfConnectors')
        (self.ConnectorTypeName,
         self.CustomerConnectorName,
         self.NumberOfConnectors,
         self.MaxPowerLevel,
         self.Voltage,
         self.NumberOfPhases,
         self.Flow) = parse_electric(node_electric)
        self.Open_24_Hours = ele.find('Products_Services').find('Open_24_Hours').text
        self.Private_Access = ele.find('Details').find('Private_Access').text
        self.HoursOfOperation = ''
        if self.Open_24_Hours != 'true':
            node_hours_of_operation = ele.find('Details').find('HoursOfOperation')
            if node_hours_of_operation:
                self.HoursOfOperation = get_hours_of_operation(node_hours_of_operation)


def get_name(ele: Element):
    if ele:
        for node in ele.findall('POI_Name'):
            if node.get('Type') == 'Official':
                for node_text in node.findall('Text'):
                    if not node_text.get('Trans_Type'):
                        return node_text.text
    return ''


def parse_entry_point(ele: Element):
    House_Number = ''
    StreetName = ''
    PlaceLevel2 = ''
    PlaceLevel3 = ''
    PlaceLevel4 = ''
    CountryCode = ''
    Entry_Point_Lat = ''
    Entry_Point_Lon = ''
    node_parsed_address = ele.find('Address').find('ParsedAddress')
    node_parsed_street_address = node_parsed_address.find('ParsedStreetAddress')
    if node_parsed_street_address:
        node_address_number = node_parsed_street_address.find('Address_Number')
        if node_address_number:
            House_Number = node_address_number.find('House_Number').text
        node_parsed_street_name = node_parsed_street_address.find('ParsedStreetName')
        if node_parsed_street_name:
            StreetName = node_parsed_street_name.find('StreetName').text
    node_parsed_place = node_parsed_address.find('ParsedPlace')
    for node in node_parsed_place.findall('PlaceLevel2'):
        if node.get('Language_Code'):
            PlaceLevel2 = node.text
        else:
            print('PlaceLevel2拥有翻译语言：%s' % node.get('Trans_Type'))
    for node in node_parsed_place.findall('PlaceLevel3'):
        if node.get('Language_Code'):
            PlaceLevel3 = node.text
        else:
            print('PlaceLevel3拥有翻译语言：%s' % node.get('Trans_Type'))
    for node in node_parsed_place.findall('PlaceLevel4'):
        if node.get('Language_Code'):
            PlaceLevel4 = node.text
        else:
            print('PlaceLevel4拥有翻译语言：%s' % node.get('Trans_Type'))
    CountryCode = node_parsed_address.find('CountryCode').text
    node_GeoPosition = ele.find('GeoPosition')
    Entry_Point_Lat = node_GeoPosition.find('Latitude').text
    Entry_Point_Lon = node_GeoPosition.find('Longitude').text

    return House_Number, StreetName, PlaceLevel2, PlaceLevel3, PlaceLevel4, CountryCode, Entry_Point_Lat, Entry_Point_Lon


def parse_display_point(ele: Element):
    node_GeoPosition = ele.find('GeoPosition')
    Point_Lat = node_GeoPosition.find('Latitude').text
    Point_Lon = node_GeoPosition.find('Longitude').text

    return Point_Lat, Point_Lon


def get_contact(ele: Element):
    phone = ''
    nodes_contact = ele.findall('Contact')
    for node in nodes_contact:
        node_number = node.find('Number')
        if node_number.get('Type') == 'Phone Number':
            phone += f'{node_number.text}\r\n'
        else:
            print('还有其他类型的联系方式：%s' % node_number.get('Type'))

    return phone


def parse_electric(ele: Element):
    ConnectorTypeName = ''
    CustomerConnectorName = ''
    NumberOfConnectors = ''
    MaxPowerLevel = ''
    Voltage = ''
    NumberOfPhases = ''
    Flow = ''
    for node in ele.findall('ConnectorType'):
        ConnectorTypeName += f'{node.find("ConnectorTypeName").text}\r\n'
        CustomerConnectorName += f'{node.find("CustomerConnectorName").text}\r\n'
        NumberOfConnectors += f'{node.find("NumberOfConnectors").text}\r\n'
        MaxPowerLevel += f'{node.find("MaxPowerLevel").text}\r\n'
        node_voltage = node.find('Voltage')
        Voltage += f'{node_voltage.find("Min").text}-{node_voltage.find("Max").text}\r\n'
        NumberOfPhases += f'{node.find("NumberOfPhases").text}\r\n'
        Flow += f'{node.find("Flow").text}\r\n'
    return ConnectorTypeName, CustomerConnectorName, NumberOfConnectors, MaxPowerLevel, Voltage, NumberOfPhases, Flow


def get_hours_of_operation(ele: Element):
    operation = ''
    for node in ele.findall('DayOfWeek'):
        operation += f'{node.get("DayType")}:{node.find("OpeningHours").text}-{node.find("ClosingHours").text}\r\n'
    return operation

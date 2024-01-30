from xml.etree.ElementTree import Element

from AstrobTestTool.app.Utils import LogManager


class EVChargePoint:
    AllAttr = [
        'CountryCode',
        'Official_Name',
        'Synonym_Name',
        'index',
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
        'PostalCode',
        'PlaceLevel2',
        'PlaceLevel3',
        'PlaceLevel4',
        'Entry_Point_Lat',
        'Entry_Point_Lon',
        'Display_Point_Lat',
        'Display_Point_Lon',
        'Open_24_Hours',
        'Private_Access',
        'HoursOfOperation',  # 组合
        'POI_Entity_ID'
    ]

    def __init__(self, ele: Element):
        self.index = None
        for attr in self.AllAttr:
            setattr(self, attr, '')
        node_identity = ele.find('Identity')
        self.POI_Entity_ID = node_identity.find('POI_Entity_ID').text
        self.Official_Name, self.Synonym_Name = get_name(node_identity.find('Names'))
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
                 self.Entry_Point_Lon,
                 self.PostalCode) = parse_entry_point(node_location)
            elif node_type == 'Display Location':
                self.Display_Point_Lat, self.Display_Point_Lon = parse_display_point(node_location)
            else:
                LogManager.error('解析Location节点失败，存在未知类型：%s' % node_type)
        node_contacts = ele.find('Contacts')
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
        node_details = ele.find('Details')
        if node_details:
            node_hours_of_operation = node_details.find('HoursOfOperation')
            self.HoursOfOperation = get_hours_of_operation(node_hours_of_operation)

    def add_index(self, index: int):
        self.index = index


def get_name(ele: Element):
    """
    对MEA SAU存在英语和阿语 官方名称和同义词 一共四种 分别放在<POI_Name>中以Language_Code 和 Type 进行区分
    对MEA ISR存在希伯来语和音译语言 一共两种 放在<POI_Name>中不同的<Text>中以Trans_Type进行区分
    对EU ESP 存在官方名称和同义词 一共两种 分别放在<POI_Name>中以Type进行区分
    """
    _name = ''
    _name1 = ''
    if ele:
        for node in ele.findall('POI_Name'):
            if node.get('Type') == 'Official':
                for node_text in node.findall('Text'):
                    # Trans_Type 拼在后面，正常语言拼在前面
                    if node_text.get('Trans_Type'):
                        _name += f'{node_text.text}\r\n'
                    else:
                        _name = f'{node_text.text}\r\n{_name}'
            if node.get('Type') == 'Synonym':
                for node_text in node.findall('Text'):
                    if node_text.get('Trans_Type'):
                        _name1 += f'{node_text.text}\r\n'
                    else:
                        _name1 = f'{node_text.text}\r\n{_name1}'
    return remove_rn(_name), remove_rn(_name1)


def parse_entry_point(ele: Element):
    House_Number = ''
    StreetName = ''
    PlaceLevel2 = ''
    PlaceLevel3 = ''
    PlaceLevel4 = ''
    CountryCode = ''
    Entry_Point_Lat = ''
    Entry_Point_Lon = ''
    PostalCode = ''
    """
    对于MEA SAU street name存在英语和阿语两种 
        存在<Address><ParsedAddress><ParsedStreetAddress><ParsedStreetName><StreetName>下以Language_Code属性区分
    对于MEA ISR street name存在希伯来语和音译语言 
        存在<Address><ParsedAddress><ParsedStreetAddress><ParsedStreetName>下以<StreetName>和<Trans_ParsedStreetName><StreetName>
    对于EU ESP street name 
        存在<Actual_Address_Components><Actual_Street_Name><Actual_Street_Name_Base>中
    """
    node_parsed_address = ele.find('Address').find('ParsedAddress')
    node_parsed_street_address = node_parsed_address.find('ParsedStreetAddress')
    if node_parsed_street_address:
        node_address_number = node_parsed_street_address.find('Address_Number')
        if node_address_number:
            House_Number = node_address_number.find('House_Number').text
        nodes_parsed_street_name = node_parsed_street_address.findall('ParsedStreetName')
        for node_parsed_street_name in nodes_parsed_street_name:
            StreetName += f"{node_parsed_street_name.find('StreetName').text}\r\n"
            node_trans_parsed_street_name = node_parsed_street_name.find('Trans_ParsedStreetName')
            if node_trans_parsed_street_name:
                StreetName += f"{node_trans_parsed_street_name.find('StreetName').text}\r\n"
    node_actual_address_components = ele.find('Actual_Address_Components')
    if node_actual_address_components:
        if len(node_actual_address_components.find('Actual_Street_Name').findall('Actual_Street_Name_Base'))>1:
            LogManager.error('Actual_Street_Name_Base 数量大于1，需要重构此处解析！')
        StreetName += f"{node_actual_address_components.find('Actual_Street_Name').find('Actual_Street_Name_Base').text}\r\n"
    StreetName = remove_rn(StreetName)
    """
    对MEA SAU place level 有阿语和英语两种 存在Language_Code区别
    对MEA ISR place level 有希伯来语和音译语言两种 存在Language_Code和Trans_Type区别
    """
    node_parsed_place = node_parsed_address.find('ParsedPlace')
    for node in node_parsed_place.findall('PlaceLevel2'):
        if node.get('Language_Code'):
            PlaceLevel2 += f"{node.get('Language_Code')}:{node.text}\r\n"
        elif node.get('Trans_Type'):
            PlaceLevel2 += f"{node.get('Trans_Type')}:{node.text}\r\n"
        else:
            LogManager.warning('未登记PlaceLevel2：%s' % node.text)
    PlaceLevel2 = remove_rn(PlaceLevel2)
    for node in node_parsed_place.findall('PlaceLevel3'):
        if node.get('Language_Code'):
            PlaceLevel3 += f"{node.get('Language_Code')}:{node.text}\r\n"
        elif node.get('Trans_Type'):
            PlaceLevel3 += f"{node.get('Trans_Type')}:{node.text}\r\n"
        else:
            LogManager.warning('未登记PlaceLevel3：%s' % node.text)
    PlaceLevel3 = remove_rn(PlaceLevel3)
    for node in node_parsed_place.findall('PlaceLevel4'):
        if node.get('Language_Code'):
            PlaceLevel4 += f"{node.get('Language_Code')}:{node.text}\r\n"
        elif node.get('Trans_Type'):
            PlaceLevel4 += f"{node.get('Trans_Type')}:{node.text}\r\n"
        else:
            LogManager.warning('未登记PlaceLevel4：%s' % node.text)
    node_postal_code = node_parsed_address.find('PostalCode')
    if node_postal_code:
        PostalCode = node_postal_code.find('NT_Postal').text
    PlaceLevel4 = remove_rn(PlaceLevel4)
    CountryCode = node_parsed_address.find('CountryCode').text
    node_GeoPosition = ele.find('GeoPosition')
    Entry_Point_Lat = node_GeoPosition.find('Latitude').text
    Entry_Point_Lon = node_GeoPosition.find('Longitude').text

    return House_Number, StreetName, PlaceLevel2, PlaceLevel3, PlaceLevel4, CountryCode, Entry_Point_Lat, Entry_Point_Lon, PostalCode


def parse_display_point(ele: Element):
    node_GeoPosition = ele.find('GeoPosition')
    Point_Lat = node_GeoPosition.find('Latitude').text
    Point_Lon = node_GeoPosition.find('Longitude').text
    return Point_Lat, Point_Lon


def get_contact(ele: Element):
    phone = ''
    if ele:
        nodes_contact = ele.findall('Contact')
        for node in nodes_contact:
            node_number = node.find('Number')
            if node_number.get('Type') == 'Phone Number':
                phone += f'{node_number.text}\r\n'
            else:
                LogManager.warning('还有其他类型的联系方式：%s' % node_number.get('Type'))
    return remove_rn(phone)


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
    return (remove_rn(ConnectorTypeName),
            remove_rn(CustomerConnectorName),
            remove_rn(NumberOfConnectors),
            remove_rn(MaxPowerLevel),
            remove_rn(Voltage),
            remove_rn(NumberOfPhases), remove_rn(Flow))


def remove_rn(input_str: str):
    if input_str.endswith('\r\n'):
        return input_str[:-2]
    else:
        return input_str


def get_hours_of_operation(ele: Element):
    operation = ''
    if ele:
        for node in ele.findall('DayOfWeek'):
            operation += f'{node.get("DayType")}:{node.find("OpeningHours").text}-{node.find("ClosingHours").text}\r\n'
    return remove_rn(operation)

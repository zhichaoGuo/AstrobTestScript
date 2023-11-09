from QueryScript import QueryCapital, QueryAllCountry, QueryAllCity, QueryAllPoi, QueryAllPtaddr, QueryTotal, QueryLevel


class MapDBInfo:
    def __init__(self):
        pass


class CountryInfo:
    # 此处定义Excel表格的内容
    AllAttr = [
        'ISO_COUNTRY_CODE',
        'COUNTRY_ID',
        'NAME',
        'CAPITAL',
        'TOTAL',
        'LEVEL',
        'LANGUAGE',
        'DRIVING',
        'NAME_LANGUAGE'
    ]

    def __init__(self, country_obj: QueryAllCountry.QueryResults, capital, total, level):
        for attr in self.AllAttr:
            setattr(self, attr, '')
        self.ISO_COUNTRY_CODE = country_obj.ISO_COUNTRY_CODE
        self.COUNTRY_ID = country_obj.COUNTRY_ID
        self.NAME = country_obj.NAME
        self.CAPITAL = ''
        self.TOTAL = ''
        self.LEVEL = ''
        self.LANGUAGE = country_obj.LANGUAGE_CODE
        self.DRIVING = country_obj.DRIVING_SIDE
        self.NAME_LANGUAGE = country_obj.NAME_LANGUAGE
        if capital:
            self.load_capital(capital[0])
        if total:
            self.load_total(total[0])
        if level:
            self.load_level(level[0])

    def load_capital(self, capital_obj: QueryCapital.QueryResults):
        self.CAPITAL = capital_obj.NAME

    def load_total(self, total_obj: QueryTotal.QueryResults):
        self.TOTAL = total_obj.TOTAL

    def load_level(self, level_obj: QueryLevel.QueryResults):
        self.LEVEL = level_obj.LEVEL


class CountryInfos:
    # 此类用于放置一个国家不同语言的数据
    """
    eg:
        self data = {   "ENG":country_info_eng,
                        "ARA":country_info_ara}
        self default_language_info = country_info_eng
    """
    def __init__(self, country_info: CountryInfo):
        self.data = {country_info.NAME_LANGUAGE: country_info}
        self.default_language_info = country_info

    def load_other_language(self, country_info: CountryInfo):
        self.data[country_info.NAME_LANGUAGE] = country_info

    def get_country_by_language(self, language_code: str):
        if language_code in self.data.keys():
            return self.data[language_code]
        else:
            return None


class CityInfo:
    # 此处定义Excel表格的内容
    AllAttr = [
        'CITY_NAME',
        'POI_ID',
        'NAMED_PLACE_ID',
        'ORDER1_ID',
        'ORDER2_ID',
        'ORDER8_ID',
        'BUILTUP_ID',
        'POPULATION',
        'CAPITAL_COUNTRY',
        'CAPITAL_ORDER1',
        'CAPITAL_ORDER8',
        'NAMED_PLACE_TYPE',
        'LANGUAGE_CODE'
    ]

    def __init__(self, city_obj: QueryAllCity.QueryResults):
        self.CITY_NAME = city_obj.CITY_NAME
        if city_obj.CAPITAL_ORDER1 == 'Y':
            self.POI_ID = city_obj.ORDER1_ID
        else:
            self.POI_ID = city_obj.CITY_POI_ID
        self.NAMED_PLACE_ID = city_obj.NAMED_PLACE_ID
        self.ORDER1_ID = city_obj.ORDER1_ID
        self.ORDER2_ID = city_obj.ORDER2_ID
        self.ORDER8_ID = city_obj.ORDER8_ID
        self.BUILTUP_ID = city_obj.BUILTUP_ID
        self.POPULATION = city_obj.POPULATION
        self.CAPITAL_COUNTRY = city_obj.CAPITAL_COUNTRY
        self.CAPITAL_ORDER1 = city_obj.CAPITAL_ORDER1
        self.CAPITAL_ORDER8 = city_obj.CAPITAL_ORDER8
        self.NAMED_PLACE_TYPE = city_obj.NAMED_PLACE_TYPE
        self.LANGUAGE_CODE = city_obj.LANGUAGE_CODE


class CityInfos:
    # 此类用于放置一个城市不同语言的数据
    def __init__(self, city_info: CityInfo):
        self.data = {city_info.LANGUAGE_CODE: city_info}
        self.default_language_info = city_info

    def load_other_language(self, city_info: CityInfo):
        self.data[city_info.LANGUAGE_CODE] = city_info

    def get_city_by_language(self, language_code: str):
        if language_code in self.data.keys():
            return self.data[language_code]
        else:
            return None


class PoiInfo:
    # 此处定义Excel表格的内容
    AllAttr = ['POI_NAME',
               'POI_ID',
               'house_number',
               'street_name',
               'POI_OWN',
               'postal_code',
               'PHONE',
               'Lon',
               'Lat',
               'LINK_ID',
               'LANGUAGE_POI',
               'ORDER1_ID',
               'ORDER2_ID',
               'ORDER8_ID',
               'BUILTUP_ID',
               'CAT_ID',
               'db_name']

    def __init__(self, poi_obj: QueryAllPoi.QueryResults):
        self.POI_NAME = poi_obj.POI_NAME
        self.POI_ID = poi_obj.POI_ID
        self.house_number = poi_obj.house_number
        self.street_name = poi_obj.street_name
        self.POI_OWN = poi_obj.POI_OWN
        self.postal_code = poi_obj.postal_code
        self.PHONE = poi_obj.PHONE
        self.Lon = poi_obj.Lon
        self.Lat = poi_obj.Lat
        self.LINK_ID = poi_obj.LINK_ID
        self.LANGUAGE_POI = poi_obj.LANGUAGE_POI
        self.ORDER1_ID = poi_obj.ORDER1_ID
        self.ORDER2_ID = poi_obj.ORDER2_ID
        self.ORDER8_ID = poi_obj.ORDER8_ID
        self.BUILTUP_ID = poi_obj.BUILTUP_ID
        self.CAT_ID = poi_obj.CAT_ID
        self.db_name = poi_obj.db_name


class PoiInfos:
    # 此类用于放置一个poi不同语言的数据
    def __init__(self, poi_info: PoiInfo):
        self.data = {poi_info.LANGUAGE_POI: poi_info}

    def load_other_language(self, poi_info: PoiInfo):
        self.data[poi_info.LANGUAGE_POI] = poi_info

    def get_city_by_language(self, language_code: str):
        if language_code in self.data.keys():
            return self.data[language_code]
        else:
            return None


class PtaddrInfo:
    AllAttr = ['ROAD_NAME',
               'ADDRESS',
               'SIDE',
               'ADDRESS_POINT_ID',
               'ROAD_OWNER',
               'PD',
               'LON',
               'LAT',
               'EdgeID',
               'Road_language',
               'BUILDING_NAME',
               'admin_place_id',
               'admin_order',
               'db_name']

    def __init__(self, ptaddr_obj: QueryAllPtaddr.QueryResults):
        self.ROAD_NAME = ptaddr_obj.ROAD_NAME
        self.ADDRESS = ptaddr_obj.ADDRESS
        self.SIDE = ptaddr_obj.SIDE
        self.ADDRESS_POINT_ID = ptaddr_obj.ADDRESS_POINT_ID
        self.ROAD_OWNER = ptaddr_obj.ROAD_OWNER
        self.PD = ptaddr_obj.PD
        self.LON = ptaddr_obj.LON
        self.LAT = ptaddr_obj.LAT
        self.EdgeID = ptaddr_obj.EdgeID
        self.Road_language = ptaddr_obj.Road_language
        self.BUILDING_NAME = ptaddr_obj.BUILDING_NAME
        self.admin_place_id = ptaddr_obj.admin_place_id
        self.admin_order = ptaddr_obj.admin_order
        self.db_name = ptaddr_obj.db_name


class PtaddrInfos:
    # 此类用于放置一个poi不同语言的数据
    def __init__(self, ptaddr_info: PtaddrInfo):
        self.data = {ptaddr_info.Road_language: ptaddr_info}
        self.default_language_info = ptaddr_info

    def load_other_language(self, ptaddr_info: PtaddrInfo):
        ptaddr_info.LON = self.default_language_info.LON
        ptaddr_info.LAT = self.default_language_info.LAT
        self.data[ptaddr_info.Road_language] = ptaddr_info

    def get_ptaddr_by_language(self, language_code: str):
        if language_code in self.data.keys():
            return self.data[language_code]
        else:
            return None



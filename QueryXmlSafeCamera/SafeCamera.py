from xml.etree.ElementTree import Element

from Utils import LogUtils


class CameraType:
    TYPE_RED_LIGHT = 'REDLIGHT'
    TYPE_SPEED = 'SPEED'
    TYPE_RED_LIGHT_SPEED = 'REDLIGHTANDSPEED'
    TYPE_SECTION_START = 'SECTIONSTART'
    TYPE_SECTION_END = 'SECTIONEND'
    TYPE_BUSLANE = 'BUSLANE'
    TYPE_DISTANCE = 'DISTANCE'
    # 这部分转换代码没看到
    TYPE_DANGER_ZONE_START = 'DANGERZONESTART'
    TYPE_DANGER_ZONE_END = 'DANGERZONEEND'
    ALL_TYPE = [TYPE_RED_LIGHT, TYPE_SPEED, TYPE_RED_LIGHT_SPEED,
                TYPE_SECTION_START, TYPE_SECTION_END,
                TYPE_BUSLANE, TYPE_DISTANCE,
                TYPE_DANGER_ZONE_START, TYPE_DANGER_ZONE_END]


class SafeCamera:
    AllAttr = ['ISO_COUNTRY_CODE'
        , 'POI_Entity_ID',  # cid
               'Latitude',  # lat
               'Longitude',  # lon
               'LinkID',  # EID
               'CameraType',  # ctype
               'FixtureStatus',  # status
               'SpeedLimit',  # spd
               'Unit',  # unit
               'DrivingDirection',  # cdir
               'LinkHeading']  # ldir

    def __init__(self, ele: Element):
        for attr in self.AllAttr:
            setattr(self, attr, '')
        self.ISO_COUNTRY_CODE = ele.get('ISO_COUNTRY_CODE')
        node_Identity = ele.find('Identity')
        node_POI_Entity_ID = node_Identity.find('POI_Entity_ID')
        self.POI_Entity_ID = node_POI_Entity_ID.text
        node_Location = ele.find('Locations').find('Location')
        node_GeoPosition = node_Location.find('GeoPosition')
        self.Latitude = node_GeoPosition.find('Latitude').text
        self.Longitude = node_GeoPosition.find('Longitude').text
        node_MapLinkID = node_Location.find('MapLinkID')
        self.LinkID = node_MapLinkID.find('LinkID').text
        # self.Side_of_Street = node_MapLinkID.find('Side_of_Street').text
        # self.Percent_from_RefNode = node_MapLinkID.find('Percent_from_RefNode').text
        node_Details = ele.find('Details')
        if len(node_Details.findall('Camera')) > 1:
            LogUtils.warning(f"{self.ISO_COUNTRY_CODE}:{self.POI_Entity_ID} has more than one camera!")
        node_Camera = node_Details.find('Camera')
        self.CameraType = node_Camera.find('CameraType').text
        self.FixtureStatus = node_Camera.find('FixtureStatus').text
        node_SpeedLimit = node_Camera.find('SpeedLimit')
        if node_SpeedLimit is not None:
            self.SpeedLimit = node_SpeedLimit.text
            self.Unit = node_SpeedLimit.get('Unit')
        node_DrivingDirection = node_Camera.find('DrivingDirection')
        if node_DrivingDirection is not None:
            self.DrivingDirection = node_DrivingDirection.text
            self.LinkHeading = node_DrivingDirection.get('LinkHeading')

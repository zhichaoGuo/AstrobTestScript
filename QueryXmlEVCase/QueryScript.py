from QuerySqlDataCase.QueryScript import QueryResultObj, QueryObj


class QueryPlaceInfo(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['OWN',
               'AXID',
               'RNA',
               'STREET_TYPE']

    def __init__(self, link_id: str):
        self.link_id = link_id

    def script(self) -> str:
        """
        测试特例：APAC eid=1012394252 没有街道名
        APAC 1110851474 有三条路名
        MEA 1116629366 双语RNA OWN
        """
        script = f'''
        SELECT --*
            RDF_FEATURE_NAME.NAME AS OWN,
            RDF_LINK.LEFT_ADMIN_PLACE_ID AS AXID,
            RDF_ROAD_NAME.STREET_NAME AS RNA,
            -- RDF_ROAD_NAME.LANGUAGE_CODE,
            RDF_ROAD_NAME.STREET_TYPE
        FROM
            RDF_LINK
            INNER JOIN RDF_FEATURE_NAMES ON RDF_LINK.LEFT_ADMIN_PLACE_ID = RDF_FEATURE_NAMES.FEATURE_ID
                and RDF_LINK.LINK_ID = '{self.link_id}'
            INNER JOIN RDF_FEATURE_NAME on RDF_FEATURE_NAME.NAME_ID = RDF_FEATURE_NAMES.NAME_ID
                AND RDF_FEATURE_NAMES.NAME_TYPE = 'B'
                AND RDF_FEATURE_NAMES.IS_EXONYM = 'N'
            LEFT JOIN RDF_ROAD_LINK ON RDF_LINK.LINK_ID = RDF_ROAD_LINK.LINK_ID
            LEFT JOIN RDF_ROAD_NAME ON RDF_ROAD_LINK.ROAD_NAME_ID = RDF_ROAD_NAME.ROAD_NAME_ID
        where (RDF_FEATURE_NAME.LANGUAGE_CODE = RDF_ROAD_NAME.LANGUAGE_CODE
            or RDF_ROAD_NAME.STREET_NAME IS NULL)
        ORDER BY
            ROUTE_TYPE ASC,
            IS_NAME_ON_ROADSIGN DESC
                '''
        return script


class QueryISOCountryCode(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ISO_COUNTRY_CODE']

    def __init__(self):
        pass

    def script(self) -> str:
        script = f'''
            SELECT ISO_COUNTRY_CODE FROM RDF_COUNTRY
            '''
        return script

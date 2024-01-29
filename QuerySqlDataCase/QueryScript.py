class QueryObj:
    class QueryResults:
        arg = []

        def __init__(self, ele: tuple):
            pass

    @staticmethod
    def script() -> str:
        script = f'''
        '''
        return script


class QueryResultObj:
    arg = []

    def __init__(self, ele: tuple):
        # 查询结果应与定义的arg的长度一致
        if len(ele) != len(self.arg):
            raise AttributeError('查询结果长度与定义不符，请检查！')
        for i in range(len(self.arg)):
            setattr(self, self.arg[i], ele[i])


class QueryCountry(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ["ISO_COUNTRY_CODE",
               "COUNTRY_ID",
               "NAME",
               "CAPITAL",
               "TOTAL",
               "LEVEL",
               "LANGUAGE_CODE",
               "DRIVING",
               "NAME_LANGUAGE"]

    def __init__(self, iso_country_code: list, language_code: list):
        self.iso_country = ""
        self.language = ""
        if iso_country_code:
            country_str = ""
            for c in iso_country_code:
                if country_str is not "":
                    country_str += f","
                country_str += f"'{c}'"
            self.iso_country = f"AND RC.ISO_COUNTRY_CODE IN ({country_str})"

        if language_code:
            language_str = ""
            for c in language_code:
                if language_str is not "":
                    language_str += f","
                language_str += f"'{c}'"
            self.language = f"AND RFN.LANGUAGE_CODE in ({language_str})"
        else:
            self.language = "AND RFN.LANGUAGE_CODE = RC.LANGUAGE_CODE"

    def script(self) -> str:
        script = f'''
            SELECT DISTINCT
                LT.ISO_COUNTRY_CODE,
                LT.COUNTRY_ID,
                LT.NAME,
                RT.NAME AS CAPITAL,
                TOTAL_TABLE.TOTAL,
                LEVEL_TABLE.LEVEL,
                LT.LANGUAGE_CODE,
                LT.DRIVING_SIDE AS DRIVING,
                LT.NAME_LANGUAGE
            FROM
                (SELECT DISTINCT
                    RAH.ISO_COUNTRY_CODE,
                    RC.LANGUAGE_CODE,
                    RAH.COUNTRY_ID,
                    RFN.NAME,
                    RFN.NAME_ID,
                    RFNS.IS_EXONYM,
                    RFNS.NAME_TYPE,
                    RFNS.OWNER,
                    RC.DRIVING_SIDE,
                    RFN.LANGUAGE_CODE AS NAME_LANGUAGE
                FROM
                    RDF_ADMIN_HIERARCHY RAH
                    LEFT JOIN RDF_FEATURE_NAMES RFNS ON RAH.ADMIN_PLACE_ID = RFNS.FEATURE_ID
                    LEFT JOIN RDF_FEATURE_NAME RFN ON RFNS.NAME_ID = RFN.NAME_ID
                    LEFT JOIN RDF_COUNTRY RC ON RAH.ISO_COUNTRY_CODE = RC.ISO_COUNTRY_CODE 
                WHERE
                    RAH.ADMIN_ORDER= '0' 
                    AND RFNS.NAME_TYPE= 'B' 
                    {self.language}
                    {self.iso_country}
                )LT
                LEFT JOIN 
                (SELECT
                    R.POI_ID,
                    R.COUNTRY_ID,
                    R.ISO_COUNTRY_CODE,
                    RFN.NAME,
                    RFN.LANGUAGE_CODE
                FROM
                    (SELECT 
                        POI_ID,
                        COUNTRY_ID,
                        ISO_COUNTRY_CODE,
                        NAMED_PLACE_ID
                    FROM 
                        RDF_CITY_POI
                    WHERE 
                        CAPITAL_COUNTRY = 'Y'
                    ) R
                    LEFT JOIN 
                        RDF_FEATURE_NAMES RFNS ON R.NAMED_PLACE_ID = RFNS.FEATURE_ID
                    LEFT JOIN 
                        RDF_FEATURE_NAME RFN ON RFNS.NAME_ID = RFN.NAME_ID
                    LEFT JOIN 
                        RDF_COUNTRY RC ON RC.ISO_COUNTRY_CODE = R.ISO_COUNTRY_CODE
                WHERE
                    NAME_TYPE = 'B'
                    {self.language}
                    {self.iso_country}
                )  RT ON LT.ISO_COUNTRY_CODE=RT.ISO_COUNTRY_CODE
                LEFT JOIN
                    (SELECT
                        ISO_COUNTRY_CODE,
                        COUNT ( * ) TOTAL
                    FROM
                        RDF_ADMIN_HIERARCHY
                    GROUP BY
                        ISO_COUNTRY_CODE
                    ) TOTAL_TABLE on LT.ISO_COUNTRY_CODE=TOTAL_TABLE.ISO_COUNTRY_CODE
                LEFT JOIN
                    (SELECT DISTINCT
                        ISO_COUNTRY_CODE,
                        COUNTRY_ID,
                        LEVEL=stuff(
                            (SELECT
                                '/'+ CAST(ADMIN_ORDER AS varchar(10))
                            FROM
                                (SELECT
                                    ISO_COUNTRY_CODE,
                                    COUNTRY_ID,
                                    ADMIN_ORDER 
                                FROM
                                    RDF_ADMIN_HIERARCHY
                                GROUP BY
                                    ISO_COUNTRY_CODE,
                                    COUNTRY_ID,
                                    ADMIN_ORDER 
                                ) AS A
                            WHERE 
                                ISO_COUNTRY_CODE = B.ISO_COUNTRY_CODE
                            GROUP BY
                                ADMIN_ORDER 
                            FOR XML PATH('') 
                            ),
                            1,
                            1,
                            '')
                    FROM
                        RDF_ADMIN_HIERARCHY B
                    GROUP BY
                        ISO_COUNTRY_CODE,
                        COUNTRY_ID,
                        ADMIN_ORDER 
                    ) LEVEL_TABLE ON LT.ISO_COUNTRY_CODE=LEVEL_TABLE.ISO_COUNTRY_CODE
                WHERE 
                    (RT.NAME IS NULL)
                    OR LT.NAME_LANGUAGE=RT.LANGUAGE_CODE
                ORDER BY
                    ISO_COUNTRY_CODE,
                    NAME_LANGUAGE
'''
        return script


class QueryCity(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['CITY_NAME',
               'CITY_POI_ID',
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
               'LANGUAGE_CODE',
               'IS_EXONYM',
               'NAME_LANGUAGE']

    def __init__(self, iso_country_code: str, language_code: list):
        self.iso_country_code = iso_country_code
        self.language = ""
        for c in language_code:
            if self.language is not "":
                self.language += f","
            self.language += f"'{c}'"

    def script(self) -> str:
        script = f'''
            SELECT 
                RDF_CITY_POI_NAME.NAME AS CITY_NAME,
                CITY_TABLE.POI_ID AS CITY_POI_ID,
                CITY_TABLE.NAMED_PLACE_ID,
                CITY_TABLE.ORDER1_ID,
                CITY_TABLE.ORDER2_ID,
                CITY_TABLE.ORDER8_ID,
                CITY_TABLE.BUILTUP_ID,
                CITY_TABLE.POPULATION,
                CITY_TABLE.CAPITAL_COUNTRY,
                CITY_TABLE.CAPITAL_ORDER1,
                CITY_TABLE.CAPITAL_ORDER8,
                CITY_TABLE.NAMED_PLACE_TYPE,
                CITY_TABLE.LANGUAGE_CODE,
                RDF_CITY_POI_NAMES.IS_EXONYM,
                RDF_CITY_POI_NAME.LANGUAGE_CODE AS NAME_LANGUAGE
            FROM
                (SELECT TOP 6 * 
                    FROM
                        RDF_CITY_POI RCP
                    WHERE
                        RCP.POPULATION IS NOT NULL
                        AND RCP.ISO_COUNTRY_CODE = '{self.iso_country_code}'
                    ORDER BY
                        RCP.POPULATION DESC
                ) AS CITY_TABLE
                INNER JOIN RDF_CITY_POI_NAMES ON CITY_TABLE.POI_ID = RDF_CITY_POI_NAMES.POI_ID 
                INNER JOIN RDF_CITY_POI_NAME ON RDF_CITY_POI_NAMES.NAME_ID = RDF_CITY_POI_NAME.NAME_ID 
            WHERE
                RDF_CITY_POI_NAMES.NAME_TYPE = 'B'
                AND RDF_CITY_POI_NAME.LANGUAGE_CODE in ({self.language})
                AND CITY_TABLE.CAT_ID = 4444
            ORDER BY  
                CITY_TABLE.POPULATION DESC,
                CITY_TABLE.POI_ID,
                RDF_CITY_POI_NAME.LANGUAGE_CODE
'''
        return script


class QueryPoi(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['POI_NAME',
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

    def __init__(self, iso_country_code: str, order8_id: str, poi_id: list = None, language='ENG'):
        self.iso_country_code = iso_country_code
        self.order8_id = order8_id
        self.language_code = language
        self.poi_query = ''
        if poi_id:
            _poi_id = ""
            for c in poi_id:
                if _poi_id is not "":
                    _poi_id += f","
                _poi_id += f"'{c}'"
            self.poi_query = f' AND RP.POI_ID in ({_poi_id})'

    def script(self) -> str:
        """
            根据iso_country_code和order8_id，查询城市的poi信息（取随机六个）
            :return:
            """
        script = f'''
                    SELECT
                LEFTTABLE.POI_NAME,
                LEFTTABLE.POI_ID,
                LEFTTABLE.house_number,
                LEFTTABLE.street_name,
                LEFTTABLE.POI_OWN,
                LEFTTABLE.postal_code,
                RIGHTTABLE.PHONE,
                LEFTTABLE.Lon,
                LEFTTABLE.Lat,
                LEFTTABLE.LINK_ID,
                LEFTTABLE.LANGUAGE_POI,
                LEFTTABLE.ORDER1_ID,
                LEFTTABLE.ORDER2_ID,
                LEFTTABLE.ORDER8_ID,
                LEFTTABLE.BUILTUP_ID,
                LEFTTABLE.CAT_ID,
                db_name() 
            FROM (
                SELECT TOP 6
                        RPN.NAME AS POI_NAME,
                        RP.POI_ID,
                        RPA.house_number,
                        RPA.street_name,
                        RPA.postal_code,
                        POI_OWN = RFN.NAME,
                        Lon = RLOC.Lon * 0.00001,
                        Lat = RLOC.Lat * 0.00001,
                        RLOC.LINK_ID,
                        RPN.LANGUAGE_CODE AS LANGUAGE_POI,
                        RPA.ORDER1_ID,
                        RPA.ORDER2_ID,
                        RPA.ORDER8_ID,
                        RPA.BUILTUP_ID,
                        RP.CAT_ID,
                        RPN.LANGUAGE_CODE
                FROM
                        RDF_POI RP
                        INNER JOIN RDF_POI_ADDRESS RPA ON RP.POI_ID = RPA.POI_ID
                        {self.poi_query}
                        AND RPA.STREET_NAME IS NOT NULL
                        AND RPA.ISO_COUNTRY_CODE = '{self.iso_country_code}'
                        AND RPA.ORDER8_ID = {self.order8_id}
                        AND RPA.LANGUAGE_CODE = '{self.language_code}'
                        INNER JOIN RDF_POI_NAMES RPNS ON RP.POI_ID = RPNS.POI_ID
                        INNER JOIN RDF_POI_NAME RPN ON RPNS.NAME_ID = RPN.NAME_ID 
                        AND RPN.LANGUAGE_CODE = RPA.LANGUAGE_CODE
                        INNER JOIN RDF_FEATURE_NAMES RFNS ON RPA.BUILTUP_ID = RFNS.FEATURE_ID
                        INNER JOIN RDF_FEATURE_NAME RFN ON RFNS.NAME_ID = RFN.NAME_ID
                        and RFN.LANGUAGE_CODE = RPN.LANGUAGE_CODE
                        INNER JOIN RDF_LOCATION RLOC ON RPA.LOCATION_ID = RLOC.LOCATION_ID
                WHERE
                        RPNS.name_type = 'b'
                        AND RFNS.name_type = 'b'
                        AND RFNS.IS_EXONYM = 'n'
                ORDER BY
                        NEWID()
                ) AS LEFTTABLE
                LEFT JOIN (
                    SELECT
                        POI_id,
                        PHONE = stuff(
                            (
                            SELECT
                                ',' + CONTACT 
                            FROM (
                                SELECT
                                    * 
                                FROM
                                    RDF_POI_CONTACT_INFORMATION 
                                WHERE
                                    RDF_POI_CONTACT_INFORMATION.contact_type IN ( 1, 2, 5 )
                                ) AS t 
                            WHERE
                                t.POI_id = bb.POI_id FOR xml path ( '' )
                            ),
                            1,
                            1,
                            '' 
                        ) 
                    FROM
                        DBO.RDF_POI_CONTACT_INFORMATION bb 
                    GROUP BY
                        POI_id 
                ) AS RIGHTTABLE ON LEFTTABLE.POI_ID= RIGHTTABLE.POI_ID
            ORDER BY 
                LEFTTABLE.POI_ID,
                LEFTTABLE.LANGUAGE_POI
            '''
        return script


class QueryPtaddr(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ROAD_NAME',
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

    def __init__(self, iso_code, order_8, language: str, point_id: list):
        self.iso_country_code = iso_code
        self.order8_id = order_8
        self.language_code = language
        self.ptaddr_query_link_id = ""
        self.ptaddr_query_point_id = ""
        self.without_ptaddr_query = "INNER JOIN RDF_ROAD_LINK ON RDF_ROAD_LINK.LINK_ID = RDF_LINK.LINK_ID"
        if point_id:
            _point_id = ""
            for c in point_id:
                if _point_id is not "":
                    _point_id += f","
                _point_id += f"'{c}'"
            self.ptaddr_query_link_id = f"""INNER JOIN RDF_ROAD_LINK ON RDF_ROAD_LINK.LINK_ID = RDF_LINK.LINK_ID"""
            self.ptaddr_query_point_id = f"""AND RDF_ADDRESS_POINT.ADDRESS_POINT_ID IN ({_point_id})"""
            self.without_ptaddr_query = ""

    def script(self) -> str:
        script = f'''
        SELECT top 6
            RDF_ROAD_NAME.STREET_NAME AS ROAD_NAME,
            RDF_ADDRESS_POINT.ADDRESS,
            RDF_ADDRESS_POINT.SIDE,
            RDF_ADDRESS_POINT.ADDRESS_POINT_ID ,
            RDF_FEATURE_NAME.NAME AS ROAD_OWNER,
            RDF_POSTAL_AREA.POSTAL_CODE AS PD,
            RDF_LINK_GEOMETRY.LON* 0.00001 LON,
            RDF_LINK_GEOMETRY.LAT* 0.00001 LAT,
            RDF_ROAD_LINK.LINK_ID AS EdgeID,
            RDF_ROAD_NAME.LANGUAGE_CODE AS Road_language,
            RDF_ADDRESS_POINT.BUILDING_NAME,
            RDF_ADMIN_HIERARCHY.admin_place_id,
            RDF_ADMIN_HIERARCHY.admin_order,
            db_name()
        FROM 
            RDF_LINK
            {self.ptaddr_query_link_id}
            INNER JOIN RDF_ADMIN_PLACE ON RDF_ADMIN_PLACE.ADMIN_PLACE_ID = RDF_LINK.LEFT_ADMIN_PLACE_ID
            INNER JOIN RDF_ADMIN_HIERARCHY ON RDF_ADMIN_HIERARCHY.ADMIN_PLACE_ID = RDF_ADMIN_PLACE.ADMIN_PLACE_ID
                AND RDF_ADMIN_HIERARCHY.ISO_COUNTRY_CODE = '{self.iso_country_code}'
                AND RDF_ADMIN_HIERARCHY.ORDER8_ID = {self.order8_id}
            {self.without_ptaddr_query}
            INNER JOIN RDF_ADDRESS_POINT ON RDF_ADDRESS_POINT.ROAD_LINK_ID = RDF_ROAD_LINK.ROAD_LINK_ID
                AND RDF_ADDRESS_POINT.LANGUAGE_CODE = '{self.language_code}'
                {self.ptaddr_query_point_id}
            INNER JOIN RDF_ROAD_NAME ON RDF_ROAD_NAME.ROAD_NAME_ID = RDF_ROAD_LINK.ROAD_NAME_ID
                AND RDF_ROAD_NAME.NAME_TYPE='B'
                AND RDF_ROAD_NAME.IS_EXONYM='N'
                AND RDF_ROAD_NAME.LANGUAGE_CODE = RDF_ADDRESS_POINT.LANGUAGE_CODE
            INNER JOIN RDF_FEATURE_NAMES  ON RDF_FEATURE_NAMES.FEATURE_ID = RDF_ADMIN_PLACE.ADMIN_PLACE_ID
                    AND RDF_FEATURE_NAMES.NAME_TYPE= 'B'
                    AND RDF_FEATURE_NAMES.IS_EXONYM= 'N' 
            INNER JOIN RDF_FEATURE_NAME ON RDF_FEATURE_NAME.NAME_ID = RDF_FEATURE_NAMES.NAME_ID
                    AND RDF_FEATURE_NAME.LANGUAGE_CODE = RDF_ROAD_NAME.LANGUAGE_CODE
            INNER JOIN RDF_LINK_GEOMETRY ON RDF_LINK_GEOMETRY.LINK_ID = RDF_LINK.LINK_ID
                    AND RDF_LINK_GEOMETRY.SEQ_NUM = '0'
            LEFT JOIN RDF_POSTAL_AREA ON RDF_LINK.LEFT_POSTAL_AREA_ID = RDF_POSTAL_AREA.POSTAL_AREA_ID 
        ORDER BY
            newid()
        '''
        return script


class QueryAllCountry(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ISO_COUNTRY_CODE',
               'LANGUAGE_CODE',
               'COUNTRY_ID',
               'NAME',
               'NAME_ID',
               'IS_EXONYM',
               'NAME_TYPE',
               'OWNER',
               'DRIVING_SIDE',
               'NAME_LANGUAGE']

    # 有查询参数的时候，就需要先实例化，将参数传递进来再执行
    def __init__(self, iso_country_code: list = None, name_language: str = 'ENG'):
        """
        查询国家数据
        :param iso_country_code: 需要查询的国家的iso_country_code，如果为None则查询所有国家的数据，一次智能查询一个国家或者所有国家
        :param name_language: 默认查询的为ENG语言，一次只能查询一个语言
        """
        country_str = ""
        if iso_country_code:
            for c in iso_country_code:
                if country_str is not "":
                    country_str += f","
                country_str += f"'{c}'"
        if country_str is not "":
            self.iso_query = f" AND RAH.ISO_COUNTRY_CODE in ({country_str})"
        else:
            self.iso_query = ""
        self.language = name_language

    def script(self) -> str:
        """
        查询数据库内所有国家的信息，国家名的语言为ENG
        :return:
        """

        script = f'''
            SELECT DISTINCT
                RAH.ISO_COUNTRY_CODE,
                RC.LANGUAGE_CODE,
                RAH.COUNTRY_ID,
                FN.NAME,
                FN.NAME_ID,
                FNS.IS_EXONYM,
                FNS.NAME_TYPE,
                FNS.OWNER,
                RC.DRIVING_SIDE,
                FN.LANGUAGE_CODE AS NAME_LANGUAGE
            FROM
                RDF_ADMIN_HIERARCHY RAH
                LEFT JOIN RDF_FEATURE_NAMES FNS ON RAH.ADMIN_PLACE_ID = FNS.FEATURE_ID
                LEFT JOIN RDF_FEATURE_NAME FN ON FNS.NAME_ID = FN.NAME_ID
                LEFT JOIN RDF_COUNTRY RC ON RAH.ISO_COUNTRY_CODE = RC.ISO_COUNTRY_CODE 
            WHERE
                RAH.ADMIN_ORDER= '0' 
                AND FNS.NAME_TYPE= 'B' 
                AND FN.LANGUAGE_CODE = '{self.language}'
                {self.iso_query}
            ORDER BY
                RAH.ISO_COUNTRY_CODE,
                FN.LANGUAGE_CODE
            '''
        return script


class QueryCapital(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['POI_ID',
               'COUNTRY_ID',
               'ISO_COUNTRY_CODE',
               'NAME']

    # 有查询参数的时候，就需要先实例化，将参数传递进来再执行
    def __init__(self, iso_country_code: str, country_id: str, language: str = 'ENG'):
        self.iso_country_code = iso_country_code
        self.country_id = country_id
        self.language = language

    def script(self) -> str:
        """
        根据国家的iso_country_code和country_id查询国家的首都信息，首都名称语言为ENG
        :return:
        """
        script = f'''
            SELECT
                POI_ID,
                COUNTRY_ID,
                ISO_COUNTRY_CODE,
                NAME
            FROM
            (
                SELECT 
                    POI_ID,
                    COUNTRY_ID,
                    ISO_COUNTRY_CODE,
                    NAMED_PLACE_ID
                FROM [dbo].[RDF_CITY_POI]
                WHERE CAPITAL_COUNTRY = 'Y'
            ) R
            LEFT JOIN RDF_FEATURE_NAMES RFNS ON R.NAMED_PLACE_ID = RFNS.FEATURE_ID
            LEFT JOIN RDF_FEATURE_NAME RFN ON RFNS.NAME_ID = RFN.NAME_ID
            WHERE
                RFN.LANGUAGE_CODE = '{self.language}'
                AND ISO_COUNTRY_CODE = '{self.iso_country_code}'
                AND COUNTRY_ID = '{self.country_id}'
        '''
        return script


class QueryTotal(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ISO_COUNTRY_CODE',
               'TOTAL']

    def __init__(self, iso_country_code: str):
        self.iso_country_code = iso_country_code

    def script(self) -> str:
        """
        根据iso_country_code查询国家的行政层级数量
        :return:
        """
        script = f'''
        SELECT
            ISO_COUNTRY_CODE,
            COUNT ( * ) TOTAL
        FROM
            RDF_ADMIN_HIERARCHY
        WHERE	
            ISO_COUNTRY_CODE='{self.iso_country_code}'
        GROUP BY
            ISO_COUNTRY_CODE
        '''
        return script


class QueryLevel(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ISO_COUNTRY_CODE',
               'COUNTRY_ID',
               'LEVEL']

    def __init__(self, iso_country_code):
        self.iso_country_code = iso_country_code

    def script(self) -> str:
        """
        根据iso_country_code查询层级信息
        :return:
        """
        script = f'''
        SELECT DISTINCT
            ISO_COUNTRY_CODE,
            COUNTRY_ID,
            LEVEL=stuff(
            (	SELECT
                    '/'+ CAST(ADMIN_ORDER AS varchar(10))
                FROM
                (
                    SELECT
                        ISO_COUNTRY_CODE,
                        COUNTRY_ID,
                        ADMIN_ORDER 
                    FROM
                        RDF_ADMIN_HIERARCHY
                    GROUP BY
                        ISO_COUNTRY_CODE,
                        COUNTRY_ID,
                        ADMIN_ORDER 
                ) AS A
                WHERE 
                    ISO_COUNTRY_CODE = B.ISO_COUNTRY_CODE
                GROUP BY
                    ADMIN_ORDER 
                FOR XML PATH('') 
            ),
            1,
            1,
            '')
        FROM
            RDF_ADMIN_HIERARCHY B
        WHERE
            ISO_COUNTRY_CODE = '{self.iso_country_code}'
        GROUP BY
            ISO_COUNTRY_CODE,
            COUNTRY_ID,
            ADMIN_ORDER 
        '''
        return script


class QueryAllCity(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['CITY_NAME',
               'CITY_POI_ID',
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
               'LANGUAGE_CODE',
               'IS_EXONYM']

    def __init__(self, iso_country_code: str, city_poi_id: str = None, poi_language: str = 'ENG'):
        self.iso_country_code = iso_country_code
        self.city_query = ''
        if city_poi_id:
            self.city_query = f'AND RDF_CITY_POI.POI_ID = {city_poi_id}'
        self.language_code = poi_language

    def script(self) -> str:
        """
        根据iso_country_code，查询国家的城市（取前六）
        :return:
        """
        script = f'''
        SELECT top 6
            RDF_CITY_POI_NAME.NAME AS CITY_NAME,
            RDF_CITY_POI.POI_ID AS CITY_POI_ID,
            RDF_CITY_POI.NAMED_PLACE_ID,
            RDF_CITY_POI.ORDER1_ID,
            RDF_CITY_POI.ORDER2_ID,
            RDF_CITY_POI.ORDER8_ID,
            RDF_CITY_POI.BUILTUP_ID,
            RDF_CITY_POI.POPULATION,
            RDF_CITY_POI.CAPITAL_COUNTRY,
            RDF_CITY_POI.CAPITAL_ORDER1,
            RDF_CITY_POI.CAPITAL_ORDER8,
            RDF_CITY_POI.NAMED_PLACE_TYPE,
            RDF_CITY_POI_NAME.LANGUAGE_CODE,
            RDF_CITY_POI_NAMES.IS_EXONYM
        FROM
            RDF_CITY_POI,
            RDF_CITY_POI_NAME,
            RDF_CITY_POI_NAMES
        WHERE
            RDF_CITY_POI.POI_ID = RDF_CITY_POI_NAMES.POI_ID 
            AND RDF_CITY_POI_NAMES.NAME_ID = RDF_CITY_POI_NAME.NAME_ID 
            AND RDF_CITY_POI_NAMES.NAME_TYPE = 'B'
            AND RDF_CITY_POI_NAME.LANGUAGE_CODE = '{self.language_code}'
            {self.city_query}
            AND RDF_CITY_POI_NAMES.IS_EXONYM = 'N'
            AND RDF_CITY_POI.ISO_COUNTRY_CODE =   '{self.iso_country_code}'
            AND RDF_CITY_POI.CAT_ID = 4444
        ORDER BY  
            RDF_CITY_POI.POPULATION DESC,
            RDF_CITY_POI.POI_ID,
            RDF_CITY_POI_NAME.LANGUAGE_CODE
        '''
        return script


class QueryAllPoi(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['POI_NAME',
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

    def __init__(self, iso_country_code: str, order8_id: str, poi_id: str = None, language='ENG'):
        self.iso_country_code = iso_country_code
        self.order8_id = order8_id
        self.language_code = language
        self.poi_query = ''
        if poi_id:
            self.poi_query = f' AND RP.POI_ID = {poi_id}'

    def script(self) -> str:
        """
        根据iso_country_code和order8_id，查询城市的poi信息（取随机六个）
        :return:
        """
        script = f'''
                SELECT
            LEFTTABLE.POI_NAME,
            LEFTTABLE.POI_ID,
            LEFTTABLE.house_number,
            LEFTTABLE.street_name,
            LEFTTABLE.POI_OWN,
            LEFTTABLE.postal_code,
            RIGHTTABLE.PHONE,
            LEFTTABLE.Lon,
            LEFTTABLE.Lat,
            LEFTTABLE.LINK_ID,
            LEFTTABLE.LANGUAGE_POI,
            LEFTTABLE.ORDER1_ID,
            LEFTTABLE.ORDER2_ID,
            LEFTTABLE.ORDER8_ID,
            LEFTTABLE.BUILTUP_ID,
            LEFTTABLE.CAT_ID,
            db_name() 
        FROM (
            SELECT TOP 6
                    RPN.NAME AS POI_NAME,
                    RP.POI_ID,
                    RPA.house_number,
                    RPA.street_name,
                    RPA.postal_code,
                    POI_OWN = RFN.NAME,
                    Lon = RLOC.Lon * 0.00001,
                    Lat = RLOC.Lat * 0.00001,
                    RLOC.LINK_ID,
                    RPN.LANGUAGE_CODE AS LANGUAGE_POI,
                    RPA.ORDER1_ID,
                    RPA.ORDER2_ID,
                    RPA.ORDER8_ID,
                    RPA.BUILTUP_ID,
                    RP.CAT_ID,
                    RPN.LANGUAGE_CODE
            FROM
                    RDF_POI RP
                    INNER JOIN RDF_POI_ADDRESS RPA ON RP.POI_ID = RPA.POI_ID
                    {self.poi_query}
                    AND RPA.STREET_NAME IS NOT NULL
                    AND RPA.ISO_COUNTRY_CODE = '{self.iso_country_code}'
                    AND RPA.ORDER8_ID = {self.order8_id}
                    AND RPA.LANGUAGE_CODE = '{self.language_code}'
                    INNER JOIN RDF_POI_NAMES RPNS ON RP.POI_ID = RPNS.POI_ID
                    INNER JOIN RDF_POI_NAME RPN ON RPNS.NAME_ID = RPN.NAME_ID 
                    AND RPN.LANGUAGE_CODE = RPA.LANGUAGE_CODE
                    INNER JOIN RDF_FEATURE_NAMES RFNS ON RPA.BUILTUP_ID = RFNS.FEATURE_ID
                    INNER JOIN RDF_FEATURE_NAME RFN ON RFNS.NAME_ID = RFN.NAME_ID
                    and RFN.LANGUAGE_CODE = RPN.LANGUAGE_CODE
                    INNER JOIN RDF_LOCATION RLOC ON RPA.LOCATION_ID = RLOC.LOCATION_ID
            WHERE
                    RPNS.name_type = 'b'
                    AND RFNS.name_type = 'b'
                    AND RFNS.IS_EXONYM = 'n'
            ORDER BY
                    NEWID()
            ) AS LEFTTABLE
            LEFT JOIN (
                SELECT
                    POI_id,
                    PHONE = stuff(
                        (
                        SELECT
                            ',' + CONTACT 
                        FROM (
                            SELECT
                                * 
                            FROM
                                RDF_POI_CONTACT_INFORMATION 
                            WHERE
                                RDF_POI_CONTACT_INFORMATION.contact_type IN ( 1, 2, 5 )
                            ) AS t 
                        WHERE
                            t.POI_id = bb.POI_id FOR xml path ( '' )
                        ),
                        1,
                        1,
                        '' 
                    ) 
                FROM
                    DBO.RDF_POI_CONTACT_INFORMATION bb 
                GROUP BY
                    POI_id 
            ) AS RIGHTTABLE ON LEFTTABLE.POI_ID= RIGHTTABLE.POI_ID
        ORDER BY 
            LEFTTABLE.POI_ID,
            LEFTTABLE.LANGUAGE_POI
        '''
        return script


class QueryAllPtaddr(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ['ROAD_NAME',
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

    def __init__(self, iso_country_code: str, country_id: str, order8_id: str, ptaddr_id: str = None, language='ENG'):
        self.iso_country_code = iso_country_code
        self.country_id = country_id
        self.order8_id = order8_id
        self.ptaddr_query = ''
        if ptaddr_id:
            self.ptaddr_query = f'AND RDF_ADDRESS_POINT.ADDRESS_POINT_ID = {ptaddr_id}'
        self.language = language

    def script(self) -> str:
        """
        根据iso_country_code、country_id、order8_id查询ptaddr信息（取随机六个）
        :return:
        """
        script = f"""
        SELECT top 6
            RDF_ROAD_NAME.STREET_NAME AS ROAD_NAME,
            RDF_ADDRESS_POINT.ADDRESS,
            RDF_ADDRESS_POINT.SIDE,
            RDF_ADDRESS_POINT.ADDRESS_POINT_ID ,
            RDF_FEATURE_NAME.NAME AS ROAD_OWNER,
            RDF_POSTAL_AREA.POSTAL_CODE AS PD,
            RDF_LINK_GEOMETRY.LON* 0.00001 LON,
            RDF_LINK_GEOMETRY.LAT* 0.00001 LAT,
            RDF_ROAD_LINK.LINK_ID AS EdgeID,
            RDF_ROAD_NAME.LANGUAGE_CODE AS Road_language,
            RDF_ADDRESS_POINT.BUILDING_NAME,
            RDF_ADMIN_HIERARCHY.admin_place_id,
            RDF_ADMIN_HIERARCHY.admin_order,
            db_name()
        FROM 
            RDF_LINK 
            INNER JOIN RDF_ROAD_LINK ON RDF_ROAD_LINK.LINK_ID = RDF_LINK.LINK_ID
            INNER JOIN RDF_ADDRESS_POINT ON RDF_ADDRESS_POINT.ROAD_LINK_ID = RDF_ROAD_LINK.ROAD_LINK_ID
                AND RDF_ADDRESS_POINT.LANGUAGE_CODE = '{self.language}'
                {self.ptaddr_query}
            INNER JOIN RDF_ROAD_NAME ON RDF_ROAD_NAME.ROAD_NAME_ID = RDF_ROAD_LINK.ROAD_NAME_ID
                AND RDF_ROAD_NAME.NAME_TYPE='B'
                AND RDF_ROAD_NAME.IS_EXONYM='N'
                AND RDF_ROAD_NAME.LANGUAGE_CODE = RDF_ADDRESS_POINT.LANGUAGE_CODE
            INNER JOIN RDF_ADMIN_PLACE ON RDF_ADMIN_PLACE.ADMIN_PLACE_ID = RDF_LINK.LEFT_ADMIN_PLACE_ID
            INNER JOIN RDF_FEATURE_NAMES  ON RDF_FEATURE_NAMES.FEATURE_ID = RDF_ADMIN_PLACE.ADMIN_PLACE_ID
                AND RDF_FEATURE_NAMES.NAME_TYPE= 'B'
                AND RDF_FEATURE_NAMES.IS_EXONYM= 'N' 
            INNER JOIN RDF_FEATURE_NAME ON RDF_FEATURE_NAME.NAME_ID = RDF_FEATURE_NAMES.NAME_ID
                AND RDF_FEATURE_NAME.LANGUAGE_CODE = RDF_ROAD_NAME.LANGUAGE_CODE
            INNER JOIN RDF_LINK_GEOMETRY ON RDF_LINK_GEOMETRY.LINK_ID = RDF_LINK.LINK_ID
            INNER JOIN RDF_ADMIN_HIERARCHY ON RDF_ADMIN_HIERARCHY.ADMIN_PLACE_ID = RDF_ADMIN_PLACE.ADMIN_PLACE_ID
            and RDF_LINK_GEOMETRY.SEQ_NUM = '0'
            LEFT JOIN RDF_POSTAL_AREA ON RDF_LINK.LEFT_POSTAL_AREA_ID = RDF_POSTAL_AREA.POSTAL_AREA_ID
        WHERE
            RDF_ADMIN_HIERARCHY.ISO_COUNTRY_CODE = '{self.iso_country_code}'
            AND RDF_ADMIN_HIERARCHY.ORDER8_ID = {self.order8_id}
            AND RDF_ADMIN_HIERARCHY.COUNTRY_ID = {self.country_id}
        ORDER BY
            newid()
        """
        return script


class QueryEJV(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ["DP_NODE_ID",
               "ORIGINATING_LINK_ID",
               "DEST_LINK_ID",
               "LATITUDE",
               "LONGITUDE"]

    def __init__(self, iso_country_code: str):
        self.iso_country_code = iso_country_code

    def script(self) -> str:
        script = f"""
        SELECT top 6
            DP_NODE_ID,ORIGINATING_LINK_ID,DEST_LINK_ID,LATITUDE,LONGITUDE
        FROM 
            RDF_AC_EJV
        WHERE
            RDF_AC_EJV.ISO_COUNTRY_CODE ='{self.iso_country_code}'
            AND RDF_AC_EJV.SIGN_DEST != '-1'
            and RDF_AC_EJV.EJV_FILENAME != ''
        ORDER BY
            NEWID()
        """
        return script


class QueryLink4Node(QueryObj):
    class QueryResults(QueryResultObj):
        arg = ["LINK_ID", "SEQ_NUM", "LAT", "LON"]

    def __init__(self, orig_link):
        self.orig_link = orig_link

    def script(self) -> str:
        script = f"""
        SELECT
            LINK_ID,SEQ_NUM,LAT,LON
        FROM
            RDF_LINK_GEOMETRY
        WHERE
            RDF_LINK_GEOMETRY.LINK_ID = '{self.orig_link}'
            and SEQ_NUM IN ('0' ,'999999')
        ORDER BY
            SEQ_NUM
        """
        return script

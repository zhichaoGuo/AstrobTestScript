from QueryScript import QueryEJV, QueryLink4Node
from Utils import SqlServer, load_config, ModelUtils


def query_EJV(db: SqlServer, iso_county_code: list = None):
    """

    :param db:
    :param iso_county_code:
    :return: ret = {"THA":[[orig_lat,orig_lon,dest_lat,dest_lon],[]]
    """
    ret = {}
    for country in iso_county_code:
        ret[country] = []
        all_ejv = db.query(QueryEJV(iso_country_code=country))
        for ejv in all_ejv:
            ejv_node_link = db.query(QueryLink4Node(orig_link=ejv.ORIGINATING_LINK_ID))
            if len(ejv_node_link) != 2:
                continue
            res_node = ModelUtils.return_unique_node(ejv_node_link, ejv)
            if res_node:
                ret[country].append([res_node.LAT / 100000, res_node.LON / 100000])

    return ret


def query_EJV_case():
    db = SqlServer(**load_config().get("sqlserver"))
    print(query_EJV(db, ['THA']))
    db.close()


if __name__ == '__main__':
    query_EJV_case()

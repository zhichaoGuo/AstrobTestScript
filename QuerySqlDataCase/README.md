# 查询数据库中用例
**此脚本将HERE_RDF数据按照一定规则生成excel用例。**

计划分为四步走：
1. 先查询国家信息，如：ISO_COUNTRY_CODE、COUNTRY_ID、NAME_ID
2. 查询城市信息，如：CITY_NAME、CITY_POI_ID、NAMED_PLACE_ID
3. 查询poi信息，如：POI_NAME、POI_ID、street_name
4. 查询ptaddr信息，如：ROAD_NAME、ADDRESS、SIDE

数据传递路线：

- 数据库查询结果 -> 数据模型 -> 下一次查询参数 -> 数据库查询结果 -> 数据模型 -> 输出表格

这种方法要求，如果希望修改输出表格内容，需要修改数据模型以及处理查询结果的相关代码，必要时修改数据库查询语句，在数据库查询结果和数据模型之间使用数据转换层，避免兼容性问题。

### 查询国家信息
先查大部分信息，在通过load函数添加查询的首都、行政区数量、行政区等级的信息
### 查询城市信息
由于查询结果类和最终的数据类内容一致，所以转换简单
### 查询poi信息
由于查询结果类和最终的数据类内容一致，所以转换简单
### 查询ptaddr信息
由于查询结果类和最终的数据类内容一致，所以转换简单

### 使用方法
```shell
    # 安装依赖库
    pip install -r requirements.txt
    # 修改config.yml的database部分的数据库名字
    
    # 运行query_map_case.py的if __name__ == '__main__':部分的参数
    
    # 运行query_map_case.py
    python ./query_map_case.py
    
```

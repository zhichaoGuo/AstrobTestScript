# 查询数据库中用例
**此脚本将HERE_RDF数据按照一定规则生成excel用例。**
## 方法 V2.0
### 更新原因
- 由于方法 V1.0在查询国家信息时，使用了三次查询，再通过脚本汇总为查询记录，一次查询效率比多次查询要高，所以优化了国家数据的查询sql
- 删除了V1.0为了将多次查询结果拼成一个结果而创造出的数据层
- 优化了所有的sql查询语句，显著提升查询效率（EEU数据库在V1.0时需要3.5h，V2.0时需要0.5h）
- 将查询参数抽象出来，方便修改和使用

### 使用方法
主要方法在`main.py`中，数据结构在`DataInfo.py`中，查询sql在`QueryScript.py`中。
```shell
    # 安装依赖库
    pip install -r requirements.txt
    
    # 修改main.py的if __name__ == '__main__':部分的参数
    # iso_country_code为需要查询的国家iso_country_code的列表，为空时默认查询数据库中的所有国家
    # language_code为需要查询的数据语言的列表（建议只在MEA数据库中查询["RAR","ENG"]），为空时默认查询当前国家的官方语言
    # 运行main.py
    python ./main.py
    
```
### 程序逻辑
新建查询结果目录 -> 查询国家数据 -> 存入目录中的pkl -> 查询城市数据并存pkl -> 查poi、ptaddr并村pkl -> 写excel
## 方法 V1.0

### 计划分为四步走：
1. 先查询国家信息，如：ISO_COUNTRY_CODE、COUNTRY_ID、NAME_ID
2. 查询城市信息，如：CITY_NAME、CITY_POI_ID、NAMED_PLACE_ID
3. 查询poi信息，如：POI_NAME、POI_ID、street_name
4. 查询ptaddr信息，如：ROAD_NAME、ADDRESS、SIDE

### 数据传递路线：

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


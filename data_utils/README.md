# 转换工具
此工具用于将HERE_XML格式的数据抽取储存到数据库中

## 转换流程
顺序读取xml文件，解析xml树，对于每行解析place_id、CategoryId将其version、country、xml_name、line_index存储至数据库。

每个文件解析完成后存一次数据库

## 使用方法

1. 在`query_ev_model.py`中重写`__tablename__`属性，将其改为需要存储的数据库的名字，如：places_xml_s231_f1_mea
2. 在`transf_EV_res.py`中的`main()`中重写`version_paths`变量，将其改为需要转换的version的路径
3. 使用`python ./transf_EV_res.py` 执行脚本
本项目提供两种数据源的EV station的用例查询：

## HERE Advanced Places
由 query_EV_case.py启动

## HERE EV Charge Points Static
由 main.py启动

后面不出意外的话应该都会切换到第二种方式。
### 过滤规则
#### POI NAME
- 对MEA SAU存在英语和阿语 官方名称和同义词 一共四种 分别放在`<POI_Name>`中以Language_Code 和 Type 进行区分
- 对MEA ISR存在希伯来语和音译语言 一共两种 放在`<POI_Name>`中不同的<Text>中以Trans_Type进行区分
- 对EU ESP 存在官方名称和同义词 一共两种 分别放在`<POI_Name>`中以Type进行区分

#### Street Name
- 对于MEA SAU street name存在英语和阿语两种    
  存在`<Address>` `<ParsedAddress>` `<ParsedStreetAddress>` `<ParsedStreetName>` `<StreetName>`下以Language_Code属性区分
- 对于MEA ISR street name存在希伯来语和音译语言 
  存在`<Address>` `<ParsedAddress>` `<ParsedStreetAddress>` `<ParsedStreetName>`下以`<StreetName>`和`<Trans_ParsedStreetName>` `<StreetName>`
- 对于EU ESP street name 
  存在`<Actual_Address_Components>` `<Actual_Street_Name>` `<Actual_Street_Name_Base>`中

#### Place Level
- 对MEA SAU place level 有阿语和英语两种 存在Language_Code区别
- 对MEA ISR place level 有希伯来语和音译语言两种 存在Language_Code和Trans_Type区别
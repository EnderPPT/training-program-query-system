# 跨校对比演示查询

以下测试用例用于验证子模块 B。默认对比学校为西南财经大学和上海财经大学。

## 1. 对比两校同专业总学分要求

```http
GET /compare/majors/信息管理与信息系统/summary
```

验证点：返回两所学校同名专业的总学分、必修课数量、显式课程总学分。

## 2. 查询两校同专业共同课程

```http
GET /compare/majors/信息管理与信息系统/common-courses
```

验证点：返回两校都开设的课程，例如思政、数学、专业基础类课程。

## 3. 查询西南财经大学相对上海财经大学的独有课程

```http
GET /compare/majors/信息管理与信息系统/school-only-courses?school_name=西南财经大学&other_school_name=上海财经大学
```

验证点：返回西南财经大学培养方案中存在、上海财经大学同名专业中未出现的课程。

## 4. 查询上海财经大学相对西南财经大学的独有课程

```http
GET /compare/majors/信息管理与信息系统/school-only-courses?school_name=上海财经大学&other_school_name=西南财经大学
```

验证点：返回上海财经大学培养方案中存在、西南财经大学同名专业中未出现的课程。

## 5. 对比某门课程在两校中的开设情况

```http
GET /compare/courses/程序设计基础?major_name=计算机科学与技术
```

验证点：返回该课程在两校相关专业中的课程类别、学分、学时和建议学期。

## 6. 中文自然语言查询：总学分对比

```http
POST /compare/nl-query
Content-Type: application/json

{"question": "对比两校信息管理与信息系统总学分"}
```

验证点：系统识别中文问题意图，映射到跨校总学分对比查询并返回结果。

## 7. 中文自然语言查询：共同课程

```http
POST /compare/nl-query
Content-Type: application/json

{"question": "查询两校信息管理与信息系统共同课程"}
```

验证点：系统识别同名专业共同课程查询并返回两校课程交集。

## 8. 中文自然语言查询：差异课程

```http
POST /compare/nl-query
Content-Type: application/json

{"question": "对比两校数据科学与大数据技术差异课程"}
```

验证点：系统识别差异课程查询，默认返回西南财经大学相对上海财经大学的独有课程。

## 9. 中文自然语言查询：课程学分学时对比

```http
POST /compare/nl-query
Content-Type: application/json

{"question": "对比课程程序设计基础学分"}
```

验证点：系统识别课程名称，返回该课程在两校培养方案中的学分、学时和所属专业。

## 10. 中文自然语言查询：上财必修课

```http
POST /compare/nl-query
Content-Type: application/json

{"question": "查询上海财经大学数据科学与大数据技术必修课"}
```

验证点：系统识别学校、专业和必修课意图，返回上财该专业必修课程。

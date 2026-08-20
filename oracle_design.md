# Oracle SQL 练习程序 —— 结构设计文档(发给 AI 的实现规格书)

> 本文档是**需求 + 结构设计 + 实现规格**,用途:把它直接复制发给任意 AI
> (ChatGPT / Claude / DeepSeek 等),让 AI 照此实现一个可运行的 Oracle SQL 练习程序。
> 文档已把表结构、示例数据、转换规则、题库、判分算法、交互流程全部定义清楚,
> AI 不需要再"猜需求",按章节实现即可。

---

## 0. 一句话目标

做一个**离线、零依赖、无需安装 Oracle** 的命令行 Oracle SQL 练习程序:
用户手写 SQL → 程序本地**真实执行** → **表格形式展示执行效果** → 自动判分 + 解析;
并附带题库练习、模拟考试、错题本、学习统计等辅助功能。

---

## 1. 项目背景与目标

- **用户场景**:想练习 Oracle 数据库语法,但没有真实 Oracle 环境(也没有 Docker)。
- **核心诉求**:
  1. 能直接练习数据库语法(手写 SQL)。
  2. 写完 SQL 后能看到**执行效果**(结果表格、返回行数、耗时)。
  3. 有自动判分、答案解析等辅助功能。
- **产品形态**:命令行交互程序(Windows / Linux / macOS 均可),纯 Python 标准库实现。

---

## 2. 技术方案与约束(必须遵守)

| 项 | 要求 |
|---|---|
| 语言 | Python 3.8+(仅用标准库) |
| 执行引擎 | 内置 `sqlite3` 内存库,用它**模拟 Oracle** 执行 SQL |
| 第三方依赖 | **零依赖**,禁止引入任何 pip 包 |
| 界面 | 命令行,全中文提示 |
| 持久化 | 本地 JSON 文件(统计、错题本) |
| 平台 | 需兼容 Windows 控制台(注意中文输出编码) |

### 为什么用 SQLite 模拟 Oracle?

- 用户没有真实 Oracle,SQLite 是 Python 自带、零安装的最优"本地执行器"。
- SQLite 与 Oracle 共通的 SQL(标准 SELECT / WHERE / ORDER BY / GROUP BY / JOIN / 子查询 /
  聚合函数 / CASE WHEN / 窗口函数等)可以直接执行,**结果真实可信**。
- Oracle 特有语法(DUAL、SYSDATE、NVL、DECODE、ROWNUM、MINUS 等)通过一层
  **"Oracle → SQLite 语法转换" + 自定义函数注册**来兼容,让绝大部分练习 SQL 都能跑出结果。
- Oracle 无法在 SQLite 模拟的特性(CONNECT BY 层次查询、PIVOT 行转列、序列、PL/SQL 等)
  以**选择题 / 讲解题**形式覆盖,不影响练习完整性。

---

## 3. 总体架构与目录结构

### 3.1 模块划分(3 个文件)

```
oracle-practice/
├── oracle_practice.py     # 主程序:菜单 + 各练习模式 + 交互 + 判分流程(入口)
├── db_engine.py           # 执行引擎:建表/示例数据/语法转换/函数模拟/执行/结果比对
├── question_bank.py       # 题库:42 道题的数据(题干/标准答案/解析),纯数据文件
├── data/                  # 运行时生成:progress.json(统计)、wrongbook.json(错题本)
└── README.md              # 使用说明
```

### 3.2 各模块职责

- **db_engine.py**(核心):
  - 定义 EMP / DEPT / SALGRADE / DUAL 四张表的建表语句与全部示例数据。
  - `OracleEngine` 类:负责连接内存库、注册自定义函数、执行 SQL、语法转换、结果集比对。
- **question_bank.py**:
  - `QUESTION_BANK` 列表,每题一个 dict(结构见第 6 章)。
  - 提供按难度筛选题目的辅助函数。
- **oracle_practice.py**:
  - 主菜单 + 6 个功能:自由练习、题库练习、模拟考试、错题本、学习统计、表结构预览。
  - 判分流程、结果表格打印、JSON 持久化读写。

---

## 4. 示例数据设计(必须与本文档一致)

使用 Oracle 经典演示表,数据是**标准 14 员工 + 4 部门 + 5 等级**,很多教材/面试题都基于它。

### 4.1 表结构

**EMP(员工)**
| 列 | 类型 | 说明 |
|---|---|---|
| EMPNO | NUMBER(4) | 员工号,主键 |
| ENAME | VARCHAR2(10) | 姓名 |
| JOB | VARCHAR2(9) | 岗位 |
| MGR | NUMBER(4) | 上级编号 |
| HIREDATE | DATE | 入职日期(本地用 TEXT 存 `YYYY-MM-DD`) |
| SAL | NUMBER(7,2) | 工资 |
| COMM | NUMBER(7,2) | 奖金(可空) |
| DEPTNO | NUMBER(2) | 部门号 |

**DEPT(部门)**
| 列 | 类型 | 说明 |
|---|---|---|
| DEPTNO | NUMBER(2) | 部门号,主键 |
| DNAME | VARCHAR2(14) | 部门名 |
| LOC | VARCHAR2(13) | 所在地 |

**SALGRADE(工资等级)**
| 列 | 类型 | 说明 |
|---|---|---|
| GRADE | NUMBER | 等级 |
| LOSAL | NUMBER | 最低工资 |
| HISAL | NUMBER | 最高工资 |

**DUAL(虚表)**:Oracle 内置单行单列表,本地建为 `DUAL(DUMMY TEXT)` 并插入一行 `'X'`,
用于支持 `SELECT SYSDATE FROM DUAL` 这类写法。

### 4.2 示例数据(必须完整照抄)

**EMP 14 行**(字段顺序 EMPNO, ENAME, JOB, MGR, HIREDATE, SAL, COMM, DEPTNO):

```
7369  SMITH   CLERK     7902  1980-12-17  800   NULL  20
7499  ALLEN   SALESMAN  7698  1981-02-20  1600  300   30
7521  WARD    SALESMAN  7698  1981-02-22  1250  500   30
7566  JONES   MANAGER   7839  1981-04-02  2975  NULL  20
7654  MARTIN  SALESMAN  7698  1981-09-28  1250  1400  30
7698  BLAKE   MANAGER   7839  1981-05-01  2850  NULL  30
7782  CLARK   MANAGER   7839  1981-06-09  2450  NULL  10
7788  SCOTT   ANALYST   7566  1987-04-19  3000  NULL  20
7839  KING    PRESIDENT NULL  1981-11-17  5000  NULL  10
7844  TURNER  SALESMAN  7698  1981-09-08  1500  0     30
7876  ADAMS   CLERK     7788  1987-05-23  1100  NULL  20
7900  JAMES   CLERK     7698  1981-12-03  950   NULL  30
7902  FORD    ANALYST   7566  1981-12-03  3000  NULL  20
7934  MILLER  CLERK     7782  1982-01-23  1300  NULL  10
```

**DEPT 4 行**:

```
10  ACCOUNTING  NEW YORK
20  RESEARCH    DALLAS
30  SALES       CHICAGO
40  OPERATIONS  BOSTON
```

**SALGRADE 5 行**:

```
1  700   1200
2  1201  1400
3  1401  2000
4  2001  3000
5  3001  9999
```

---

## 5. 模块 1 设计:数据库执行引擎(db_engine.py)

### 5.1 OracleEngine 类接口(伪代码)

```
class OracleEngine:
    __init__():          # 连接 :memory:,注册自定义函数,建表,插入示例数据
    translate(sql):      # 静态方法:Oracle 语法 → SQLite 语法(规则见 5.3)
    execute(sql):        # 执行 SQL,返回 {ok, columns, rows, rowcount, elapsed_ms, translated, error}
    tables():            # 返回 ["EMP","DEPT","SALGRADE"]
    describe(table):     # 返回表结构描述(列名+类型+中文说明)
    preview(table, n):   # 预览表前 n 行
    compare_results(std, usr):  # 结果集比对(用于判分,见 5.4)
```

### 5.2 需要注册(create_function)的 Oracle 函数模拟清单

SQLite 没有但 Oracle 有的函数,用 `conn.create_function` 注册,**函数名用小写**(SQL 大小写不敏感):

| 函数 | 参数 | 实现要点 |
|---|---|---|
| `nvl(x,y)` | 2 | x 为 NULL 返回 y,否则返回 x |
| `nvl2(x,a,b)` | 3 | x 非空返回 a,否则 b |
| `decode(...)` | 可变 | `DECODE(expr, 匹配1,结果1, 匹配2,结果2, ..., [默认])`,逐对比较(数字与字符串按字符串宽松比较),无匹配返回默认值或 NULL |
| `instr(s,sub[,start[,nth]])` | 2/3/4 | 返回 sub 第 nth 次出现位置(1 起),找不到返回 0 |
| `substr(s,start[,len])` | 2/3 | start 从 1 起;start=0 视为 1;负数从末尾算 |
| `initcap(s)` | 1 | 每个单词首字母大写 |
| `lpad/rpad(s,w[,pad])` | 2/3 | 左/右填充到宽度 w |
| `mod(a,b)` | 2 | 取余 |
| `trunc(n[,d])` | 1/2 | 数值截断(保留 d 位小数,默认 0) |
| `months_between(d1,d2)` | 2 | 返回月数差(含小数,按天折算 /31) |
| `add_months(d,n)` | 2 | 加 n 个月,自动处理月末(如 1-31 加 1 月 → 2-28/29) |
| `last_day(d)` | 1 | 当月最后一天 |
| `to_char(v[,fmt])` | 1/2 | 日期/数字格式化,支持 YYYY/MM/DD/HH24/MI/SS 占位符 |
| `to_date(s[,fmt])` | 1/2 | 字符串转日期(返回 YYYY-MM-DD) |
| `to_number(s)` | 1 | 转数字 |
| `greatest/least(...)` | 可变 | 取最大/最小(忽略 NULL) |
| `round(n[,d])` | 2 | 四舍五入 |
| `next_day(d,weekday)` | 2 | 下一个指定星期几 |

> SQLite 已原生支持、**无需注册**的:`UPPER/LOWER/LENGTH/REPLACE/TRIM/ABS/CEIL/FLOOR/COALESCE/NULLIF`、
> 窗口函数 `ROW_NUMBER()/RANK()/DENSE_RANK()/SUM() OVER`、`||` 字符串拼接、`CASE WHEN`。

### 5.3 Oracle → SQLite 语法转换规则表(translate 方法)

按顺序执行以下替换(全部忽略大小写):

| 序号 | Oracle 写法 | 转换结果 |
|---|---|---|
| 1 | `WHERE ROWNUM <= n` / `< n` / `= 1` | 删除该条件,末尾追加 `LIMIT n`(处理 AND/OR/WHERE 连接词残留) |
| 2 | `SYSDATE` | `datetime('now','localtime')` |
| 3 | `TRUNC(SYSDATE)` | `date('now','localtime')` |
| 4 | `TRUNC(日期列)` | `date(日期列)` |
| 5 | `MINUS` | `EXCEPT` |
| 6 | `(+)` 旧式外连接 | 不转换,抛友好错误提示改用 `LEFT JOIN ... ON` |
| 7 | 裸 `ROWNUM`(如 `SELECT ROWNUM rn FROM ...`) | `ROW_NUMBER() OVER ()` |

> 注意序号 1 的细节:`WHERE ROWNUM <= 3 AND sal > 1000` 要能正确变成 `WHERE sal > 1000 LIMIT 3`,
> 删除后需清理可能残留的 `WHERE AND`、孤立的 `WHERE`。

### 5.4 结果集比对算法(判分核心,compare_results)

SQL 题判分**不看写法、只比结果**,这样"写法不同但结果正确"也能判对。

```
输入: 标准答案执行结果 std,用户 SQL 执行结果 usr(都是 {ok, columns, rows})
1. 若 usr 执行出错 → 返回(False, "执行出错: ...")
2. 若 std.columns 与 usr.columns 的集合(忽略大小写/顺序)不一致
   → 返回(False, "结果列不一致(标准列 vs 你的列)")
3. 按 std 的列顺序,把 usr 每一行重排成相同列顺序,得到规范化行集合
4. 比较两个规范化行集合是否相等(集合比对,忽略行顺序)
5. 相等 → (True, "结果一致");不相等 → (False, 差异提示:缺少几行/多出几行)
```

### 5.5 execute 返回结构

```
{
  "ok": true/false,          # 是否执行成功
  "columns": ["ENAME","SAL"],# 列名(仅 SELECT)
  "rows": [("SMITH",800),...],# 数据行(tuple 列表)
  "rowcount": 14,            # 行数
  "elapsed": 1.23,           # 耗时(毫秒)
  "translated": "...",       # 转换后的 SQL(用于展示)
  "error": null / "错误信息"
}
```

---

## 6. 模块 2 设计:题库(question_bank.py)

### 6.1 题目数据结构

```python
{
    "id": 1,               # 题号(唯一)
    "difficulty": "初级",   # 初级 / 中级 / 高级
    "topic": "基础查询",    # 主题
    "type": "sql",          # "sql"(书写题) 或 "choice"(选择题)
    "title": "查询所有员工",
    "question": "从 EMP 表查询所有员工的姓名、岗位和工资。",
    "hint": "SELECT 列名 FROM 表名;",        # 提示(sql 题,可为 None)
    "answer_sql": "SELECT ename, job, sal FROM emp",  # 标准答案(sql 题)
    "answer": None,         # 正确选项字母(choice 题)
    "options": None,        # 选项列表(choice 题)
    "explanation": "详细解析(可多行)"
}
```

### 6.2 判分规则

- **sql 题**:用户输入 SQL → 引擎执行 → 与 `answer_sql` 的执行结果做 `compare_results` 比对。
  - 答对:显示 ✅ + 用户的执行效果表格。
  - 答错/报错:显示 ❌ + 错误原因 + 标准答案 SQL + **标准答案的执行效果表格** + 解析。
- **choice 题**:用户输入 A/B/C/D(兼容 1/2/3/4)→ 与 `answer` 比对。

### 6.3 题目清单(共 42 题,可直接照抄为题库数据)

#### 初级(12 题)——基础查询 / 条件 / 排序 / 聚合 / 分组

| id | 主题 | 题型 | 题目要点 | 标准答案(参考) |
|---|---|---|---|---|
| 1 | 基础查询 | sql | 查所有员工姓名、岗位、工资 | `SELECT ename, job, sal FROM emp` |
| 2 | 条件查询 | sql | 工资 > 2000 的姓名和工资 | `SELECT ename, sal FROM emp WHERE sal > 2000` |
| 3 | 条件查询 | sql | 10 号部门员工姓名和岗位 | `SELECT ename, job FROM emp WHERE deptno = 10` |
| 4 | 排序 | sql | 按工资降序 | `SELECT ename, sal FROM emp ORDER BY sal DESC` |
| 5 | 聚合 | sql | 各部门平均工资 | `SELECT deptno, AVG(sal) FROM emp GROUP BY deptno` |
| 6 | 聚合 | sql | 员工总人数 | `SELECT COUNT(*) FROM emp` |
| 7 | 去重 | sql | 所有不同岗位 | `SELECT DISTINCT job FROM emp` |
| 8 | 模糊查询 | sql | 姓名以 S 开头 | `SELECT ename FROM emp WHERE ename LIKE 'S%'` |
| 9 | 条件查询 | sql | 工资 1500~3000 之间 | `... WHERE sal BETWEEN 1500 AND 3000` |
| 10 | 空值 | sql | 奖金为空的员工 | `... WHERE comm IS NULL` |
| 11 | 条件查询 | sql | MANAGER 或 ANALYST | `... WHERE job IN ('MANAGER','ANALYST')` |
| 12 | 模糊查询 | sql | 姓名含字母 A | `... WHERE ename LIKE '%A%'` |

#### 中级(14 题)——连接 / 子查询 / 集合 / 函数

| id | 主题 | 题型 | 题目要点 | 标准答案(参考) |
|---|---|---|---|---|
| 13 | 连接 | sql | 员工姓名 + 部门名(内连接) | `SELECT e.ename,d.dname FROM emp e JOIN dept d ON e.deptno=d.deptno` |
| 14 | 连接 | sql | 左外连接(所有员工+部门名) | `... LEFT JOIN dept d ON e.deptno=d.deptno` |
| 15 | 子查询 | sql | 工资 > 全公司平均 | `... WHERE sal > (SELECT AVG(sal) FROM emp)` |
| 16 | 子查询 | sql | 工资 > 本部门平均(相关子查询) | `... WHERE sal > (SELECT AVG(sal) FROM emp WHERE deptno=e.deptno)` |
| 17 | 分组过滤 | sql | 平均工资 > 2000 的部门 | `... GROUP BY deptno HAVING AVG(sal) > 2000` |
| 18 | 自连接 | sql | 员工 + 上级姓名 | `SELECT e.ename,m.ename FROM emp e LEFT JOIN emp m ON e.mgr=m.empno` |
| 19 | Top-N | sql | 工资最高 3 人(ROWNUM) | `SELECT ename,sal FROM (SELECT ename,sal FROM emp ORDER BY sal DESC) WHERE ROWNUM <= 3` |
| 20 | EXISTS | sql | 有员工的部门名 | `SELECT dname FROM dept d WHERE EXISTS (SELECT 1 FROM emp e WHERE e.deptno=d.deptno)` |
| 21 | 集合 | sql | UNION 合并两个结果去重 | `SELECT ename FROM emp WHERE sal>2500 UNION SELECT ename FROM emp WHERE job='CLERK'` |
| 22 | 非等值连接 | sql | 员工 + 工资等级 | `... JOIN salgrade s ON e.sal BETWEEN s.losal AND s.hisal` |
| 23 | 分组 | sql | 部门人数/最高/最低工资 | `SELECT deptno, COUNT(*), MAX(sal), MIN(sal) FROM emp GROUP BY deptno` |
| 24 | 子查询 | sql | 与 SCOTT 同部门的人 | `... WHERE deptno = (SELECT deptno FROM emp WHERE ename='SCOTT')` |
| 25 | 字符串函数 | sql | 姓名小写 + 前 3 字符 | `SELECT LOWER(ename), SUBSTR(ename,1,3) FROM emp` |
| 26 | 日期 | sql | 1981 年入职员工 | `... WHERE hiredate >= '1981-01-01' AND hiredate < '1982-01-01'` |

#### 高级(16 题)——Oracle 特有函数 / 分析函数 / 日期运算 / 概念

| id | 主题 | 题型 | 题目要点 | 标准答案(参考) |
|---|---|---|---|---|
| 27 | Oracle 函数 | sql | NVL 空奖金按 0 | `SELECT ename, NVL(comm,0) FROM emp` |
| 28 | Oracle 函数 | sql | DECODE 岗位转中文 | `SELECT ename, DECODE(job,'MANAGER','经理','SALESMAN','销售','CLERK','职员','ANALYST','分析师','PRESIDENT','总裁','其他') FROM emp` |
| 29 | 日期格式化 | sql | TO_CHAR 格式化 `YYYY年MM月` | `SELECT ename, TO_CHAR(hiredate,'YYYY年MM月') FROM emp` |
| 30 | 分析函数 | sql | 部门内工资排名 RANK | `SELECT ename,deptno,sal, RANK() OVER (PARTITION BY deptno ORDER BY sal DESC) FROM emp` |
| 31 | 分析函数 | sql | 累计工资 SUM OVER | `SELECT ename,sal, SUM(sal) OVER (ORDER BY sal) FROM emp` |
| 32 | 分页 | sql | ROW_NUMBER 取第 4~6 名 | `SELECT ename,sal FROM (SELECT ename,sal,ROW_NUMBER() OVER (ORDER BY sal DESC) rn FROM emp) WHERE rn BETWEEN 4 AND 6` |
| 33 | 日期运算 | sql | MONTHS_BETWEEN 司龄 | `SELECT ename, ROUND(MONTHS_BETWEEN('1985-01-01',hiredate),1) FROM emp` |
| 34 | 集合 | sql | MINUS 求没有员工的部门 | `SELECT dname FROM dept MINUS SELECT d.dname FROM dept d JOIN emp e ON d.deptno=e.deptno` |
| 35 | 层次查询 | choice | CONNECT BY 层次查询关键字 | 答案 A:`START WITH ... CONNECT BY PRIOR` |
| 36 | 行列转换 | choice | PIVOT 行转列关键字 | 答案 A:PIVOT |
| 37 | 序列 | choice | 取序列下一个值 | 答案 A:`my_seq.NEXTVAL` |
| 38 | 事务 | choice | Oracle 默认隔离级别 | 答案 A:READ COMMITTED |
| 39 | 索引 | choice | 高区分度列适合的索引 | 答案 A:B-Tree 索引 |
| 40 | 数据类型 | choice | VARCHAR2 vs CHAR | 答案 A:VARCHAR2 变长,CHAR 定长 |
| 41 | 外连接语法 | choice | `(+)` 在右表侧表示 | 答案 A:左外连接 |
| 42 | 执行计划 | choice | 查看执行计划的命令 | 答案 A:`EXPLAIN PLAN FOR <SQL>` |

> 每道 sql 题的 `explanation` 需写清:① 执行结果有几行、关键行是什么;② 语法讲解;③ 易错点/面试考点。
> 每道 choice 题的 `explanation` 需写清正确选项含义 + 其他选项为什么错 + 示例。

---

## 7. 模块 3 设计:主程序与交互(oracle_practice.py)

### 7.1 主菜单

```
═════════════════════════════════════════
   Oracle SQL 练习程序
   (内置 EMP/DEPT/SALGRADE 示例数据,本地真实执行)
═════════════════════════════════════════
 1. 自由练习    —— 任意输入 SQL,看真实执行效果
 2. 题库练习    —— 42 道题自动判分 + 解析
 3. 模拟考试    —— 随机组卷,交卷出成绩单
 4. 错题本      —— 重做做错的题
 5. 学习统计    —— 正确率与进度(自动保存)
 6. 查看表结构与数据
 0. 退出
```

### 7.2 功能 1:自由练习

- **流程**:循环提示 `SQL> ` 输入;以分号 `;` 结尾或空行提交;`exit/quit` 返回菜单。
- **内置命令**(不执行 SQL,直接处理):
  - `tables` — 列出所有表
  - `desc 表名` — 显示表结构(列名+类型+中文说明)
  - `show 表名 [n]` / `preview 表名` — 预览前 n 行数据
  - `help` — 使用提示
- **执行成功**:打印"执行效果展示"区块(见第 8 章)。
- **执行失败**:打印 `❌ 执行出错: <错误信息>`。

### 7.3 功能 2:题库练习

- 子菜单:① 顺序做全部 ② 随机抽题 ③ 按难度练习(初级/中级/高级)。
- 逐题作答(见 7.6 判分流程),结束后打印小结:`完成 X 题 | 答对 Y 题 | 正确率 Z%`。

### 7.4 功能 3:模拟考试

- 选择出题范围(全题库 / 某难度)→ 输入数量(默认 10)→ 随机抽题组卷。
- 逐题作答(考试中不即时记录统计),中途可 `exit` 提前交卷。
- 交卷打印**成绩单**:总分(100 制)、正确率、答对/答错数、错题编号、评级(≥90 优秀 / ≥75 良好 / ≥60 及格 / 其余需加强)。
- 交卷后把本卷结果一次性计入统计与错题本。

### 7.5 功能 4/5/6:错题本 / 学习统计 / 表预览

- **错题本**:列出所有答错过的题(含错几次),可一键"重做错题";某题重做答对则从错题本移除。
- **学习统计**:总答题数、总正确率;按难度分组的正确率 + 进度条(`████░░`);显示数据文件路径。
- **表预览**:依次打印每张表的结构 + 前 5 行数据 + 总行数。

### 7.6 判分流程(每题通用)

```
出题(显示:难度图标 + 题号 + 标题 + 题干 + 提示)
  ↓
用户作答(sql 题输入 SQL / choice 题输入 A-D)
  ↓
执行用户 SQL 并展示执行效果表格
  ↓
比对结果集(sql)或比对选项(choice)
  ↓
✅ 正确 → 记录统计、从错题本移除
❌ 错误 → 显示标准答案 + 标准答案执行效果 + 解析;记录统计、加入错题本
```

---

## 8. 执行效果展示设计(重点)

这是用户明确要求的核心体验。**每次 SQL 执行成功后,必须打印如下区块**:

```
  ┌──────────────────────────────────────────┐
  │             执行效果展示                 │
  └──────────────────────────────────────────┘
  转换后执行: SELECT ...(若发生语法转换才显示)
  +----------+------+
  | ENAME    | SAL  |
  +----------+------+
  | KING     | 5000 |
  | SCOTT    | 3000 |
  +----------+------+
  → 返回 6 行 | 耗时 1.23 ms
```

### 8.1 表格打印要求

- 用 `+---+` 和 `| |` 画 ASCII 边框,列宽按内容自适应。
- **中文字符按 2 列宽度计算**(用 `unicodedata.east_asian_width`,W/F 记 2,否则 1),否则中文表格对不齐。
- `NULL` 值显示为字符串 `NULL`。
- 超过 20 行只显示前 20 行,末尾提示 `... 仅显示前 20 行,共 N 行`。
- 表头用列名(取 SELECT 的列名或表达式)。

### 8.2 结果信息

- 打印 `→ 返回 N 行 | 耗时 X.XX ms`(SELECT);非查询语句显示 `影响 N 行`。
- 若发生 Oracle→SQLite 转换,额外打印 `转换后执行: <转换后的 SQL>`,帮助用户理解等价写法。

---

## 9. 持久化设计(JSON 文件)

目录 `data/` 首次运行时自动创建。

### progress.json(学习统计)

```json
{
  "answered": 57,
  "correct": 40,
  "by_difficulty": {
    "初级": {"answered": 20, "correct": 18},
    "中级": {"answered": 22, "correct": 15},
    "高级": {"answered": 15, "correct": 7}
  }
}
```

### wrongbook.json(错题本)

```json
{
  "items": {
    "16": 2,
    "32": 1
  }
}
```

- key 为题号(字符串),value 为答错次数;答对后删除该 key。

---

## 10. 编码与兼容性要求

- Windows 控制台中文输出:程序开头用 `sys.stdout.reconfigure(encoding="utf-8")` 和
  `sys.stdin.reconfigure(encoding="utf-8")`,并包在 `try/except` 里兼容非 Windows。
- 所有文件 UTF-8 编码,文件头加 `# -*- coding: utf-8 -*-`。
- 源码里的中文引号统一用「」或 " ",**禁止在 Python 字符串内使用英文双引号 `"` 包裹中文**
  (否则字符串会提前结束导致语法错误)。

---

## 11. 验收标准(实现完成后必须逐条通过)

1. `python oracle_practice.py` 能正常启动并显示主菜单,中文无乱码。
2. `--self-test` 模式能遍历题库所有 sql 题的 `answer_sql`,全部执行成功且结果非空。
3. 自由练习输入 `SELECT ename, sal FROM emp WHERE sal > 2000` 能打印出 6 行结果表格。
4. 自由练习输入 `SELECT ename, NVL(comm,0) FROM emp` 能执行,奖金 NULL 显示 0。
5. 自由练习输入 `SELECT ename, sal FROM (SELECT ename, sal FROM emp ORDER BY sal DESC) WHERE ROWNUM <= 3`
   能返回 3 行(KING/SCOTT/FORD)。
6. 自由练习输入 `SELECT SYSDATE FROM DUAL` 能返回当前时间。
7. 题库练习做对一道题后,`data/progress.json` 中 answered/correct 相应 +1。
8. 做错一道题后,错题本出现该题,重做答对后从错题本消失。
9. 模拟考试交卷能打印成绩单与评级。
10. 表格打印:含中文(如 DECODE 转出的"经理/职员")时列依然对齐。

---

## 12. 可直接复制给 AI 的实现提示词

把下面这段(连同本文档一起)发给其他 AI:

```text
请严格按照附带的《结构设计文档》实现一个 Python 命令行 Oracle SQL 练习程序。
要求:
1. 严格遵循文档第 2 章的技术约束:Python 标准库、零第三方依赖、用 sqlite3 模拟 Oracle。
2. 严格实现文档第 4 章的表结构与示例数据(EMP 14 行 / DEPT 4 行 / SALGRADE 5 行 / DUAL 1 行)。
3. 严格实现文档第 5 章的语法转换规则表和函数模拟清单。
4. 按文档第 6.3 章的 42 题清单编写题库,每题都要有完整的中文解析。
5. 按文档第 7、8 章实现交互流程与"执行效果展示"(ASCII 表格,中文按 2 列对齐)。
6. 按文档第 9 章实现 JSON 持久化。
7. 输出三个文件:oracle_practice.py、db_engine.py、question_bank.py,外加 README.md。
8. 完成后自行运行文档第 11 章的验收标准,确保全部通过再交付。
9. 全部界面和注释使用简体中文,遵守文档第 10 章的编码规范。
```

---

## 附:与"AI 私教"配合使用

本文档产出的**程序**(本地真实执行)与另一份 `oracle_prompt.md`(让 AI 扮演 Oracle 私教、讲解纠错)
可以搭配使用:
- 用**程序**真实执行 SQL、自动判分、看执行效果、记录错题;
- 把做错的题或不懂的知识点,复制给 **AI 私教** 请求讲解。

这样"真实执行 + AI 讲解"两条腿走路,练习效果最好。

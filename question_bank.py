# -*- coding: utf-8 -*-
"""题库数据:42 道题(32 道 sql 书写题 + 10 道 choice 选择题)。

每题结构:
    id / difficulty / topic / type / title / question / hint
    sql 题: answer_sql
    choice 题: answer(正确字母) / options(4 个选项)
    explanation: 详细解析
"""

QUESTION_BANK = [
    # ---------------- 初级 12 题 ----------------
    {
        'id': 1, 'difficulty': '初级', 'topic': '基础查询', 'type': 'sql',
        'title': '查询所有员工',
        'question': '从 EMP 表查询所有员工的姓名(ename)、岗位(job)和工资(sal)。',
        'hint': 'SELECT 列1, 列2, 列3 FROM 表名',
        'answer_sql': 'SELECT ename, job, sal FROM emp',
        'answer': None, 'options': None,
        'explanation': (
            '① 执行结果共 14 行,包含全部员工。\n'
            '② 语法:SELECT 列名列表 FROM 表名;星号 * 代表所有列,'
            '但实际开发中推荐明确写出列名。\n'
            '③ 易错点:SQL 关键字不区分大小写,习惯上关键字大写、'
            '表名/列名小写;语句以分号结尾。'
        ),
    },
    {
        'id': 2, 'difficulty': '初级', 'topic': '条件查询', 'type': 'sql',
        'title': '工资高于 2000 的员工',
        'question': '查询工资大于 2000 的员工姓名和工资。',
        'hint': '用 WHERE 子句过滤行',
        'answer_sql': 'SELECT ename, sal FROM emp WHERE sal > 2000',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 6 行:JONES 2975、BLAKE 2850、CLARK 2450、'
            'SCOTT 3000、KING 5000、FORD 3000。\n'
            '② 语法:WHERE 后写过滤条件,支持 > < >= <= = <> 等比较运算符。\n'
            '③ 易错点:判断相等是一个 =(不是 ==);不等号写 <> 或 !=。'
        ),
    },
    {
        'id': 3, 'difficulty': '初级', 'topic': '条件查询', 'type': 'sql',
        'title': '10 号部门的员工',
        'question': '查询 10 号部门所有员工的姓名和岗位。',
        'hint': '部门号是数字列,直接写 deptno = 10',
        'answer_sql': 'SELECT ename, job FROM emp WHERE deptno = 10',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:CLARK(MANAGER)、KING(PRESIDENT)、MILLER(CLERK)。\n'
            '② 语法:数值与日期直接比较,不加引号;字符串才用单引号。\n'
            '③ 易错点:Oracle 中字符串只能用单引号,双引号是标识符(列名)的写法。'
        ),
    },
    {
        'id': 4, 'difficulty': '初级', 'topic': '排序', 'type': 'sql',
        'title': '按工资降序排列',
        'question': '查询所有员工的姓名和工资,按工资从高到低排列。',
        'hint': 'ORDER BY 列名 DESC',
        'answer_sql': 'SELECT ename, sal FROM emp ORDER BY sal DESC',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行,第一行是 KING(5000),SCOTT 与 FORD 并列 3000。\n'
            '② 语法:ORDER BY 列 DESC 降序,ASC 升序(默认,可省略)。\n'
            '③ 易错点:ORDER BY 是 SQL 执行的最后一步,放在 WHERE/GROUP BY 之后;'
            'Oracle 中 NULL 升序排最后、降序排最前。'
        ),
    },
    {
        'id': 5, 'difficulty': '初级', 'topic': '聚合', 'type': 'sql',
        'title': '各部门平均工资',
        'question': '查询每个部门的部门号和平均工资。',
        'hint': 'GROUP BY 分组 + AVG 聚合',
        'answer_sql': 'SELECT deptno, AVG(sal) FROM emp GROUP BY deptno',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:10 号约 2916.67、20 号 2175、30 号约 1566.67。\n'
            '② 语法:GROUP BY 把相同部门号的行归为一组,组内用 AVG 求平均; '
            '常用聚合函数 AVG/SUM/COUNT/MAX/MIN。\n'
            '③ 易错点:分组后 SELECT 只能出现分组列和聚合函数,'
            '写 SELECT ename 会报 ORA-00979(不是 GROUP BY 表达式)。'
        ),
    },
    {
        'id': 6, 'difficulty': '初级', 'topic': '聚合', 'type': 'sql',
        'title': '员工总人数',
        'question': '查询 EMP 表的员工总人数。',
        'hint': 'COUNT(*) 统计行数',
        'answer_sql': 'SELECT COUNT(*) FROM emp',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 1 行,值为 14。\n'
            '② 语法:COUNT(*) 统计所有行;COUNT(列名) 只统计该列非 NULL 的行。\n'
            '③ 易错点:COUNT(comm) 的结果是 4 而不是 14——'
            '只有 4 名销售员有奖金,这是 NULL 语义的经典考点。'
        ),
    },
    {
        'id': 7, 'difficulty': '初级', 'topic': '去重', 'type': 'sql',
        'title': '所有不同的岗位',
        'question': '查询 EMP 表中所有不同的岗位(job),不重复。',
        'hint': 'DISTINCT 关键字放在 SELECT 后面',
        'answer_sql': 'SELECT DISTINCT job FROM emp',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 5 行:CLERK、SALESMAN、PRESIDENT、MANAGER、ANALYST。\n'
            '② 语法:DISTINCT 放在 SELECT 之后、第一个列名之前。\n'
            '③ 易错点:DISTINCT 作用于其后「所有列的组合」——'
            'SELECT DISTINCT job, deptno 是对两列组合去重,不是只对 job 去重。'
        ),
    },
    {
        'id': 8, 'difficulty': '初级', 'topic': '模糊查询', 'type': 'sql',
        'title': '姓名以 S 开头',
        'question': '查询姓名以字母 S 开头的员工姓名。',
        'hint': "LIKE 'S%'",
        'answer_sql': "SELECT ename FROM emp WHERE ename LIKE 'S%'",
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 2 行:SMITH、SCOTT。\n'
            '② 语法:LIKE 模糊匹配,% 匹配任意多个字符(含 0 个),'
            '_ 匹配单个字符。\n'
            '③ 易错点:LIKE 默认区分大小写,"s%" 匹配不到 SMITH;'
            '匹配内容里的 % _ 本身要用 ESCAPE 转义。'
        ),
    },
    {
        'id': 9, 'difficulty': '初级', 'topic': '条件查询', 'type': 'sql',
        'title': '工资在 1500 到 3000 之间',
        'question': '查询工资在 1500 至 3000 之间(含边界)的员工姓名和工资。',
        'hint': 'BETWEEN ... AND ...',
        'answer_sql': ('SELECT ename, sal FROM emp '
                       'WHERE sal BETWEEN 1500 AND 3000'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 7 行:ALLEN 1600、TURNER 1500、JONES 2975、BLAKE 2850、'
            'CLARK 2450、SCOTT 3000、FORD 3000。\n'
            '② 语法:BETWEEN a AND b 是闭区间 [a, b],'
            '等价于 sal >= 1500 AND sal <= 3000。\n'
            '③ 易错点:BETWEEN 必须「小值在前大值在后」;'
            '日期区间也常用 BETWEEN,但更推荐左闭右开写法。'
        ),
    },
    {
        'id': 10, 'difficulty': '初级', 'topic': '空值', 'type': 'sql',
        'title': '奖金为空的员工',
        'question': '查询没有奖金(comm 为空)的员工姓名。',
        'hint': 'IS NULL,不能用 = NULL',
        'answer_sql': 'SELECT ename FROM emp WHERE comm IS NULL',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 10 行:除 4 名销售员(ALLEN/WARD/MARTIN/TURNER)外的所有员工。\n'
            '② 语法:NULL 的判断只能用 IS NULL / IS NOT NULL。\n'
            '③ 易错点:comm = NULL 永远查不出结果——NULL 与任何值比较都返回「未知」,'
            '这是 SQL 最高频的面试坑。'
        ),
    },
    {
        'id': 11, 'difficulty': '初级', 'topic': '条件查询', 'type': 'sql',
        'title': 'MANAGER 或 ANALYST',
        'question': "查询岗位为 MANAGER 或 ANALYST 的员工姓名、岗位和工资。",
        'hint': "IN ('MANAGER', 'ANALYST')",
        'answer_sql': ("SELECT ename, job, sal FROM emp "
                       "WHERE job IN ('MANAGER', 'ANALYST')"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 5 行:JONES、BLAKE、CLARK(MANAGER),SCOTT、FORD(ANALYST)。\n'
            '② 语法:IN (值列表) 等价于多个 OR 条件的简写。\n'
            '③ 易错点:IN 里的字符串要加单引号;NOT IN 遇到列表/子查询含 NULL 时'
            '会一条也查不出来,是著名陷阱。'
        ),
    },
    {
        'id': 12, 'difficulty': '初级', 'topic': '模糊查询', 'type': 'sql',
        'title': '姓名中含字母 A',
        'question': '查询姓名中包含字母 A 的员工姓名。',
        'hint': "LIKE '%A%'",
        'answer_sql': "SELECT ename FROM emp WHERE ename LIKE '%A%'",
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 7 行:ALLEN、WARD、MARTIN、BLAKE、CLARK、ADAMS、JAMES。\n'
            "② 语法:'%A%' 中 % 在两侧表示 A 出现在任意位置都匹配。\n"
            "③ 易错点:区分大小写,'A' 匹配不到小写 a;"
            "如需不区分大小写可用 UPPER(ename) LIKE '%A%'。"
        ),
    },
    # ---------------- 中级 14 题 ----------------
    {
        'id': 13, 'difficulty': '中级', 'topic': '连接', 'type': 'sql',
        'title': '员工姓名 + 部门名(内连接)',
        'question': '查询每个员工的姓名及其所在部门的名称(用内连接)。',
        'hint': 'emp e JOIN dept d ON e.deptno = d.deptno',
        'answer_sql': ('SELECT e.ename, d.dname FROM emp e '
                       'JOIN dept d ON e.deptno = d.deptno'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:40 号部门 OPERATIONS 没有员工,内连接不会出现。\n'
            '② 语法:JOIN ... ON 是标准内连接写法,ON 后写两表的关联条件。\n'
            '③ 易错点:忘记写 ON 会变成笛卡尔积(14 × 4 = 56 行);'
            '表别名 e、d 让列引用更清晰。'
        ),
    },
    {
        'id': 14, 'difficulty': '中级', 'topic': '连接', 'type': 'sql',
        'title': '左外连接',
        'question': '用左外连接查询所有员工的姓名及其部门名(左表为 emp)。',
        'hint': 'LEFT JOIN 保留左表全部行',
        'answer_sql': ('SELECT e.ename, d.dname FROM emp e '
                       'LEFT JOIN dept d ON e.deptno = d.deptno'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果仍是 14 行:所有员工都有部门,所以与内连接相同。\n'
            '② 语法:LEFT JOIN 以左表为主,右表无匹配的行补 NULL。\n'
            '③ 考点:若反过来写 FROM dept d LEFT JOIN emp e,'
            '会得到 15 行,多出 OPERATIONS 一行(ename 为 NULL)——'
            '理解连接方向是本题的关键。'
        ),
    },
    {
        'id': 15, 'difficulty': '中级', 'topic': '子查询', 'type': 'sql',
        'title': '工资高于全公司平均',
        'question': '查询工资高于全公司平均工资的员工姓名和工资。',
        'hint': 'WHERE sal > (SELECT AVG(sal) FROM emp)',
        'answer_sql': ('SELECT ename, sal FROM emp '
                       'WHERE sal > (SELECT AVG(sal) FROM emp)'),
        'answer': None, 'options': None,
        'explanation': (
            '① 全公司平均工资约 2073.21,结果 6 行:JONES、BLAKE、CLARK、'
            'SCOTT、KING、FORD。\n'
            '② 语法:子查询先独立执行算出平均值,再作为外层的比较值;'
            '也可用 WITH 子句(CTE)先算后用。\n'
            '③ 易错点:单行子查询只能配单行比较符;'
            '若子查询返回多行,要用 IN / ANY / ALL。'
        ),
    },
    {
        'id': 16, 'difficulty': '中级', 'topic': '子查询', 'type': 'sql',
        'title': '工资高于本部门平均(相关子查询)',
        'question': '查询工资高于「所在部门平均工资」的员工姓名、部门号和工资。',
        'hint': '子查询里用外层别名:WHERE deptno = e.deptno',
        'answer_sql': ('SELECT ename, deptno, sal FROM emp e '
                       'WHERE sal > (SELECT AVG(sal) FROM emp '
                       'WHERE deptno = e.deptno)'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 6 行:KING(10)、JONES、SCOTT、FORD(20)、ALLEN、BLAKE(30)。\n'
            '② 语法:相关子查询——内层引用外层的 e.deptno,'
            '外层每行都重新计算一次本部门平均。「超过本组平均」是经典模板。\n'
            '③ 易错点:别忘了内层写 deptno = e.deptno;'
            '漏写会变成和全公司平均比较。'
        ),
    },
    {
        'id': 17, 'difficulty': '中级', 'topic': '分组过滤', 'type': 'sql',
        'title': '平均工资超过 2000 的部门',
        'question': '查询平均工资超过 2000 的部门号和平均工资。',
        'hint': 'GROUP BY ... HAVING AVG(sal) > 2000',
        'answer_sql': ('SELECT deptno, AVG(sal) FROM emp '
                       'GROUP BY deptno HAVING AVG(sal) > 2000'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 2 行:10 号(约 2916.67)和 20 号(2175);'
            '30 号平均约 1566.67 被过滤。\n'
            '② 语法:WHERE 在分组前过滤「行」,HAVING 在分组后过滤「组」; '
            '过滤聚合值必须用 HAVING。\n'
            '③ 易错点:把 AVG(sal) > 2000 写进 WHERE 会直接报错;'
            '执行顺序是 FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY。'
        ),
    },
    {
        'id': 18, 'difficulty': '中级', 'topic': '自连接', 'type': 'sql',
        'title': '员工与上级',
        'question': '查询每个员工的姓名及其上级的姓名(没有上级的也要显示)。',
        'hint': '同一张表取两个别名,用 LEFT JOIN',
        'answer_sql': ('SELECT e.ename, m.ename FROM emp e '
                       'LEFT JOIN emp m ON e.mgr = m.empno'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行,KING 的上级显示 NULL(他是总裁,没有上级)。\n'
            '② 语法:自连接——同一张表取两个别名 e(员工视角)、m(上级视角), '
            '连接条件 e.mgr = m.empno。\n'
            '③ 易错点:若用内连接会丢掉 KING 这一行(MGR 为 NULL 匹配不上),'
            '所以必须 LEFT JOIN。'
        ),
    },
    {
        'id': 19, 'difficulty': '中级', 'topic': 'Top-N', 'type': 'sql',
        'title': '工资最高的 3 人(ROWNUM)',
        'question': '查询工资最高的前 3 名员工姓名和工资(Oracle Top-N 写法)。',
        'hint': '先在子查询 ORDER BY,外层 ROWNUM <= 3',
        'answer_sql': ('SELECT ename, sal FROM '
                       '(SELECT ename, sal FROM emp ORDER BY sal DESC) '
                       'WHERE ROWNUM <= 3'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:KING 5000、SCOTT 3000、FORD 3000。\n'
            '② 语法:Oracle 经典 Top-N——先在子查询内排序, '
            '外层用 ROWNUM <= n 截取(本程序自动转换为 LIMIT)。\n'
            '③ 易错点:直接写 WHERE ROWNUM <= 3 再 ORDER BY 是错的——'
            'ROWNUM 在排序之前分配,会「先随便取 3 行再排序」。'
        ),
    },
    {
        'id': 20, 'difficulty': '中级', 'topic': 'EXISTS', 'type': 'sql',
        'title': '有员工的部门',
        'question': '用 EXISTS 查询至少有一名员工的部门名称。',
        'hint': 'WHERE EXISTS (SELECT 1 FROM emp e WHERE e.deptno = d.deptno)',
        'answer_sql': ('SELECT dname FROM dept d WHERE EXISTS '
                       '(SELECT 1 FROM emp e WHERE e.deptno = d.deptno)'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:ACCOUNTING、RESEARCH、SALES(OPERATIONS 无员工)。\n'
            '② 语法:EXISTS 只关心子查询「是否有行返回」,找到一行即短路返回, '
            '大数据量下通常比 IN 高效。\n'
            '③ 等价写法:SELECT dname FROM dept WHERE deptno IN '
            '(SELECT deptno FROM emp);EXISTS 常配 SELECT 1 或 SELECT *。'
        ),
    },
    {
        'id': 21, 'difficulty': '中级', 'topic': '集合', 'type': 'sql',
        'title': 'UNION 合并去重',
        'question': '查询「工资大于 2500」或「岗位是 CLERK」的员工姓名'
                    '(用 UNION 合并两个查询)。',
        'hint': '两个 SELECT 用 UNION 连接',
        'answer_sql': ("SELECT ename FROM emp WHERE sal > 2500 "
                       "UNION SELECT ename FROM emp WHERE job = 'CLERK'"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 9 行:高薪 5 人(JONES/BLAKE/SCOTT/KING/FORD)'
            '+ 职员 4 人(SMITH/JAMES/ADAMS/MILLER),无重叠。\n'
            '② 语法:UNION 合并并去重;UNION ALL 不去重、更快;'
            '交集用 INTERSECT,差集用 MINUS。\n'
            '③ 易错点:UNION 两侧列数与类型必须一致;'
            '结果列名以第一个 SELECT 为准。'
        ),
    },
    {
        'id': 22, 'difficulty': '中级', 'topic': '非等值连接', 'type': 'sql',
        'title': '员工与工资等级',
        'question': '查询每个员工的姓名、工资及其对应的工资等级'
                    '(连接 SALGRADE 表)。',
        'hint': 'ON e.sal BETWEEN s.losal AND s.hisal',
        'answer_sql': ('SELECT e.ename, e.sal, s.grade FROM emp e '
                       'JOIN salgrade s ON e.sal BETWEEN s.losal AND s.hisal'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:如 SMITH 800 → 1 级,KING 5000 → 5 级。\n'
            '② 语法:非等值连接——ON 条件不是等号而是 BETWEEN 范围匹配, '
            'SALGRADE 表就是为这种练习设计的。\n'
            '③ 易错点:区间边界重叠会导致一行匹配多个等级(笛卡尔式膨胀), '
            'SALGRADE 的区间首尾相接不重叠,所以每人只命中一条。'
        ),
    },
    {
        'id': 23, 'difficulty': '中级', 'topic': '分组', 'type': 'sql',
        'title': '部门人数与最高最低工资',
        'question': '查询每个部门的部门号、人数、最高工资和最低工资。',
        'hint': 'COUNT/MAX/MIN 配合 GROUP BY',
        'answer_sql': ('SELECT deptno, COUNT(*), MAX(sal), MIN(sal) '
                       'FROM emp GROUP BY deptno'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:10 号(3 人/5000/1300)、20 号(5 人/3000/800)、'
            '30 号(6 人/2850/950)。\n'
            '② 语法:一行里可以同时取多个聚合指标,互不影响。\n'
            '③ 易错点:SELECT 出现 deptno 就必须 GROUP BY deptno;'
            'COUNT(*) 统计组内所有行。'
        ),
    },
    {
        'id': 24, 'difficulty': '中级', 'topic': '子查询', 'type': 'sql',
        'title': '与 SCOTT 同部门的人',
        'question': "查询与 SCOTT 同一部门的所有员工姓名(子查询实现)。",
        'hint': "子查询先求出 SCOTT 的 deptno",
        'answer_sql': ("SELECT ename FROM emp WHERE deptno = "
                       "(SELECT deptno FROM emp WHERE ename = 'SCOTT')"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 5 行:SMITH、JONES、SCOTT、ADAMS、FORD(都是 20 号部门)。\n'
            '② 语法:子查询返回 SCOTT 的部门号 20,外层做等值过滤。\n'
            '③ 易错点:结果包含 SCOTT 本人;若要排除自己, '
            "加 AND ename <> 'SCOTT'。"
        ),
    },
    {
        'id': 25, 'difficulty': '中级', 'topic': '字符串函数', 'type': 'sql',
        'title': '姓名小写与前 3 个字符',
        'question': '查询每个员工姓名的小写形式,以及姓名的前 3 个字符。',
        'hint': 'LOWER() 和 SUBSTR(ename, 1, 3)',
        'answer_sql': 'SELECT LOWER(ename), SUBSTR(ename, 1, 3) FROM emp',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:如 SMITH → smith / smi。\n'
            '② 语法:LOWER 转小写;SUBSTR(串, 起点, 长度) 起点从 1 开始, '
            '不是 0。\n'
            '③ 易错点:Oracle 下标从 1 起,写 SUBSTR(ename, 0, 3) 也会被当作 1 '
            '处理(结果相同),但 MySQL 习惯不同,面试常考; '
            '负数起点表示从末尾倒数。'
        ),
    },
    {
        'id': 26, 'difficulty': '中级', 'topic': '日期', 'type': 'sql',
        'title': '1981 年入职的员工',
        'question': '查询 1981 年入职的所有员工姓名和入职日期。',
        'hint': "hiredate >= '1981-01-01' AND hiredate < '1982-01-01'",
        'answer_sql': ("SELECT ename, hiredate FROM emp "
                       "WHERE hiredate >= '1981-01-01' "
                       "AND hiredate < '1982-01-01'"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 10 行:ALLEN、WARD、JONES、MARTIN、BLAKE、CLARK、KING、'
            'TURNER、JAMES、FORD(SMITH 是 1980、MILLER 1982、SCOTT/ADAMS 1987)。\n'
            '② 语法:「左闭右开」写法 >= 起点 AND < 终点,不用纠结年末边界, '
            '是日期范围查询的最佳实践。\n'
            "③ 易错点:TO_CHAR(hiredate, 'YYYY') = '1981' 也能实现, "
            '但对列套函数后无法走索引,大数据量下性能差。'
        ),
    },
    # ---------------- 高级 16 题 ----------------
    {
        'id': 27, 'difficulty': '高级', 'topic': 'Oracle 函数', 'type': 'sql',
        'title': 'NVL 处理空奖金',
        'question': '查询所有员工的姓名和奖金,奖金为空的显示 0(用 NVL)。',
        'hint': 'NVL(comm, 0)',
        'answer_sql': 'SELECT ename, NVL(comm, 0) FROM emp',
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行,10 个无奖金者显示 0,4 名销售显示实际奖金'
            '(TURNER 的奖金本身就是 0)。\n'
            '② 语法:NVL(x, y):x 为 NULL 取 y,否则取 x; '
            '近亲 NVL2(x, a, b) 是「非空取 a 否则取 b」。\n'
            '③ 易错点:comm + 100 在 comm 为 NULL 时整体是 NULL, '
            '所以要先 NVL 再做算术;SQL 标准等价函数是 COALESCE(可多参数)。'
        ),
    },
    {
        'id': 28, 'difficulty': '高级', 'topic': 'Oracle 函数', 'type': 'sql',
        'title': 'DECODE 岗位翻译',
        'question': '用 DECODE 把岗位翻译成中文:MANAGER→经理、SALESMAN→销售、'
                    'CLERK→职员、ANALYST→分析师、PRESIDENT→总裁,'
                    '其他岗位显示「其他」。',
        'hint': "DECODE(job, 'MANAGER', '经理', ..., '其他')",
        'answer_sql': ("SELECT ename, DECODE(job, 'MANAGER', '经理', "
                       "'SALESMAN', '销售', 'CLERK', '职员', "
                       "'ANALYST', '分析师', 'PRESIDENT', '总裁', '其他') "
                       "FROM emp"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:经理 3 人、销售 4 人、职员 4 人、分析师 2 人、总裁 1 人, '
            '默认值「其他」本例未被用到。\n'
            '② 语法:DECODE(列, 值1, 译1, 值2, 译2, ..., 默认值) '
            '逐对匹配,是多个 CASE WHEN 的简写,Oracle 面试必考。\n'
            '③ 易错点:DECODE 认为 NULL 与 NULL 相等(与普通比较不同); '
            "标准写法 CASE job WHEN 'MANAGER' THEN '经理' ... ELSE '其他' END "
            '更通用。'
        ),
    },
    {
        'id': 29, 'difficulty': '高级', 'topic': '日期格式化', 'type': 'sql',
        'title': 'TO_CHAR 格式化入职年月',
        'question': "查询员工姓名及入职年月,格式为「YYYY年MM月」(用 TO_CHAR)。",
        'hint': "TO_CHAR(hiredate, 'YYYY年MM月')",
        'answer_sql': ("SELECT ename, TO_CHAR(hiredate, 'YYYY年MM月') "
                       "FROM emp"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:如 SMITH → 1980年12月、KING → 1981年11月。\n'
            '② 语法:TO_CHAR(日期, 格式) 把日期转字符串, '
            '常用占位符:YYYY 年、MM 月、DD 日、HH24 时、MI 分、SS 秒; '
            '格式串里的中文等非占位符字符会原样保留。\n'
            "③ 易错点:反方向转换用 TO_DATE('1981-11-17', 'YYYY-MM-DD'); "
            'WHERE 里对列套 TO_CHAR 会破坏索引。'
        ),
    },
    {
        'id': 30, 'difficulty': '高级', 'topic': '分析函数', 'type': 'sql',
        'title': '部门内工资排名(RANK)',
        'question': '查询员工姓名、部门号、工资,以及在本部门内的工资排名'
                    '(用 RANK 分析函数,工资高的排第 1)。',
        'hint': 'RANK() OVER (PARTITION BY deptno ORDER BY sal DESC)',
        'answer_sql': ('SELECT ename, deptno, sal, '
                       'RANK() OVER (PARTITION BY deptno '
                       'ORDER BY sal DESC) FROM emp'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:每个部门独立排名,如 20 号部门 SCOTT/FORD 并列第 1、'
            'JONES 第 3。\n'
            '② 语法:RANK() OVER (PARTITION BY 分区列 ORDER BY 排序列) '
            '先按部门分区、区内按工资降序排名;分析函数不减少行数, '
            '这是与 GROUP BY 最大的区别。\n'
            '③ 易错点:RANK 并列跳号(1,1,3)、DENSE_RANK 并列不跳号(1,1,2)、'
            'ROW_NUMBER 强制连续(1,2,3),三者对比是高频面试题。'
        ),
    },
    {
        'id': 31, 'difficulty': '高级', 'topic': '分析函数', 'type': 'sql',
        'title': '累计工资(SUM OVER)',
        'question': '查询员工姓名、工资,以及按工资升序的累计工资'
                    '(用 SUM OVER 分析函数)。',
        'hint': 'SUM(sal) OVER (ORDER BY sal)',
        'answer_sql': ('SELECT ename, sal, SUM(sal) OVER (ORDER BY sal) '
                       'FROM emp'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:按 sal 升序逐行累加,最后一行累计 29025(工资总额);'
            '相同工资的行(SCOTT/FORD)会一起累加。\n'
            '② 语法:SUM(...) OVER (ORDER BY ...) 形成累计窗口; '
            'OVER() 里不写 ORDER BY 则每行都是全表总计。\n'
            '③ 易错点:OVER 的默认窗口是 RANGE(相同值一起算), '
            '想逐行累计不并列需写 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW。'
        ),
    },
    {
        'id': 32, 'difficulty': '高级', 'topic': '分页', 'type': 'sql',
        'title': '第 4~6 名(ROW_NUMBER 分页)',
        'question': '按工资降序取第 4 名到第 6 名的员工姓名和工资'
                    '(用 ROW_NUMBER 生成序号后过滤)。',
        'hint': '子查询里 ROW_NUMBER() OVER (ORDER BY sal DESC) 生成 rn',
        'answer_sql': ('SELECT ename, sal FROM (SELECT ename, sal, '
                       'ROW_NUMBER() OVER (ORDER BY sal DESC) rn FROM emp) '
                       'WHERE rn BETWEEN 4 AND 6'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 3 行:JONES 2975、BLAKE 2850、CLARK 2450。'
            '(前 3 名是 KING 5000、SCOTT 3000、FORD 3000。)\n'
            '② 语法:ROW_NUMBER() OVER (ORDER BY ...) 生成连续序号, '
            '外层用 rn BETWEEN 过滤区间,这是 Oracle 12c 之前的通用分页方案。\n'
            '③ 易错点:分析函数不能直接写在 WHERE 里(执行顺序在 WHERE 之后), '
            '必须包一层子查询;12c+ 可用 OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY。'
        ),
    },
    {
        'id': 33, 'difficulty': '高级', 'topic': '日期运算', 'type': 'sql',
        'title': 'MONTHS_BETWEEN 计算司龄',
        'question': "以 1985-01-01 为基准日,查询每位员工的姓名和司龄"
                    "(月数,保留 1 位小数,用 MONTHS_BETWEEN + ROUND)。",
        'hint': "ROUND(MONTHS_BETWEEN('1985-01-01', hiredate), 1)",
        'answer_sql': ("SELECT ename, "
                       "ROUND(MONTHS_BETWEEN('1985-01-01', hiredate), 1) "
                       "FROM emp"),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 14 行:司龄最长 SMITH 约 48.5 个月,最短 ADAMS 约 -20.3 个月'
            '(1987 年入职,晚于基准日,为负)。\n'
            '② 语法:MONTHS_BETWEEN(d1, d2) 返回 d1-d2 的月数差,可含小数'
            '(按天折算 /31);ROUND(n, d) 四舍五入保留 d 位小数。\n'
            '③ 易错点:参数顺序决定正负;若两个日期都是当月最后一天, '
            'Oracle 返回整数月差。'
        ),
    },
    {
        'id': 34, 'difficulty': '高级', 'topic': '集合', 'type': 'sql',
        'title': 'MINUS 找没有员工的部门',
        'question': '用 MINUS 查询没有任何员工的部门名称。',
        'hint': '全部部门名 MINUS 有员工的部门名',
        'answer_sql': ('SELECT dname FROM dept '
                       'MINUS SELECT d.dname FROM dept d '
                       'JOIN emp e ON d.deptno = e.deptno'),
        'answer': None, 'options': None,
        'explanation': (
            '① 结果 1 行:OPERATIONS(40 号部门无人)。\n'
            '② 语法:MINUS 取第一个结果集减去第二个结果集(自动去重), '
            'Oracle 特有;本程序已自动转换为 SQLite 的 EXCEPT。\n'
            '③ 易错点:MINUS 前后两个查询的列数/类型要一致; '
            '等价替代:NOT EXISTS 或 NOT IN(注意 NOT IN 的 NULL 陷阱)。'
        ),
    },
    {
        'id': 35, 'difficulty': '高级', 'topic': '层次查询', 'type': 'choice',
        'title': 'CONNECT BY 层次查询',
        'question': ('在 Oracle 中,要从 KING 开始查询整棵「员工→上级」汇报树, '
                     '正确的层次查询写法是?'),
        'hint': None,
        'answer_sql': None,
        'answer': 'B',
        'options': [
            'SELECT ... FROM emp GROUP BY mgr CONNECT BY empno',
            "SELECT ... FROM emp START WITH mgr IS NULL "
            "CONNECT BY PRIOR empno = mgr",
            'SELECT ... FROM emp ORDER BY mgr CONNECT BY empno',
            'SELECT ... FROM emp WHERE PRIOR mgr = empno LEVEL',
        ],
        'explanation': (
            '正确答案 B:层次查询固定句式为 '
            'START WITH <树根条件> CONNECT BY PRIOR <父列=子列>。'
            'START WITH mgr IS NULL 定位 KING(没有上级),'
            'PRIOR empno = mgr 表示「父节点的 empno = 子节点的 mgr」,自顶向下遍历。\n'
            '其他选项错误:A 中 GROUP BY 不是层次查询关键字;'
            'C 中 ORDER BY 不能与 CONNECT BY 混用(保序要用 ORDER SIBLINGS BY);'
            'D 是拼凑的语法。\n'
            '补充:LEVEL 伪列表示层级深度(根为 1),SYS_CONNECT_BY_PATH 可拼路径, '
            '11g 后也可用递归 WITH(CTE)实现同样效果。'
        ),
    },
    {
        'id': 36, 'difficulty': '高级', 'topic': '行列转换', 'type': 'choice',
        'title': 'PIVOT 行转列',
        'question': 'Oracle 11g 引入的、把「行」转换为「列」的语法关键字是?',
        'hint': None,
        'answer_sql': None,
        'answer': 'A',
        'options': [
            'PIVOT',
            'UNPIVOT',
            'MERGE',
            'CROSS JOIN',
        ],
        'explanation': (
            '正确答案 A:PIVOT(11g 引入)把行转列——例如把各部门的多行工资'
            '汇总转成「一行、每部门一列」。典型写法:SELECT * FROM emp '
            'PIVOT (SUM(sal) FOR deptno IN (10 AS d10, 20 AS d20))。\n'
            '其他选项错误:B UNPIVOT 方向相反(列转行);'
            'C MERGE 是 upsert(存在则更新不存在则插入);'
            'D CROSS JOIN 是笛卡尔积。\n'
            '补充:11g 之前行转列要用 DECODE/CASE + GROUP BY 手工实现。'
        ),
    },
    {
        'id': 37, 'difficulty': '高级', 'topic': '序列', 'type': 'choice',
        'title': '序列取下一个值',
        'question': '创建序列 my_seq 后,取「下一个新值」的正确写法是?',
        'hint': None,
        'answer_sql': None,
        'answer': 'C',
        'options': [
            'my_seq.CURRVAL',
            'NEXT VALUE FOR my_seq',
            'my_seq.NEXTVAL',
            'my_seq.VALUE',
        ],
        'explanation': (
            '正确答案 C:my_seq.NEXTVAL 返回序列的下一个值并让序列前进; '
            '常用于主键生成:INSERT INTO t VALUES (my_seq.NEXTVAL, ...)。\n'
            '其他选项错误:A CURRVAL 返回当前会话最近一次 NEXTVAL 的值、不前进;'
            'B 是标准 SQL/SQL Server 的写法,Oracle 不支持;'
            'D 没有这种语法。\n'
            '补充:12c 起可用 IDENTITY 列(CREATE TABLE ... id NUMBER '
            'GENERATED AS IDENTITY)替代序列;序列 CACHE 可提升并发性能。'
        ),
    },
    {
        'id': 38, 'difficulty': '高级', 'topic': '事务', 'type': 'choice',
        'title': 'Oracle 默认隔离级别',
        'question': 'Oracle 数据库的默认事务隔离级别是?',
        'hint': None,
        'answer_sql': None,
        'answer': 'A',
        'options': [
            'READ COMMITTED(读已提交)',
            'SERIALIZABLE(串行化)',
            'READ UNCOMMITTED(读未提交)',
            'REPEATABLE READ(可重复读)',
        ],
        'explanation': (
            '正确答案 A:Oracle 默认 READ COMMITTED——每条语句执行时只能看到'
            '已提交的数据,语句级一致性由多版本读实现。\n'
            '其他选项错误:B SERIALIZABLE 需显式指定,开销大;'
            'C Oracle 不提供脏读(不依赖读锁,靠 undo 构造一致性版本);'
            'D Oracle 未实现标准 REPEATABLE READ 隔离级别。\n'
            '补充:Oracle 靠 undo 段 + SCN 实现「读不阻塞写、写不阻塞读」,'
            '这与 MySQL(锁 + MVCC)的机制不同,是面试常见对比点。'
        ),
    },
    {
        'id': 39, 'difficulty': '高级', 'topic': '索引', 'type': 'choice',
        'title': '高区分度列的索引选择',
        'question': '员工号、手机号这类「几乎不重复」的列,适合创建哪种索引?',
        'hint': None,
        'answer_sql': None,
        'answer': 'B',
        'options': [
            '位图索引(BITMAP INDEX)',
            'B-Tree 索引(默认索引)',
            '反向键索引(REVERSE KEY INDEX)',
            '函数索引(FUNCTION-BASED INDEX)',
        ],
        'explanation': (
            '正确答案 B:B-Tree(默认)索引适合高区分度列, '
            '等值和范围查询都高效,是 OLTP 的标配。\n'
            '其他选项错误:A 位图索引适合低区分度(如性别)且极少更新的列,'
            '适合数据仓库;C 反向键索引用于缓解 RAC 环境索引热块;'
            'D 函数索引针对 WHERE UPPER(name)=... 这类对列套函数的查询。\n'
            '补充:索引不是越多越好——每个索引都会拖慢 INSERT/UPDATE 并占用空间。'
        ),
    },
    {
        'id': 40, 'difficulty': '高级', 'topic': '数据类型', 'type': 'choice',
        'title': 'VARCHAR2 与 CHAR 的区别',
        'question': '关于 VARCHAR2 和 CHAR,下列说法正确的是?',
        'hint': None,
        'answer_sql': None,
        'answer': 'A',
        'options': [
            'VARCHAR2 变长存储,CHAR 定长存储(不足补空格)',
            'CHAR 变长存储,VARCHAR2 定长存储(不足补空格)',
            '两者完全相同,只是写法不同',
            'VARCHAR2 已被淘汰,新项目应使用 CHAR',
        ],
        'explanation': (
            "正确答案 A:VARCHAR2(10) 存 'ABC' 只占 3 字节; "
            "CHAR(10) 存 'ABC' 占 10 字节,不足部分补空格。\n"
            '其他选项错误:B 方向说反;C 两者存储机制不同;'
            'D 恰恰相反,Oracle 官方推荐用 VARCHAR2。\n'
            '补充:定长 CHAR 的补空格特性会导致比较时隐式带空格、'
            '浪费空间;VARCHAR2 最大 4000 字节(12c 扩展参数后可达 32767)。'
        ),
    },
    {
        'id': 41, 'difficulty': '高级', 'topic': '外连接语法', 'type': 'choice',
        'title': '旧式 (+) 外连接',
        'question': '旧式写法 WHERE e.deptno = d.deptno(+) 中,'
                    '(+) 在右表 d 一侧,表示哪种连接?',
        'hint': None,
        'answer_sql': None,
        'answer': 'C',
        'options': [
            '右外连接(RIGHT OUTER JOIN)',
            '内连接(INNER JOIN)',
            '左外连接(LEFT OUTER JOIN)',
            '全外连接(FULL OUTER JOIN)',
        ],
        'explanation': (
            '正确答案 C:(+) 标在哪个表上,哪个表就是「可补 NULL」的表——'
            '(+) 在右表 d 上,表示左表 e 全保留,即 LEFT OUTER JOIN。\n'
            '其他选项错误:A 方向反了((+) 在左表侧才是右外连接);'
            'B 内连接没有 (+);D (+) 不能两边同时写,全外连接要用 FULL JOIN。\n'
            '补充:Oracle 9i 起推荐标准 SQL 的 LEFT/RIGHT/FULL JOIN 写法, '
            '(+) 是老项目里才会见到的历史语法。'
        ),
    },
    {
        'id': 42, 'difficulty': '高级', 'topic': '执行计划', 'type': 'choice',
        'title': '查看执行计划',
        'question': '在 Oracle 中查看某条 SQL 的执行计划,标准命令是?',
        'hint': None,
        'answer_sql': None,
        'answer': 'D',
        'options': [
            'DESCRIBE PLAN FOR <SQL>',
            'SHOW PLAN FOR <SQL>',
            'ANALYZE TABLE ... FOR <SQL>',
            'EXPLAIN PLAN FOR <SQL>',
        ],
        'explanation': (
            '正确答案 D:EXPLAIN PLAN FOR <SQL> 把执行计划写入 PLAN_TABLE, '
            '再执行 SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY) 查看。\n'
            '其他选项错误:A DESCRIBE 是查看表结构;'
            'B 没有这个命令(SQL*Plus 里相关的是 SET AUTOTRACE ON, '
            '可以直接看真实执行计划与统计);'
            'C ANALYZE 是收集表/索引的统计信息,供优化器使用。\n'
            '补充:EXPLAIN PLAN 是「预估」计划,实际执行可能不同; '
            '真实运行计划要用 DBMS_XPLAN.DISPLAY_CURSOR 或 SQL Monitor 看。'
        ),
    },
]


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def by_difficulty(level):
    """按难度筛选题目:level ∈ 初级/中级/高级。"""
    return [q for q in QUESTION_BANK if q['difficulty'] == level]


def get_question(qid):
    """按题号取题,不存在返回 None。"""
    for q in QUESTION_BANK:
        if q['id'] == qid:
            return q
    return None


def all_ids():
    return [q['id'] for q in QUESTION_BANK]

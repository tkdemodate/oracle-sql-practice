# Oracle SQL 练习程序

> 离线、零依赖的 Oracle SQL 练习工具 —— 手写 SQL → 本地真实执行 → 表格展示 → 自动判分 + 解析。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-zero-success)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

无需安装 Oracle、无需联网、无需任何第三方包。打开即用，写完 SQL 立即看到执行结果,答错自动进错题本,练完出成绩单。

---

## ✨ 功能特性

| 模块 | 能力 |
|---|---|
| 🖊 **自由练习** | 任意 SQL 真实执行,ASCII 表格展示结果 + 行数 + 耗时 |
| 🎨 **语法高亮**(GUI) | 关键字 / 函数 / 字符串 / 数字 / 注释 五色区分 |
| 🗂 **表结构浮窗**(GUI) | 独立窗口,可一边写 SQL 一边看表结构,不切换页面 |
| 📚 **题库练习** | 42 道题(初级 12 / 中级 14 / 高级 16),支持顺序 / 随机 / 按难度 |
| 📝 **模拟考试** | 按范围随机组卷,交卷出成绩单(总分 / 正确率 / 评级 / 错题) |
| 🔁 **错题本** | 自动记录答错的题,可重做,答对自动移除 |
| 📊 **学习统计** | 总正确率 + 各难度掌握度进度条,JSON 持久化 |
| 🗂 **表预览** | 查看 EMP / DEPT / SALGRADE 结构 + 数据 |
| 🪟 **双版本** | GUI 窗体版(tkinter)+ 命令行版,功能等价 |

### Oracle 语法兼容

内置 19 个 Oracle 函数模拟 + 多条语法转换,几乎能跑教材 80% 的查询:

- **虚表与日期**:`DUAL`、`SYSDATE`、`SYSTIMESTAMP`
- **空值处理**:`NVL`、`NVL2`、`COALESCE`
- **条件**:`DECODE`、`CASE WHEN`
- **字符串**:`INSTR`、`SUBSTR`、`LENGTH`、`INITCAP`、`UPPER`、`LOWER`、`LPAD`、`RPAD`、`LTRIM`、`RTRIM`、`REPLACE`
- **数值**:`ROUND`、`TRUNC`、`MOD`、`ABS`、`SIGN`
- **日期**:`TO_CHAR`、`TO_DATE`、`MONTHS_BETWEEN`、`ADD_MONTHS`、`LAST_DAY`、`NEXT_DAY`、`EXTRACT`
- **分页与排序**:`ROWNUM`、`ROW_NUMBER() OVER`、`RANK() OVER`、`DENSE_RANK()`
- **集合**:`MINUS`、`UNION`、`INTERSECT`
- **分组**:`GROUP BY ... HAVING`、`SUM/AVG/COUNT/MAX/MIN OVER`

> 覆盖不到的(PL/SQL、`CONNECT BY`、`PIVOT`)以选择题形式在题库中给出。

---

## 🚀 快速开始

### 环境要求

- **Python 3.8+**(仅使用标准库,**无需 `pip install` 任何东西**)
- Windows / Linux / macOS 均可

### 三步上手

```bash
# 1. 克隆仓库
git clone https://github.com/<your-name>/oracle-sql-practice.git
cd oracle-sql-practice

# 2. 运行 GUI 版(推荐)
python oracle_gui.py
```

Windows 用户可以直接双击 `启动练习器.bat`(脚本会自动选用合适的 Python 解释器)。

### 命令行版

```bash
python oracle_practice.py
```

启动后按菜单提示操作(数字键选择):

```
═══════ Oracle SQL 练习器(本地真实执行 · 零依赖)═══════
1. 自由练习       2. 题库练习       3. 模拟考试
4. 错题本         5. 学习统计       6. 表预览
0. 退出
═══════════════════════════════════════════════════════
请选择[0-6]:
```

### 非交互命令

```bash
python oracle_practice.py --self-test   # 自检:跑题库 42 道标准答案,确认都能执行
python oracle_practice.py --demo        # 演示几段 SQL 的真实执行效果
```

---

## 📖 使用指南

### 自由练习

输入任意 SQL,以 `;` 结尾提交。常用命令:

| 输入 | 作用 |
|---|---|
| `SELECT ename, sal FROM emp WHERE sal > 2000;` | 查工资 > 2000 的员工 |
| `SELECT ename, NVL(comm, 0) FROM emp;` | 空奖金显示 0 |
| `SELECT * FROM (SELECT ename, sal FROM emp ORDER BY sal DESC) WHERE ROWNUM <= 3;` | 工资 Top-3 |
| `SELECT SYSDATE FROM DUAL;` | 当前时间 |
| `desc emp` | 查看 emp 表结构 |
| `tables` | 列出所有表 |
| `help` | 帮助 |
| `exit` | 返回菜单 |

### 题库练习示例

```
═══════ 第 5 / 42 题 · 中级 ═══════
题目:查询每位员工的姓名、工资、奖金,并把空奖金转换为 0。

请输入你的 SQL(Ctrl+C 跳过):
> SELECT ename, sal, NVL(comm,0) FROM emp;

✅ 回答正确!用时 18 秒。

— 标准答案 SQL:
  SELECT ename, sal, NVL(comm, 0) FROM emp;

— 解析:
  ① NVL(expr1, expr2): 当 expr1 为 NULL 时返回 expr2,否则返回 expr1。
  ② 奖金列多数员工为空,直接展示会很难看,常用 NVL 转为 0。
  ③ 也可以用 NVL2(comm, comm, 0) 或 COALESCE(comm, 0)。
```

### 模拟考试

按难度范围组卷,交卷后输出成绩单:

```
════════════════════════════════════════════
              模拟考试成绩单
════════════════════════════════════════════
考试范围:初级 + 中级(共 10 题)
答对:8 题    答错:2 题    总分:80 分
正确率:80.0%   评级:良好

错题清单:
  第 3 题 [初级] 查询部门平均工资...
  第 7 题 [中级] 行转列...
════════════════════════════════════════════
```

---

## 📂 项目结构

```
oracle-sql-practice/
├── oracle_gui.py          # GUI 窗体版入口(推荐)
├── oracle_practice.py     # 命令行版入口
├── db_engine.py           # 执行引擎:示例数据 + Oracle→SQLite 转换 + 函数模拟
├── question_bank.py       # 42 题题库(初级/中级/高级)
├── oracle_design.md       # 结构设计文档(规格书,适合发给其他 AI 实现)
├── oracle_prompt.md       # 让 AI 扮演「Oracle 私教」的提示词
├── 启动练习器.bat         # Windows 双击启动脚本
├── README.md              # 本文档
├── LICENSE                # MIT 协议
└── .gitignore
```

---

## 🗃 示例数据

内置 Oracle 经典演示表(与教材 / 面试题一致):

| 表 | 行数 | 列 |
|---|---|---|
| **EMP** | 14 | EMPNO / ENAME / JOB / MGR / HIREDATE / SAL / COMM / DEPTNO |
| **DEPT** | 4 | DEPTNO / DNAME / LOC |
| **SALGRADE** | 5 | GRADE / LOSAL / HISAL |
| **DUAL** | 1 | DUMMY |

经典员工:SMITH / ALLEN / WARD / JONES / MARTIN / BLAKE / CLARK / SCOTT / KING / TURNER / ADAMS / JAMES / FORD / MILLER。

---

## 🧪 自检与验收

```bash
python oracle_practice.py --self-test
```

会跑完题库 42 道题的标准答案 SQL,只要全部 ✅,说明引擎对 Oracle 函数的模拟覆盖到位。

---

## 🛠 技术原理

为什么不直接装 Oracle?真实 Oracle 安装包 2GB+,启动慢、对机器配置有要求。本项目用 **Python 标准库 sqlite3** 在内存里模拟 Oracle:

1. **建表阶段**:把 EMP / DEPT / SALGRADE / DUAL 真实数据灌进 SQLite
2. **语法转换**:用正则把 Oracle 专属写法转成 SQLite 等价语法
   - `NVL(a,b)` → `COALESCE(a,b)`
   - `SYSDATE` → `CURRENT_TIMESTAMP`
   - `ROWNUM` 加上 `LIMIT` 子句
   - `MINUS` → `EXCEPT`
   - `||` 字符串拼接 → SQLite 原生 `||`
   - `TO_CHAR(d, 'YYYY-MM-DD')` → `strftime('%Y-%m-%d', d)`
3. **函数模拟**:SQLite 没实现的,用 Python `register_function` 注册
   - `NVL / NVL2 / DECODE / TO_CHAR / TO_DATE / MONTHS_BETWEEN / ADD_MONTHS / LAST_DAY / INSTR / INITCAP / LPAD / RPAD` 等
4. **判分**:把用户 SQL 和标准答案 SQL 都执行,逐列比对结果集(忽略列名差异、列序差异)

> 局限:PL/SQL / `CONNECT BY` 递归 / `PIVOT` 行转列 / `(+)` 旧式外连接 无法本地模拟,会在题库中以选择题形式覆盖并提示改用 `LEFT JOIN`。

---

## 🤝 贡献

欢迎贡献!可以:

- 扩充题库(在 `question_bank.py` 加题,标注难度)
- 增加新的 Oracle 函数模拟(在 `db_engine.py` 的 `OracleEngine` 加)
- 优化 GUI(在 `oracle_gui.py` 加新功能或美化)
- 修 Bug / 改进文档

提 PR 时请保证:
- `python oracle_practice.py --self-test` 仍然通过
- 自行跑过主程序验证功能

---

## 📄 协议

[MIT License](./LICENSE) — 自由使用、修改、分发。

---

## 🙏 致谢

- 题库与示例数据参考 Oracle 经典教材 SCOTT 演示账户
- GUI 使用 Python 标准库 tkinter,无需任何第三方依赖

⭐ 如果觉得有用,欢迎点 Star!
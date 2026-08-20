# Oracle SQL Trainer

> 离线、零依赖的 **Oracle SQL 交互式训练器** — 手写 SQL → 本地真实执行 → 自动判分 + 解析。
> 内置 42 题题库、19 个 Oracle 函数模拟、SQL 语法高亮、表结构浮窗。
> 装个 Python 双击就练,免装 Oracle、免联网。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-zero-success)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![GUI](https://img.shields.io/badge/GUI-tkinter-orange)

---

## ✨ 核心特性

- 🖊 **自由练习** — 任意 SQL 真实执行,表格展示结果 + 行数 + 耗时
- 🎨 **语法高亮** — 关键字 / 函数 / 字符串 / 数字 / 注释 五色区分
- 🗂 **表结构浮窗** — 独立窗口,可一边写 SQL 一边看表结构,不切换页面
- 📚 **42 题题库** — 初级 12 / 中级 14 / 高级 16,顺序 / 随机 / 按难度
- 📝 **模拟考试** — 随机组卷,交卷出成绩单(总分 / 正确率 / 评级 / 错题)
- 🔁 **错题本** — 自动记录答错的题,可重做,答对自动移除
- 📊 **学习统计** — 总正确率 + 各难度掌握度进度条,JSON 持久化
- 🪟 **零依赖 GUI** — 仅用 Python 标准库 tkinter,无需 `pip install` 任何东西

### 兼容的 Oracle 语法

- **虚表与日期**:`DUAL`、`SYSDATE`
- **空值**:`NVL`、`NVL2`、`COALESCE`
- **条件**:`DECODE`、`CASE WHEN`
- **字符串**:`INSTR`、`SUBSTR`、`LENGTH`、`INITCAP`、`UPPER`、`LOWER`、`LPAD`、`RPAD`、`LTRIM`、`RTRIM`、`REPLACE`
- **数值**:`ROUND`、`TRUNC`、`MOD`、`ABS`、`SIGN`
- **日期**:`TO_CHAR`、`TO_DATE`、`MONTHS_BETWEEN`、`ADD_MONTHS`、`LAST_DAY`、`NEXT_DAY`
- **分页与排序**:`ROWNUM`、`ROW_NUMBER() OVER`、`RANK() OVER`、`DENSE_RANK()`
- **集合**:`MINUS`、`UNION`、`INTERSECT`
- **分组**:`GROUP BY ... HAVING`、`SUM/AVG/COUNT/MAX/MIN OVER`

> 覆盖不到的(PL/SQL、`CONNECT BY`、`PIVOT`)以选择题形式在题库中给出。

---

## 🚀 快速开始(30 秒)

### 1. 准备 Python

需要 **Python 3.8+** 且自带 **tkinter**(官方安装包默认带)。
Windows 用户如果是从 Microsoft Store 装的 Python,tcl/tk 也已包含。

### 2. 启动

**方式 A · Windows 用户**(推荐):

双击 **`启动练习器.bat`**,自动弹出练习窗口。

**方式 B · 任何系统**:

```bash
python oracle_gui.py
```

---

## 📖 功能一览

| 模块 | 能力 |
|---|---|
| ✍ **自由练习** | SQL 编辑器式输入框(语法高亮),Ctrl+Enter 执行,结果表格展示 |
| 📚 **题库练习** | 42 题分初级/中级/高级,支持顺序/随机/按难度;自动判分 + 答案解析 |
| 📝 **模拟考试** | 按范围随机组卷,交卷出成绩单(总分/正确率/评级/错题) |
| 🔁 **错题本** | 自动记录答错的题,可重做,答对自动移除 |
| 📊 **学习统计** | 总正确率 + 各难度掌握度进度条 |
| 🗂 **表结构浮窗** | 独立窗口,写 SQL 时边看表结构边写,来回切换零成本 |

### 自由练习 · 示例 SQL

```sql
SELECT ename, sal FROM emp WHERE sal > 2000;

SELECT ename, NVL(comm, 0) FROM emp;

SELECT * FROM (
  SELECT ename, sal FROM emp ORDER BY sal DESC
) WHERE ROWNUM <= 3;

SELECT ename, sal, DECODE(job,
  'MANAGER', sal * 1.2,
  'ANALYST', sal * 1.1,
  sal) AS new_sal
FROM emp;
```

### 题库练习 · 示例界面

```
═══════ 第 5 / 42 题 · 中级 ═══════
题目:查询每位员工的姓名、工资、奖金,并把空奖金转换为 0。

请输入你的 SQL(Ctrl+Enter 提交):
> SELECT ename, sal, NVL(comm,0) FROM emp;

✅ 回答正确!用时 18 秒。

— 标准答案 SQL:
  SELECT ename, sal, NVL(comm, 0) FROM emp;

— 解析:
  ① NVL(expr1, expr2): expr1 为 NULL 时返回 expr2。
  ② 奖金列多数员工为空,直接展示会很难看,常用 NVL 转为 0。
  ③ 也可以用 NVL2(comm, comm, 0) 或 COALESCE(comm, 0)。
```

---

## 📂 项目结构

```
oracle-sql-trainer/
├── oracle_gui.py          # GUI 入口(tkinter 零依赖)
├── db_engine.py           # 执行引擎:示例数据 + Oracle→SQLite 转换 + 函数模拟
├── question_bank.py       # 42 题题库
├── 启动练习器.bat         # Windows 双击启动脚本
├── README.md              # 本文档
├── LICENSE                # MIT 协议
└── .gitignore
```

---

## 🗃 示例数据(SCOTT 经典演示账户)

| 表 | 行数 | 列 |
|---|---|---|
| **EMP** | 14 | EMPNO / ENAME / JOB / MGR / HIREDATE / SAL / COMM / DEPTNO |
| **DEPT** | 4 | DEPTNO / DNAME / LOC |
| **SALGRADE** | 5 | GRADE / LOSAL / HISAL |
| **DUAL** | 1 | DUMMY |

经典员工:SMITH / ALLEN / WARD / JONES / MARTIN / BLAKE / CLARK / SCOTT / KING / TURNER / ADAMS / JAMES / FORD / MILLER。

---

## 🛠 技术原理

为什么不直接装 Oracle?真实 Oracle 安装包 2GB+,启动慢、对机器配置有要求。本项目用 **Python 标准库 sqlite3** 在内存里模拟 Oracle:

1. **建表阶段** — 把 EMP / DEPT / SALGRADE / DUAL 真实数据灌进 SQLite
2. **语法转换** — 用正则把 Oracle 专属写法转成 SQLite 等价语法
   - `NVL(a,b)` → `COALESCE(a,b)`
   - `SYSDATE` → `CURRENT_TIMESTAMP`
   - `ROWNUM` 加 `LIMIT` 子句
   - `MINUS` → `EXCEPT`
   - `TO_CHAR(d, 'YYYY-MM-DD')` → `strftime('%Y-%m-%d', d)`
3. **函数模拟** — SQLite 没实现的,用 Python `register_function` 注册
   - `NVL / NVL2 / DECODE / TO_CHAR / TO_DATE / MONTHS_BETWEEN / ADD_MONTHS / LAST_DAY / INSTR / INITCAP / LPAD / RPAD` 等
4. **判分** — 把用户 SQL 和标准答案 SQL 都执行,逐列比对结果集(忽略列名差异、列序差异)

> 局限:PL/SQL / `CONNECT BY` 递归 / `PIVOT` 行转列 / `(+)` 旧式外连接 无法本地模拟,会在题库中以选择题形式覆盖并提示改用 `LEFT JOIN`。

---

## 🤝 贡献

欢迎贡献!可以:

- 扩充题库(在 `question_bank.py` 加题,标注难度)
- 增加新的 Oracle 函数模拟(在 `db_engine.py` 加)
- 优化 GUI(在 `oracle_gui.py` 加新功能或美化)
- 修 Bug / 改进文档

提 PR 时请保证:程序能正常启动,自由练习和题库判分功能可用。

---

## 📄 协议

[MIT License](./LICENSE) — 自由使用、修改、分发。

---

## 🙏 致谢

- 题库与示例数据参考 Oracle 经典教材 SCOTT 演示账户
- GUI 使用 Python 标准库 tkinter,无需任何第三方依赖

⭐ 如果觉得有用,欢迎点 Star!
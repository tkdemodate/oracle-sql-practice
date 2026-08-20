# -*- coding: utf-8 -*-
"""数据库执行引擎:用 SQLite 内存库模拟 Oracle。

职责:
- 建立 EMP / DEPT / SALGRADE / DUAL 四张表并装载示例数据
- 注册 Oracle 特有函数(NVL / DECODE / TO_CHAR / ...)
- Oracle -> SQLite 语法转换(ROWNUM / SYSDATE / MINUS / ...)
- 执行 SQL 并返回结构化结果
- 结果集比对(判分核心)
"""

import re
import time
import math
import calendar
import sqlite3
import datetime as _dt


class OracleTranslateError(Exception):
    """Oracle 语法无法自动转换时抛出(如旧式外连接 (+))"""


# ---------------------------------------------------------------------------
# 日期辅助
# ---------------------------------------------------------------------------

def _parse_dt(v):
    """把 TEXT 日期/datetime 对象解析为 datetime,失败抛 ValueError。"""
    if isinstance(v, _dt.datetime):
        return v
    if isinstance(v, _dt.date):
        return _dt.datetime(v.year, v.month, v.day)
    if v is None:
        raise ValueError('日期为 NULL')
    s = str(v).strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d', '%Y%m%d'):
        try:
            return _dt.datetime.strptime(s, fmt)
        except ValueError:
            pass
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        return _dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    raise ValueError('无法识别的日期: %s' % s)


# ---------------------------------------------------------------------------
# Oracle 函数模拟(注册到 SQLite)
# ---------------------------------------------------------------------------

def _fn_nvl(x, y):
    return y if x is None else x


def _fn_nvl2(x, a, b):
    return a if x is not None else b


def _decode_key(v):
    """DECODE 的宽松比较键:数字按数值比,字符串忽略大小写。"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return ('n', float(v))
    s = str(v)
    try:
        return ('n', float(s))
    except ValueError:
        return ('s', s.upper())


def _fn_decode(*args):
    if len(args) < 3:
        return None
    expr = args[0]
    rest = list(args[1:])
    default = None
    if len(rest) % 2 == 1:
        default = rest[-1]
        rest = rest[:-1]
    key = _decode_key(expr)
    for i in range(0, len(rest), 2):
        # Oracle 的 DECODE 认为 NULL 与 NULL 相等
        if _decode_key(rest[i]) == key:
            return rest[i + 1]
    return default


def _fn_instr(s, sub, start=1, nth=1):
    if s is None or sub is None:
        return None
    s, sub = str(s), str(sub)
    nth = int(nth)
    if nth < 1 or not sub:
        return 0
    start = int(start)
    if start >= 0:
        idx = max(start - 1, 0)
        for _ in range(nth):
            idx = s.find(sub, idx)
            if idx < 0:
                return 0
            if _ < nth - 1:
                idx += 1
        return idx + 1
    else:
        idx = len(s) + start + 1
        for _ in range(nth):
            idx = s.rfind(sub, 0, idx + len(sub))
            if idx < 0:
                return 0
            if _ < nth - 1:
                idx -= 1
        return idx + 1


def _fn_substr(s, start, length=None):
    if s is None:
        return None
    s = str(s)
    start = int(start)
    if start == 0:
        start = 1
    if start > 0:
        begin = start - 1
    else:
        begin = max(len(s) + start, 0)
    if begin >= len(s):
        return ''
    if length is None or int(length) < 0:
        return s[begin:]
    return s[begin:begin + int(length)]


def _fn_initcap(s):
    if s is None:
        return None
    out = []
    prev_sep = True
    for ch in str(s):
        if ch.isalnum():
            out.append(ch.upper() if prev_sep else ch.lower())
            prev_sep = False
        else:
            out.append(ch)
            prev_sep = True
    return ''.join(out)


def _fn_lpad(s, w, pad=' '):
    if s is None:
        return None
    s = str(s)
    w = int(w)
    pad = str(pad) if pad is not None else ' '
    if not pad:
        pad = ' '
    if len(s) >= w:
        return s[:w]
    need = w - len(s)
    return (pad * need)[:need] + s


def _fn_rpad(s, w, pad=' '):
    if s is None:
        return None
    s = str(s)
    w = int(w)
    pad = str(pad) if pad is not None else ' '
    if not pad:
        pad = ' '
    if len(s) >= w:
        return s[:w]
    need = w - len(s)
    return s + (pad * need)[:need]


def _fn_mod(a, b):
    if a is None or b is None:
        return None
    a, b = float(a), float(b)
    if b == 0:
        return a  # Oracle: MOD(x,0)=x
    r = math.fmod(a, b)  # 符号跟随被除数,与 Oracle 一致
    return int(r) if r == int(r) else r


def _fn_trunc(n, d=0):
    if n is None:
        return None
    if isinstance(n, str):
        try:
            return _parse_dt(n).date().isoformat()  # TRUNC(日期)
        except ValueError:
            try:
                n = float(n)
            except ValueError:
                return None
    d = int(d)
    m = 10 ** d
    r = math.trunc(float(n) * m) / m
    return int(r) if r == int(r) else r


def _fn_months_between(d1, d2):
    a, b = _parse_dt(d1), _parse_dt(d2)
    months = (a.year - b.year) * 12 + (a.month - b.month)
    la = calendar.monthrange(a.year, a.month)[1]
    lb = calendar.monthrange(b.year, b.month)[1]
    if a.day == la and b.day == lb:
        return float(months)
    return months + (a.day - b.day) / 31.0


def _fn_add_months(d, n):
    a = _parse_dt(d)
    n = int(n)
    y = a.year + (a.month - 1 + n) // 12
    m = (a.month - 1 + n) % 12 + 1
    last = calendar.monthrange(y, m)[1]
    return _dt.date(y, m, min(a.day, last)).isoformat()


def _fn_last_day(d):
    a = _parse_dt(d)
    return _dt.date(a.year, a.month,
                    calendar.monthrange(a.year, a.month)[1]).isoformat()


def _fn_to_char(v, fmt=None):
    if v is None:
        return None
    if fmt is None:
        return str(v)
    try:
        d = _parse_dt(v)
        is_date = not isinstance(v, (int, float))
    except (ValueError, TypeError):
        is_date = False
        d = None
    if is_date and d is not None:
        out = str(fmt)
        out = out.replace('YYYY', '%04d' % d.year)
        out = out.replace('MM', '%02d' % d.month)
        out = out.replace('DD', '%02d' % d.day)
        out = out.replace('HH24', '%02d' % d.hour)
        out = out.replace('HH', '%02d' % (d.hour % 12 or 12))
        out = out.replace('MI', '%02d' % d.minute)
        out = out.replace('SS', '%02d' % d.second)
        return out
    return str(v)


def _fn_to_date(s, fmt=None):
    if s is None:
        return None
    if fmt is not None:
        # 支持 YYYY/MM/DD 等占位符格式:先按格式拆出年月日
        f = str(fmt)
        nums = re.findall(r'\d+', str(s))
        if 'YYYY' in f.upper() and len(nums) >= 3:
            return '%04d-%02d-%02d' % (int(nums[0]), int(nums[1]), int(nums[2]))
    d = _parse_dt(s)
    return d.date().isoformat()


def _fn_to_number(s):
    if s is None:
        return None
    f = float(s)
    return int(f) if f == int(f) else f


def _fn_greatest(*args):
    vals = [a for a in args if a is not None]
    if not vals:
        return None
    try:
        return max(vals, key=lambda v: float(v))
    except (TypeError, ValueError):
        return max(vals, key=lambda v: str(v))


def _fn_least(*args):
    vals = [a for a in args if a is not None]
    if not vals:
        return None
    try:
        return min(vals, key=lambda v: float(v))
    except (TypeError, ValueError):
        return min(vals, key=lambda v: str(v))


_DAY_NAMES = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY',
              'FRIDAY', 'SATURDAY', 'SUNDAY']  # 下标 = Python weekday()


def _fn_next_day(d, wd):
    a = _parse_dt(d)
    if isinstance(wd, (int, float)):
        n = int(wd) % 7  # Oracle: 1=周日 ... 7=周六
        py_target = (n - 2) % 7
    else:
        s = str(wd).strip().upper()
        if len(s) < 3:
            raise ValueError('next_day: 无法识别的星期: %s' % wd)
        for i, name in enumerate(_DAY_NAMES):
            if name.startswith(s):
                py_target = i
                break
        else:
            raise ValueError('next_day: 无法识别的星期: %s' % wd)
    delta = (py_target - a.weekday()) % 7
    if delta == 0:
        delta = 7  # 「下一个」不含当天
    return (a + _dt.timedelta(days=delta)).date().isoformat()


# ---------------------------------------------------------------------------
# 建表与示例数据(与设计文档第 4 章完全一致)
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE EMP (
    EMPNO    INTEGER PRIMARY KEY,
    ENAME    TEXT,
    JOB      TEXT,
    MGR      INTEGER,
    HIREDATE TEXT,
    SAL      REAL,
    COMM     REAL,
    DEPTNO   INTEGER
);
CREATE TABLE DEPT (
    DEPTNO INTEGER PRIMARY KEY,
    DNAME  TEXT,
    LOC    TEXT
);
CREATE TABLE SALGRADE (
    GRADE INTEGER,
    LOSAL INTEGER,
    HISAL INTEGER
);
CREATE TABLE DUAL (DUMMY TEXT);
"""

EMP_DATA = [
    (7369, '张伟',   '职员',   7902, '1980-12-17',  800, None,    20),
    (7499, '李娜',   '销售员', 7698, '1981-02-20', 1600, 300,     30),
    (7521, '王芳',   '销售员', 7698, '1981-02-22', 1250, 500,     30),
    (7566, '刘洋',   '经理',   7839, '1981-04-02', 2975, None,    20),
    (7654, '陈刚',   '销售员', 7698, '1981-09-28', 1250, 1400,    30),
    (7698, '杨丽',   '经理',   7839, '1981-05-01', 2850, None,    30),
    (7782, '赵明',   '经理',   7839, '1981-06-09', 2450, None,    10),
    (7788, '周强',   '分析师', 7566, '1987-04-19', 3000, None,    20),
    (7839, '吴伟',   '总裁',   None, '1981-11-17', 5000, None,    10),
    (7844, '郑华',   '销售员', 7698, '1981-09-08', 1500, 0,       30),
    (7876, '孙杰',   '职员',   7788, '1987-05-23', 1100, None,    20),
    (7900, '钱莉',   '职员',   7698, '1981-12-03',  950, None,    30),
    (7902, '马超',   '分析师', 7566, '1981-12-03', 3000, None,    20),
    (7934, '朱琳',   '职员',   7782, '1982-01-23', 1300, None,    10),
]

DEPT_DATA = [
    (10, '财务部', '北京'),
    (20, '研发部', '上海'),
    (30, '销售部', '广州'),
    (40, '运营部', '深圳'),
]

SALGRADE_DATA = [
    (1, 700, 1200),
    (2, 1201, 1400),
    (3, 1401, 2000),
    (4, 2001, 3000),
    (5, 3001, 9999),
]

TABLE_INFO = {
    'EMP': [
        ('EMPNO', 'NUMBER(4)', '员工号,主键'),
        ('ENAME', 'VARCHAR2(10)', '姓名'),
        ('JOB', 'VARCHAR2(9)', '岗位'),
        ('MGR', 'NUMBER(4)', '上级编号'),
        ('HIREDATE', 'DATE', '入职日期'),
        ('SAL', 'NUMBER(7,2)', '工资'),
        ('COMM', 'NUMBER(7,2)', '奖金(可空)'),
        ('DEPTNO', 'NUMBER(2)', '部门号'),
    ],
    'DEPT': [
        ('DEPTNO', 'NUMBER(2)', '部门号,主键'),
        ('DNAME', 'VARCHAR2(14)', '部门名'),
        ('LOC', 'VARCHAR2(13)', '所在地'),
    ],
    'SALGRADE': [
        ('GRADE', 'NUMBER', '工资等级'),
        ('LOSAL', 'NUMBER', '该等级最低工资'),
        ('HISAL', 'NUMBER', '该等级最高工资'),
    ],
    'DUAL': [
        ('DUMMY', 'VARCHAR2(1)', '虚表唯一列,恒为 X'),
    ],
}


# ---------------------------------------------------------------------------
# OracleEngine
# ---------------------------------------------------------------------------

class OracleEngine(object):
    """SQLite 内存库模拟 Oracle 的执行引擎。"""

    _ROWNUM_COND = re.compile(r'\bROWNUM\s*(?:<=|<|=)\s*\d+', re.I)

    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA case_sensitive_like = OFF')
        self._register_functions()
        self._create_schema()

    # ---- 初始化 ----------------------------------------------------------

    def _register_functions(self):
        funcs = [
            ('nvl', 2, _fn_nvl),
            ('nvl2', 3, _fn_nvl2),
            ('decode', -1, _fn_decode),
            ('instr', -1, _fn_instr),
            ('substr', -1, _fn_substr),
            ('initcap', 1, _fn_initcap),
            ('lpad', -1, _fn_lpad),
            ('rpad', -1, _fn_rpad),
            ('mod', 2, _fn_mod),
            ('trunc', -1, _fn_trunc),
            ('months_between', 2, _fn_months_between),
            ('add_months', 2, _fn_add_months),
            ('last_day', 1, _fn_last_day),
            ('to_char', -1, _fn_to_char),
            ('to_date', -1, _fn_to_date),
            ('to_number', 1, _fn_to_number),
            ('greatest', -1, _fn_greatest),
            ('least', -1, _fn_least),
            ('next_day', 2, _fn_next_day),
        ]
        for name, n, fn in funcs:
            try:
                self.conn.create_function(name, n, fn, deterministic=True)
            except TypeError:  # 旧版 Python 无 deterministic 参数
                self.conn.create_function(name, n, fn)

    def _create_schema(self):
        self.conn.executescript(DDL)
        self.conn.executemany('INSERT INTO EMP VALUES (?,?,?,?,?,?,?,?)', EMP_DATA)
        self.conn.executemany('INSERT INTO DEPT VALUES (?,?,?)', DEPT_DATA)
        self.conn.executemany('INSERT INTO SALGRADE VALUES (?,?,?)', SALGRADE_DATA)
        self.conn.execute("INSERT INTO DUAL VALUES ('X')")
        self.conn.commit()

    def reset(self):
        """清空并重新装载示例数据。"""
        for t in ('EMP', 'DEPT', 'SALGRADE', 'DUAL'):
            self.conn.execute('DELETE FROM ' + t)
        self.conn.executemany('INSERT INTO EMP VALUES (?,?,?,?,?,?,?,?)', EMP_DATA)
        self.conn.executemany('INSERT INTO DEPT VALUES (?,?,?)', DEPT_DATA)
        self.conn.executemany('INSERT INTO SALGRADE VALUES (?,?,?)', SALGRADE_DATA)
        self.conn.execute("INSERT INTO DUAL VALUES ('X')")
        self.conn.commit()

    # ---- 语法转换(设计文档 5.3) ------------------------------------------

    @staticmethod
    def translate(sql):
        s = sql.strip()
        while s.endswith(';'):
            s = s[:-1].rstrip()
        if not s:
            raise OracleTranslateError('空 SQL')
        # 规则 6:旧式外连接 (+)
        if re.search(r'\(\s*\+\s*\)', s):
            raise OracleTranslateError(
                '旧式外连接 (+) 无法自动转换, 请改用标准写法: '
                'LEFT JOIN ... ON ...')
        # 规则 3:TRUNC(SYSDATE) -> date(...)
        s = re.sub(r'\bTRUNC\s*\(\s*SYSDATE\s*\)',
                   "date('now','localtime')", s, flags=re.I)
        # 规则 2:SYSDATE -> datetime(...)
        s = re.sub(r'\bSYSDATE\b', "datetime('now','localtime')", s, flags=re.I)
        # 规则 5:MINUS -> EXCEPT
        s = re.sub(r'\bMINUS\b', 'EXCEPT', s, flags=re.I)
        # 规则 1:WHERE ROWNUM <= n
        m = OracleEngine._ROWNUM_COND.search(s)
        if m:
            n = re.search(r'\d+', m.group(0)).group(0)
            cond = re.escape(m.group(0))
            new = re.sub(r'(?:\bAND\b|\bOR\b)\s+' + cond, '', s, count=1, flags=re.I)
            if new == s:
                new = re.sub(cond + r'\s+(?:\bAND\b|\bOR\b)', '', s, count=1, flags=re.I)
            if new == s:
                new = s.replace(m.group(0), '')
            s = new
            # 清理残留连接词与孤立 WHERE
            s = re.sub(r'\bWHERE\s+(?:\bAND\b|\bOR\b)\s+', 'WHERE ', s, count=1, flags=re.I)
            s = re.sub(r'\bWHERE\s+(?=\bGROUP\b|\bORDER\b|\bHAVING\b|$)', '', s, count=1, flags=re.I)
            s = re.sub(r'\bWHERE\s*$', '', s, flags=re.I).rstrip()
            s = s + ' LIMIT ' + n
        # 规则 7:裸 ROWNUM
        s = re.sub(r'\bROWNUM\b', 'ROW_NUMBER() OVER ()', s, flags=re.I)
        return s

    # ---- 执行 --------------------------------------------------------------

    def execute(self, sql):
        t0 = time.perf_counter()
        res = {'ok': False, 'columns': [], 'rows': [], 'rowcount': 0,
               'elapsed': 0.0, 'translated': sql, 'changed': False, 'error': None}
        original = sql.strip()
        try:
            translated = self.translate(original)
        except OracleTranslateError as e:
            res['error'] = str(e)
            res['elapsed'] = (time.perf_counter() - t0) * 1000
            return res
        res['translated'] = translated
        res['changed'] = (translated.strip().rstrip(';')
                          != original.strip().rstrip(';'))
        try:
            cur = self.conn.execute(translated)
            if re.match(r'\s*(?:SELECT|WITH)\b', translated, re.I):
                rows = cur.fetchall()
                res['ok'] = True
                res['columns'] = ([d[0] for d in cur.description]
                                  if cur.description else [])
                res['rows'] = [tuple(r) for r in rows]
                res['rowcount'] = len(rows)
            else:
                self.conn.commit()
                res['ok'] = True
                res['rowcount'] = cur.rowcount
        except sqlite3.Error as e:
            res['error'] = str(e)
        res['elapsed'] = (time.perf_counter() - t0) * 1000
        return res

    # ---- 元数据 ------------------------------------------------------------

    @staticmethod
    def tables():
        return ['EMP', 'DEPT', 'SALGRADE']

    @staticmethod
    def describe(table):
        t = table.strip().upper()
        if t not in TABLE_INFO:
            return None
        return list(TABLE_INFO[t])

    def preview(self, table, n=5):
        t = table.strip().upper()
        if t not in TABLE_INFO:
            return None
        cur = self.conn.execute('SELECT * FROM %s LIMIT %d' % (t, int(n)))
        cols = [d[0] for d in cur.description]
        rows = [tuple(r) for r in cur.fetchall()]
        total = self.conn.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
        return {'columns': cols, 'rows': rows, 'total': total}

    # ---- 判分:结果集比对(设计文档 5.4) ------------------------------------

    @staticmethod
    def compare_results(std, usr):
        """只比结果不比写法:列集合一致 + 行集合一致(忽略行序)。"""
        if not usr['ok']:
            return False, '执行出错: %s' % usr['error']
        sc, uc = list(std['columns']), list(usr['columns'])
        if len(sc) != len(uc):
            return False, '结果列数不一致(标准 %d 列 vs 你的 %d 列: %s | %s)' % (
                len(sc), len(uc), sc, uc)
        scl = [str(c).lower() for c in sc]
        ucl = [str(c).lower() for c in uc]
        if (len(set(scl)) == len(scl) and sorted(scl) == sorted(ucl)
                and len(set(ucl)) == len(ucl)):
            idx = {c: i for i, c in enumerate(ucl)}
            order = [idx[c] for c in scl]
        else:
            order = list(range(len(scl)))  # 列名无法对应时按位置对齐

        def norm(v):
            if isinstance(v, float):
                return round(v, 6)
            return v

        def normrow(row):
            return tuple(norm(row[i]) for i in order)

        try:
            from collections import Counter
            a = Counter(normrow(r) for r in std['rows'])
            b = Counter(normrow(r) for r in usr['rows'])
        except TypeError:
            a = {normrow(r) for r in std['rows']}
            b = {normrow(r) for r in usr['rows']}
        if a == b:
            return True, '结果一致'
        if isinstance(a, dict):
            missing = sum((a - b).values()) if hasattr(a - b, 'values') else 0
            extra = sum((b - a).values()) if hasattr(b - a, 'values') else 0
            return False, ('结果不一致: 与标准答案相比缺少 %d 行、多出 %d 行'
                           '(忽略行顺序比较)' % (missing, extra))
        return False, '结果不一致(忽略行顺序比较)'

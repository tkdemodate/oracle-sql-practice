# -*- coding: utf-8 -*-
"""Oracle SQL 练习程序(命令行版)。

功能:自由练习 / 题库练习 / 模拟考试 / 错题本 / 学习统计 / 表结构预览。
运行:python oracle_practice.py        (交互模式)
      python oracle_practice.py --self-test   (自检模式)
"""

import sys
import os
import json
import random
import unicodedata

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
except Exception:
    pass

from db_engine import OracleEngine
from question_bank import QUESTION_BANK, by_difficulty, get_question

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MAX_SHOW_ROWS = 20


# ---------------------------------------------------------------------------
# 持久化(JSON)
# ---------------------------------------------------------------------------

def load_json(name, default):
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_progress():
    return load_json('progress.json', {
        'answered': 0, 'correct': 0,
        'by_difficulty': {},
    })


def load_wrongbook():
    return load_json('wrongbook.json', {'items': {}})


def record_answer(q, correct):
    """把一次作答写入统计与错题本。"""
    prog = load_progress()
    prog['answered'] += 1
    if correct:
        prog['correct'] += 1
    d = prog['by_difficulty'].setdefault(
        q['difficulty'], {'answered': 0, 'correct': 0})
    d['answered'] += 1
    if correct:
        d['correct'] += 1
    save_json('progress.json', prog)

    wb = load_wrongbook()
    key = str(q['id'])
    if correct:
        wb['items'].pop(key, None)
    else:
        wb['items'][key] = wb['items'].get(key, 0) + 1
    save_json('wrongbook.json', wb)


# ---------------------------------------------------------------------------
# 表格显示(中文按 2 列宽度对齐)
# ---------------------------------------------------------------------------

def disp_width(s):
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1
               for c in s)


def pad(s, width):
    return s + ' ' * max(0, width - disp_width(s))


def fmt_val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        s = ('%.2f' % v).rstrip('0').rstrip('.')
        return s if s else '0'
    return str(v)


def print_table(columns, rows):
    cols = [str(c) if c is not None else '' for c in columns]
    if not cols:
        if rows:
            cols = ['列%d' % (i + 1) for i in range(len(rows[0]))]
        else:
            print('  (无结果)')
            return
    data = [[fmt_val(v) for v in r] for r in rows]
    ncol = len(cols)
    widths = [disp_width(c) for c in cols]
    for r in data:
        for i in range(min(ncol, len(r))):
            widths[i] = max(widths[i], disp_width(r[i]))
    sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    print(sep)
    print('| ' + ' | '.join(pad(cols[i], widths[i])
                             for i in range(ncol)) + ' |')
    print(sep)
    for r in data[:MAX_SHOW_ROWS]:
        print('| ' + ' | '.join(pad(r[i], widths[i])
                                 for i in range(min(ncol, len(r)))) + ' |')
    print(sep)
    if len(data) > MAX_SHOW_ROWS:
        print('  ... 仅显示前 %d 行, 共 %d 行' % (MAX_SHOW_ROWS, len(data)))


def print_result_block(res):
    """每次执行成功后打印「执行效果展示」区块。"""
    print()
    title = '执行效果展示'
    total = 44
    left = (total - disp_width(title)) // 2
    right = total - disp_width(title) - left
    print('  ┌' + '─' * total + '┐')
    print('  │' + ' ' * left + title + ' ' * right + '│')
    print('  └' + '─' * total + '┘')
    if res.get('changed'):
        print('  转换后执行: %s' % res['translated'])
    if res['ok']:
        if res['columns'] or res['rows']:
            print_table(res['columns'], res['rows'])
            print('  → 返回 %d 行 | 耗时 %.2f ms'
                  % (res['rowcount'], res['elapsed']))
        else:
            print('  影响 %d 行 | 耗时 %.2f ms'
                  % (res['rowcount'], res['elapsed']))
    else:
        print('  ❌ 执行出错: %s' % res['error'])


# ---------------------------------------------------------------------------
# 输入辅助
# ---------------------------------------------------------------------------

def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def read_sql():
    """自由练习的多行 SQL 输入:分号结尾或空行提交;exit/quit 返回。"""
    buf = []
    while True:
        try:
            line = input('SQL> ' if not buf else '  ... ')
        except EOFError:
            return None
        t = line.strip()
        if not buf and t.lower() in ('exit', 'quit', 'q'):
            return None
        if not t:
            if buf:
                return '\n'.join(buf)
            continue
        if t.endswith(';'):
            buf.append(t[:-1].rstrip())
            return '\n'.join(buf)
        buf.append(t)


def read_answer_sql():
    """答题时的单行 SQL 输入。"""
    try:
        line = input('你的SQL> ').strip()
    except EOFError:
        return None
    while line.endswith(';'):
        line = line[:-1].rstrip()
    return line or None


def norm_choice(ans):
    """把 A-D / 1-4 统一为字母;非法输入返回 None。"""
    if ans is None:
        return None
    a = ans.strip().upper()
    mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
    a = mapping.get(a, a)
    return a if a in ('A', 'B', 'C', 'D') else None


# ---------------------------------------------------------------------------
# 功能 1:自由练习
# ---------------------------------------------------------------------------

FREE_HELP = """  可用命令:
    tables            列出所有表
    desc 表名         查看表结构
    show 表名 [n]     预览表前 n 行(默认 5)
    reset             恢复示例数据
    help              显示本帮助
    exit              返回主菜单
  SQL 输入:可多行输入,以分号 ; 结尾或空行提交。
  支持 Oracle 写法:ROWNUM / SYSDATE / NVL / DECODE / MINUS / TO_CHAR 等。"""


def free_practice():
    engine = OracleEngine()
    print('\n── 自由练习(输入 exit 返回菜单,help 查看帮助)──')
    print(FREE_HELP)
    while True:
        sql = read_sql()
        if sql is None:
            return
        low = sql.strip().lower()
        try:
            if low in ('help', '?'):
                print(FREE_HELP)
                continue
            if low == 'tables':
                print('  表: %s (另有虚表 DUAL)' % ', '.join(engine.tables()))
                continue
            if low == 'reset':
                engine.reset()
                print('  ✅ 示例数据已恢复')
                continue
            if low.startswith('desc '):
                t = OracleEngine.describe(low[5:])
                if t is None:
                    print('  ❌ 表不存在, 可用表: %s' % engine.tables())
                else:
                    print_table(['列名', '类型', '说明'], t)
                continue
            if low.startswith(('show ', 'preview ')):
                parts = sql.strip().split()
                table = parts[1] if len(parts) > 1 else ''
                n = 5
                if len(parts) > 2:
                    try:
                        n = int(parts[2])
                    except ValueError:
                        n = 5
                pv = engine.preview(table, n)
                if pv is None:
                    print('  ❌ 表不存在, 可用表: %s' % engine.tables())
                else:
                    print_table(pv['columns'], pv['rows'])
                    print('  → 共 %d 行' % pv['total'])
                continue
        except Exception as e:
            print('  ❌ 命令处理出错: %s' % e)
            continue
        res = engine.execute(sql)
        print_result_block(res)


# ---------------------------------------------------------------------------
# 判分流程(题库练习 / 考试 / 错题本共用)
# ---------------------------------------------------------------------------

DIFF_ICON = {'初级': '🌱', '中级': '🔥', '高级': '💎'}


def show_question(q, show_hint=True):
    print('\n' + '─' * 56)
    print('%s [%s] 第 %d 题 · %s' % (
        DIFF_ICON.get(q['difficulty'], '·'), q['difficulty'],
        q['id'], q['topic']))
    print('题目: %s' % q['question'])
    if show_hint and q.get('hint'):
        print('提示: %s' % q['hint'])
    if q['type'] == 'choice':
        for letter, opt in zip('ABCD', q['options']):
            print('  %s. %s' % (letter, opt))


def ask_question(q, record=True, reveal=True):
    """出题并作答。返回 True(对)/ False(错)/ None(跳过)。"""
    show_question(q)
    if q['type'] == 'sql':
        ans = read_answer_sql()
        if ans is None or ans.lower() in ('exit', 'quit', 'q'):
            print('  ⏭ 已跳过本题(不计入统计)')
            return None
        user_res = OracleEngine().execute(ans)
        print_result_block(user_res)
        std_res = OracleEngine().execute(q['answer_sql'])
        ok, msg = OracleEngine.compare_results(std_res, user_res)
    else:
        ans = norm_choice(ask('你的答案(A-D 或 1-4): '))
        if ans is None:
            print('  ⏭ 已跳过本题(不计入统计)')
            return None
        ok = (ans == q['answer'])
        msg = '结果一致' if ok else '答案错误'

    if ok:
        print('\n  ✅ 回答正确! %s' % msg)
    else:
        print('\n  ❌ 回答错误: %s' % msg)
        if reveal:
            if q['type'] == 'sql':
                print('\n  标准答案 SQL:')
                print('  ' + q['answer_sql'])
                print('\n  标准答案执行效果:')
                std_res = OracleEngine().execute(q['answer_sql'])
                print_result_block(std_res)
            else:
                print('  正确答案: %s. %s' % (
                    q['answer'], q['options'][ord(q['answer']) - 65]))
            print('\n  【解析】')
            for line in q['explanation'].split('\n'):
                print('  ' + line)
    if record:
        record_answer(q, ok)
    return ok


# ---------------------------------------------------------------------------
# 功能 2:题库练习
# ---------------------------------------------------------------------------

def bank_practice():
    print('\n── 题库练习 ──')
    print(' 1. 顺序做全部题目')
    print(' 2. 随机抽题')
    print(' 3. 按难度练习(初级/中级/高级)')
    print(' 0. 返回')
    choice = ask('请选择: ')
    if choice == '1':
        pool = list(QUESTION_BANK)
    elif choice == '2':
        n = ask('抽几题(回车默认 5): ') or '5'
        try:
            n = max(1, min(int(n), len(QUESTION_BANK)))
        except ValueError:
            n = 5
        pool = random.sample(QUESTION_BANK, n)
    elif choice == '3':
        level = ask('难度(初级/中级/高级): ')
        if level not in ('初级', '中级', '高级'):
            print('  ❌ 难度输入无效')
            return
        pool = by_difficulty(level)
        print('  %s共 %d 题, 答题时输入 exit 跳过本题、quit 结束练习'
              % (level, len(pool)))
    elif choice in ('0', '', None):
        return
    else:
        print('  ❌ 无效选择')
        return

    done = right = 0
    for q in pool:
        r = ask_question(q)
        if r is None:
            if ask('输入 quit 结束练习, 回车继续: ') == 'quit':
                break
            continue
        done += 1
        if r:
            right += 1
    print('\n── 小结: 完成 %d 题 | 答对 %d 题 | 正确率 %s ──'
          % (done, right, ('%.0f%%' % (100.0 * right / done)) if done else '-'))


# ---------------------------------------------------------------------------
# 功能 3:模拟考试
# ---------------------------------------------------------------------------

def take_exam():
    print('\n── 模拟考试 ──')
    print('  出题范围: 1.全题库  2.初级  3.中级  4.高级')
    scope = ask('请选择(默认 1): ') or '1'
    pools = {'1': QUESTION_BANK, '2': by_difficulty('初级'),
             '3': by_difficulty('中级'), '4': by_difficulty('高级')}
    pool = pools.get(scope)
    if not pool:
        print('  ❌ 无效选择')
        return
    n = ask('题目数量(回车默认 10): ') or '10'
    try:
        n = max(1, min(int(n), len(pool)))
    except ValueError:
        n = 10
    questions = random.sample(pool, n)
    print('  已组卷 %d 题, 逐题作答; 输入 exit 提前交卷。\n'
          '  (考试中不即时判分, 交卷后统一出成绩单)' % n)

    answers = {}  # id -> (ok, answered)
    for q in questions:
        show_question(q, show_hint=False)
        if q['type'] == 'sql':
            ans = read_answer_sql()
            if ans is None or ans.lower() in ('exit', 'quit', 'q'):
                print('  ⏭ 提前交卷')
                break
            user_res = OracleEngine().execute(ans)
            print_result_block(user_res)
            std_res = OracleEngine().execute(q['answer_sql'])
            ok, _ = OracleEngine.compare_results(std_res, user_res)
            answers[q['id']] = (ok, True)
        else:
            ans = norm_choice(ask('你的答案(A-D 或 1-4): '))
            if ans is None:
                print('  ⏭ 提前交卷')
                break
            answers[q['id']] = (ans == q['answer'], True)

    total = len(questions)
    correct = sum(1 for ok, _ in answers.values() if ok)
    wrong_ids = [qid for qid in questions if not answers.get(qid['id'], (False,))[0]]
    score = 100.0 * correct / total if total else 0
    grade = ('优秀' if score >= 90 else '良好' if score >= 75
             else '及格' if score >= 60 else '需加强')

    print('\n' + '═' * 44)
    print('                 模拟考试成绩单')
    print('═' * 44)
    print('  总分: %.0f / 100        评级: %s' % (score, grade))
    print('  答对 %d 题 | 答错(含未答)%d 题 | 未答 %d 题'
          % (correct, total - correct, total - len(answers)))
    print('  答对率: %.0f%%' % (100.0 * correct / total if total else 0))
    if wrong_ids:
        print('  错题编号: %s' % ', '.join(str(q['id']) for q in wrong_ids))
    print('═' * 44)

    # 一次性计入统计与错题本
    for q in questions:
        ok, answered = answers.get(q['id'], (False, False))
        record_answer(q, ok)

    if wrong_ids:
        show = ask('\n查看错题解析?(y/n): ')
        if show and show.lower() in ('y', 'yes', '是'):
            for q in wrong_ids:
                print('\n【第 %d 题】%s' % (q['id'], q['question']))
                if q['type'] == 'sql':
                    print('  标准答案 SQL:\n  ' + q['answer_sql'])
                    print_result_block(OracleEngine().execute(q['answer_sql']))
                else:
                    print('  正确答案: %s. %s' % (
                        q['answer'], q['options'][ord(q['answer']) - 65]))
                print('  【解析】')
                for line in q['explanation'].split('\n'):
                    print('  ' + line)


# ---------------------------------------------------------------------------
# 功能 4:错题本
# ---------------------------------------------------------------------------

def wrong_book():
    wb = load_wrongbook()
    items = wb.get('items', {})
    if not items:
        print('\n── 错题本: 暂无错题, 再接再厉! ──')
        return
    print('\n── 错题本(共 %d 题)──' % len(items))
    for key in sorted(items, key=int):
        q = get_question(int(key))
        if q:
            print('  第 %2d 题 [%s] %s —— 已错 %d 次'
                  % (q['id'], q['difficulty'], q['title'], items[key]))
    yes = ask('\n重做全部错题?(y/n): ')
    if yes and yes.lower() in ('y', 'yes', '是'):
        for key in sorted(items, key=int):
            q = get_question(int(key))
            if q:
                ask_question(q)


# ---------------------------------------------------------------------------
# 功能 5:学习统计
# ---------------------------------------------------------------------------

def statistics():
    prog = load_progress()
    answered = prog.get('answered', 0)
    correct = prog.get('correct', 0)
    print('\n── 学习统计 ──')
    print('  总答题: %d 次 | 总答对: %d 次 | 总正确率: %s'
          % (answered, correct,
             ('%.0f%%' % (100.0 * correct / answered)) if answered else '-'))
    for level in ('初级', '中级', '高级'):
        d = prog.get('by_difficulty', {}).get(level, {})
        a, c = d.get('answered', 0), d.get('correct', 0)
        rate = (100.0 * c / a) if a else 0
        k = int(round(rate / 10.0))
        bar = '█' * k + '░' * (10 - k)
        print('  %s 正确率 %5.1f%%  %s  (答对 %d / 作答 %d 次)'
              % (level, rate, bar, c, a))
        print('       题库共 %d 题' % len(by_difficulty(level)))
    print('  数据文件: %s' % os.path.join(DATA_DIR, 'progress.json'))
    print('           %s' % os.path.join(DATA_DIR, 'wrongbook.json'))


# ---------------------------------------------------------------------------
# 功能 6:表结构预览
# ---------------------------------------------------------------------------

def show_tables(engine):
    print('\n── 表结构与数据预览 ──')
    for t in engine.tables() + ['DUAL']:
        info = OracleEngine.describe(t)
        pv = engine.preview(t, 5)
        print('\n◆ 表 %s(共 %d 行)' % (t, pv['total']))
        print_table(['列名', '类型', '说明'], info)
        print('  前 5 行数据:')
        print_table(pv['columns'], pv['rows'])


# ---------------------------------------------------------------------------
# 自检模式(--self-test)
# ---------------------------------------------------------------------------

def self_test():
    print('════════ 自检模式 ════════')
    engine = OracleEngine()
    fails = []

    # 1) 题库所有 sql 题的答案可执行且非空
    sql_qs = [q for q in QUESTION_BANK if q['type'] == 'sql']
    for q in sql_qs:
        r = engine.execute(q['answer_sql'])
        if not r['ok'] or r['rowcount'] == 0:
            fails.append('题 %d 答案执行失败: %s' % (q['id'], r['error']))
        else:
            print('  ✅ 题 %2d 答案 OK, %d 行' % (q['id'], r['rowcount']))
    # choice 题结构检查
    for q in QUESTION_BANK:
        if q['type'] == 'choice':
            if not (q['answer'] in 'ABCD' and len(q['options']) == 4):
                fails.append('题 %d 选项结构异常' % q['id'])

    # 2) 验收标准 3:工资>2000 共 6 行
    r = engine.execute('SELECT ename, sal FROM emp WHERE sal > 2000')
    if not (r['ok'] and r['rowcount'] == 6):
        fails.append('验收3失败: %s' % r['error'])

    # 3) 验收标准 4:NVL 空奖金显示 0
    r = engine.execute('SELECT ename, NVL(comm,0) FROM emp')
    row = [x for x in r['rows'] if x[0] == 'SMITH']
    if not (r['ok'] and row and row[0][1] == 0):
        fails.append('验收4失败: NVL 未生效')

    # 4) 验收标准 5:ROWNUM Top-3 = KING/SCOTT/FORD
    r = engine.execute('SELECT ename, sal FROM '
                       '(SELECT ename, sal FROM emp ORDER BY sal DESC) '
                       'WHERE ROWNUM <= 3')
    names = set(x[0] for x in r['rows'])
    if not (r['ok'] and r['rowcount'] == 3
            and names == {'KING', 'SCOTT', 'FORD'}):
        fails.append('验收5失败: Top-3 结果异常 %s' % names)

    # 5) 验收标准 6:SYSDATE
    r = engine.execute('SELECT SYSDATE FROM DUAL')
    if not (r['ok'] and r['rowcount'] == 1 and r['rows'][0][0]):
        fails.append('验收6失败: SYSDATE 异常')

    # 6) 验收标准 10:中文表格渲染不报错(DECODE 经理/职员)
    r = engine.execute("SELECT ename, DECODE(job,'MANAGER','经理',"
                       "'CLERK','职员','其他') FROM emp")
    if r['ok']:
        print_table(r['columns'], r['rows'])
    else:
        fails.append('验收10失败: %s' % r['error'])

    # 7) 判分健壮性:等价写法应判对
    std = engine.execute('SELECT ename, sal FROM emp WHERE sal > 2000')
    alt = engine.execute('SELECT ename, sal FROM emp WHERE 2000 < sal')
    ok, msg = OracleEngine.compare_results(std, alt)
    if not ok:
        fails.append('判分检查失败: 等价写法被判错(%s)' % msg)

    print('\n──── 自检结果 ────')
    if fails:
        for f in fails:
            print('  ❌ ' + f)
        print('共 %d 项失败' % len(fails))
        sys.exit(1)
    print('  ✅ 全部通过(%d 道 sql 答案 + 7 项验收检查)'
          % len(sql_qs))


# ---------------------------------------------------------------------------
# 演示模式(--demo)
# ---------------------------------------------------------------------------

DEMO_SQLS = [
    'SELECT ename, job, sal FROM emp WHERE sal > 2000',
    'SELECT ename, NVL(comm, 0) FROM emp',
    'SELECT ename, sal FROM (SELECT ename, sal FROM emp '
    'ORDER BY sal DESC) WHERE ROWNUM <= 3',
    'SELECT SYSDATE FROM DUAL',
    "SELECT ename, DECODE(job, 'MANAGER', '经理', 'CLERK', '职员', "
    "'其他') FROM emp",
    'SELECT deptno, AVG(sal) FROM emp GROUP BY deptno',
]


def demo():
    print('════════ 演示模式:几段典型 SQL 的执行效果 ════════')
    engine = OracleEngine()
    for sql in DEMO_SQLS:
        print('\n>>> %s' % sql)
        print_result_block(engine.execute(sql))


# ---------------------------------------------------------------------------
# 主菜单
# ---------------------------------------------------------------------------

MENU = """
═════════════════════════════════════════
   Oracle SQL 练习程序
   (内置 EMP/DEPT/SALGRADE 示例数据, 本地真实执行)
═════════════════════════════════════════
 1. 自由练习    —— 任意输入 SQL, 看真实执行效果
 2. 题库练习    —— 42 道题自动判分 + 解析
 3. 模拟考试    —— 随机组卷, 交卷出成绩单
 4. 错题本      —— 重做做错的题
 5. 学习统计    —— 正确率与进度(自动保存)
 6. 查看表结构与数据
 0. 退出
"""


def main():
    if '--self-test' in sys.argv:
        self_test()
        return
    if '--demo' in sys.argv:
        demo()
        return
    engine = OracleEngine()
    print(MENU)
    while True:
        c = ask('请选择: ')
        if c is None or c == '0':
            print('\n再见, 继续加油!')
            return
        try:
            if c == '1':
                free_practice()
            elif c == '2':
                bank_practice()
            elif c == '3':
                take_exam()
            elif c == '4':
                wrong_book()
            elif c == '5':
                statistics()
            elif c == '6':
                show_tables(engine)
            elif c == '':
                continue
            else:
                print('  ❌ 无效选择, 请输入 0-6')
        except KeyboardInterrupt:
            print('\n(已中断当前操作)')
        print(MENU)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已退出。')

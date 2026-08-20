# -*- coding: utf-8 -*-
"""Oracle SQL 练习器(窗体版)

运行: python oracle_gui.py
依赖: 仅 Python 标准库(tkinter), 复用 db_engine / question_bank,
统计数据与命令行版共用 data/ 目录。
"""

import re
import random
import tkinter as tk
from tkinter import ttk, messagebox

from db_engine import OracleEngine
from question_bank import QUESTION_BANK, by_difficulty, get_question
from oracle_practice import (record_answer, load_progress, load_wrongbook,
                             fmt_val, DATA_DIR)

TEXT_FONT = ('Microsoft YaHei UI', 10)
META_FONT = ('Microsoft YaHei UI', 10, 'bold')
TITLE_FONT = ('Microsoft YaHei UI', 11, 'bold')
SQL_FONT = ('Consolas', 11)
SQL_FONT_BOLD = ('Consolas', 11, 'bold')
DIFF_TEXT = {'初级': '🌱 初级', '中级': '🔥 中级', '高级': '💎 高级'}

# ---------------------------------------------------------------------------
# SQL 语法高亮
# ---------------------------------------------------------------------------

SQL_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE',
    'BETWEEN', 'ORDER', 'GROUP', 'BY', 'HAVING', 'ASC', 'DESC', 'DISTINCT',
    'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'FULL', 'CROSS', 'ON',
    'UNION', 'ALL', 'INTERSECT', 'MINUS', 'EXCEPT', 'EXISTS', 'CASE', 'WHEN',
    'THEN', 'ELSE', 'END', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
    'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'WITH', 'OVER', 'PARTITION',
    'LIMIT', 'OFFSET', 'FETCH', 'ROWS', 'ONLY', 'START', 'CONNECT', 'PRIOR',
    'SYSDATE', 'ROWNUM', 'LEVEL', 'DUAL', 'ANY', 'SOME',
}

SQL_FUNCTIONS = {
    'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'NVL', 'NVL2', 'DECODE', 'COALESCE',
    'NULLIF', 'SUBSTR', 'INSTR', 'UPPER', 'LOWER', 'INITCAP', 'LENGTH',
    'REPLACE', 'TRIM', 'LPAD', 'RPAD', 'ROUND', 'TRUNC', 'MOD', 'ABS',
    'CEIL', 'FLOOR', 'TO_CHAR', 'TO_DATE', 'TO_NUMBER', 'GREATEST', 'LEAST',
    'ADD_MONTHS', 'MONTHS_BETWEEN', 'LAST_DAY', 'NEXT_DAY', 'RANK',
    'DENSE_RANK', 'ROW_NUMBER', 'LAG', 'LEAD', 'FIRST_VALUE', 'LISTAGG',
}


def sql_token_spans(text):
    """扫描 SQL 文本,返回 [(类别, 起点, 终点)]。"""
    spans = []
    covered = []
    for m in re.finditer(r'--[^\n]*', text):
        spans.append(('cmt', m.start(), m.end()))
        covered.append((m.start(), m.end()))
    for m in re.finditer(r"'[^']*'", text):
        spans.append(('str', m.start(), m.end()))
        covered.append((m.start(), m.end()))
    for m in re.finditer(r'[A-Za-z_][A-Za-z0-9_]*', text):
        if any(s <= m.start() < e for s, e in covered):
            continue
        word = m.group(0).upper()
        if word in SQL_KEYWORDS:
            spans.append(('kw', m.start(), m.end()))
        elif word in SQL_FUNCTIONS:
            spans.append(('fn', m.start(), m.end()))
    for m in re.finditer(r'\b\d+(?:\.\d+)?\b', text):
        if any(s <= m.start() < e for s, e in covered):
            continue
        spans.append(('num', m.start(), m.end()))
    return spans


def configure_sql_tags(widget):
    """给任意 Text 组件配置 SQL 高亮 tag。"""
    widget.tag_configure('kw', font=SQL_FONT_BOLD, foreground='#0000C0')
    widget.tag_configure('fn', foreground='#7A3E9D')
    widget.tag_configure('str', foreground='#A31515')
    widget.tag_configure('num', foreground='#098658')
    widget.tag_configure('cmt', foreground='#6A9955')


def apply_sql_tags(widget, start, end):
    """对 Text 中 [start, end) 区间做 SQL 高亮。"""
    text = widget.get(start, end)
    if not text:
        return
    for kind, s, e in sql_token_spans(text):
        widget.tag_add(kind, '%s+%dc' % (start, s), '%s+%dc' % (start, e))


class SqlText(tk.Text):
    """带实时 SQL 语法高亮的编辑框。"""

    def __init__(self, master, **kw):
        kw.setdefault('font', SQL_FONT)
        kw.setdefault('relief', 'groove')
        kw.setdefault('wrap', 'none')
        super().__init__(master, **kw)
        configure_sql_tags(self)
        self.bind('<KeyRelease>', lambda e: self.highlight())
        self.bind('<<Paste>>', lambda e: self.after_idle(self.highlight))

    def highlight(self):
        for tag in ('kw', 'fn', 'str', 'num', 'cmt'):
            self.tag_remove(tag, '1.0', 'end')
        apply_sql_tags(self, '1.0', 'end-1c')


# ---------------------------------------------------------------------------
# 通用组件
# ---------------------------------------------------------------------------

def make_tree(master, height=10):
    """带滚动条的结果表格。"""
    box = ttk.Frame(master)
    tree = ttk.Treeview(box, show='headings', height=height)
    vsb = ttk.Scrollbar(box, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    box.rowconfigure(0, weight=1)
    box.columnconfigure(0, weight=1)
    return box, tree


def render_result(tree, res, max_rows=300):
    """把 execute() 的结果展示到 Treeview, 返回信息文本。"""
    tree.delete(*tree.get_children())
    if not res['ok']:
        return '❌ 执行出错: %s' % res['error']
    if not res['columns']:
        return '✅ 执行成功 | 影响 %d 行 | 耗时 %.2f ms' % (
            res['rowcount'], res['elapsed'])
    cols = [str(c) if c is not None else '' for c in res['columns']]
    tree['columns'] = cols
    tree['show'] = 'headings'
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=max(80, min(280, 60 + 9 * len(c))),
                    anchor='w')
    for r in res['rows'][:max_rows]:
        tree.insert('', 'end', values=[fmt_val(v) for v in r])
    info = '→ 返回 %d 行 | 耗时 %.2f ms' % (res['rowcount'], res['elapsed'])
    if res.get('changed'):
        info += '   [已自动转换 Oracle 语法]'
    if len(res['rows']) > max_rows:
        info += '(仅显示前 %d 行)' % max_rows
    return info


def render_rows(tree, columns, rows):
    """把普通二维数据展示到 Treeview。"""
    tree.delete(*tree.get_children())
    tree['columns'] = columns
    tree['show'] = 'headings'
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, width=max(90, min(280, 60 + 9 * len(c))), anchor='w')
    for r in rows:
        tree.insert('', 'end', values=[fmt_val(v) if not isinstance(v, str)
                                       else v for v in r])


def make_feedback(master, height=9):
    t = tk.Text(master, height=height, font=TEXT_FONT, wrap='word',
                state='disabled', background='#fafafa', relief='groove')
    t.tag_configure('ok', foreground='#0a7d32')
    t.tag_configure('err', foreground='#c62828')
    t.tag_configure('dim', foreground='#666666')
    t.tag_configure('sql', font=SQL_FONT)
    t.tag_configure('title', font=META_FONT)
    configure_sql_tags(t)
    return t


def set_feedback(widget, parts):
    """parts: [(文本, 标签), ...];标签为 'sql' 时做语法高亮。"""
    widget.configure(state='normal')
    widget.delete('1.0', 'end')
    for text, tag in parts:
        if tag == 'sql':
            start = widget.index('end-1c')
            widget.insert('end', text, 'sql')
            apply_sql_tags(widget, start, widget.index('end-1c'))
        else:
            widget.insert('end', text, tag or ())
        widget.insert('end', '\n')
    widget.configure(state='disabled')


class QuestionCard(ttk.LabelFrame):
    """题目卡片:显示题干 + 作答区(SQL 输入框或选项单选)。"""

    def __init__(self, master, on_submit=None, submit_text='提交答案',
                 show_hint=True):
        super().__init__(master, text=' 题目 ', padding=8)
        self.q = None
        self.on_submit = on_submit
        self.show_hint = show_hint
        self.var_choice = tk.StringVar(value='')

        self.lbl_meta = ttk.Label(self, text='', font=META_FONT,
                                  foreground='#1565c0')
        self.lbl_question = ttk.Label(self, text='', font=TITLE_FONT,
                                      wraplength=600, justify='left')
        self.lbl_hint = ttk.Label(self, text='', font=TEXT_FONT,
                                  foreground='#8a6d3b', wraplength=600,
                                  justify='left')
        self.answer_box = tk.Frame(self)
        self.btn_submit = ttk.Button(self, text=submit_text,
                                     command=self._submit)
        self.lbl_meta.grid(row=0, column=0, sticky='w')
        self.lbl_question.grid(row=1, column=0, sticky='w', pady=(4, 2))
        self.lbl_hint.grid(row=2, column=0, sticky='w', pady=(0, 4))
        self.answer_box.grid(row=3, column=0, sticky='we', pady=(0, 6))
        self.btn_submit.grid(row=4, column=0, sticky='w')
        self.columnconfigure(0, weight=1)

    # ---- 题目装载 ----------------------------------------------------------

    def set_question(self, q, restore=None):
        self.q = q
        self.var_choice.set('')
        for w in self.answer_box.winfo_children():
            w.destroy()
        self.lbl_meta.configure(text='%s | 第 %d 题 | %s' % (
            DIFF_TEXT.get(q['difficulty'], q['difficulty']),
            q['id'], q['topic']))
        self.lbl_question.configure(text=q['question'])
        self.lbl_hint.configure(
            text=('提示: %s' % q['hint']) if (self.show_hint and q['hint'])
            else '')
        if q['type'] == 'sql':
            self.sql_text = SqlText(self.answer_box, height=4)
            self.sql_text.grid(row=0, column=0, sticky='we')
            self.sql_text.bind('<Control-Return>', self._submit)
            if restore:
                self.sql_text.insert('1.0', restore)
                self.sql_text.highlight()
        else:
            self.sql_text = None
            for letter, opt in zip('ABCD', q['options']):
                ttk.Radiobutton(self.answer_box, text='%s. %s' % (letter, opt),
                                value=letter, variable=self.var_choice)\
                    .grid(sticky='w', pady=1)
            if restore:
                self.var_choice.set(restore)
        self.answer_box.columnconfigure(0, weight=1)

    def get_answer(self):
        """返回 ('sql', 文本) / ('choice', 字母) / None(未作答)。"""
        if self.q is None:
            return None
        if self.q['type'] == 'sql':
            t = self.sql_text.get('1.0', 'end').strip()
            while t.endswith(';'):
                t = t[:-1].rstrip()
            return ('sql', t) if t else None
        v = self.var_choice.get()
        return ('choice', v) if v else None

    def _submit(self, *_):
        if self.on_submit:
            self.on_submit(self.q, self.get_answer())


def judge_sql(q, user_sql):
    """执行并判分一道 sql 题。返回 (ok, msg, user_res, std_res)。"""
    user_res = OracleEngine().execute(user_sql)
    std_res = OracleEngine().execute(q['answer_sql'])
    ok, msg = OracleEngine.compare_results(std_res, user_res)
    return ok, msg, user_res, std_res


# ---------------------------------------------------------------------------
# 功能 1:自由练习
# ---------------------------------------------------------------------------

class FreeFrame(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.engine = OracleEngine()

        ttk.Label(self, text='自由练习:输入任意 SQL(支持 ROWNUM / SYSDATE / '
                             'NVL / DECODE / MINUS 等 Oracle 写法)',
                  font=TEXT_FONT).grid(row=0, column=0, columnspan=4,
                                       sticky='w')
        self.sql = SqlText(self, height=5)
        self.sql.grid(row=1, column=0, columnspan=4, sticky='we', pady=6)
        self.sql.bind('<Control-Return>', self.run_sql)
        self.sql.bind('<F5>', self.run_sql)

        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, columnspan=4, sticky='w')
        ttk.Button(btns, text='执行 (Ctrl+Enter)', command=self.run_sql)\
            .pack(side='left')
        ttk.Button(btns, text='清空', command=lambda: self.sql.delete(
            '1.0', 'end')).pack(side='left', padx=4)
        ttk.Button(btns, text='恢复示例数据',
                   command=self.reset_data).pack(side='left', padx=4)

        tools = ttk.Frame(self)
        tools.grid(row=3, column=0, columnspan=4, sticky='w', pady=(6, 2))
        ttk.Label(tools, text='表:').pack(side='left')
        self.cb_table = ttk.Combobox(
            tools, state='readonly', width=12,
            values=self.engine.tables() + ['DUAL'])
        self.cb_table.current(0)
        self.cb_table.pack(side='left', padx=4)
        ttk.Button(tools, text='查看数据', command=self.show_data)\
            .pack(side='left', padx=2)
        ttk.Button(tools, text='结构浮窗(可边写边看)',
                   command=self.open_schema_win).pack(side='left', padx=2)
        ttk.Label(tools, text='  (示例:SELECT ename, sal FROM emp '
                              'WHERE sal > 2000)',
                  foreground='#888888').pack(side='left')

        self.info = ttk.Label(self, text='', font=TEXT_FONT,
                              foreground='#444444')
        self.info.grid(row=4, column=0, columnspan=4, sticky='w')
        box, self.tree = make_tree(self, height=13)
        box.grid(row=5, column=0, columnspan=4, sticky='nsew', pady=(2, 0))
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

    def run_sql(self, *_):
        sql = self.sql.get('1.0', 'end').strip()
        if not sql:
            return
        res = self.engine.execute(sql)
        self.info.configure(text=render_result(self.tree, res))

    def reset_data(self):
        self.engine.reset()
        self.info.configure(text='✅ 示例数据已恢复')
        self.tree.delete(*self.tree.get_children())

    def show_data(self):
        pv = self.engine.preview(self.cb_table.get(), 50)
        if pv is None:
            self.info.configure(text='❌ 表不存在')
            return
        render_rows(self.tree, pv['columns'], pv['rows'])
        self.info.configure(text='表 %s | 共 %d 行(最多显示 50 行)'
                            % (self.cb_table.get(), pv['total']))

    def open_schema_win(self):
        self.app.open_table_window(self.cb_table.get())


# ---------------------------------------------------------------------------
# 功能 2:题库练习
# ---------------------------------------------------------------------------

class BankFrame(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.pool = list(QUESTION_BANK)
        self.index = 0

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky='we')
        ttk.Label(top, text='难度:').pack(side='left')
        self.cb_level = ttk.Combobox(
            top, state='readonly', width=8,
            values=['全部', '初级', '中级', '高级'])
        self.cb_level.current(0)
        self.cb_level.bind('<<ComboboxSelected>>', self.change_level)
        self.cb_level.pack(side='left', padx=4)
        ttk.Button(top, text='随机一题', command=self.random_one)\
            .pack(side='left', padx=4)
        ttk.Button(top, text='上一题', command=lambda: self.move(-1))\
            .pack(side='left', padx=(16, 2))
        ttk.Button(top, text='下一题', command=lambda: self.move(1))\
            .pack(side='left', padx=2)
        self.lbl_pos = ttk.Label(top, text='', font=TEXT_FONT,
                                 foreground='#666666')
        self.lbl_pos.pack(side='right')

        self.card = QuestionCard(self, on_submit=self.submit)
        self.card.grid(row=1, column=0, sticky='we', pady=6)

        self.info = ttk.Label(self, text='执行你的 SQL 查看真实效果:',
                              font=TEXT_FONT)
        self.info.grid(row=2, column=0, sticky='w')
        box, self.tree = make_tree(self, height=6)
        box.grid(row=3, column=0, sticky='we', pady=2)

        self.feedback = make_feedback(self, height=8)
        self.feedback.grid(row=4, column=0, sticky='we', pady=(4, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        self.load_index(0)

    # ---- 导航 ---------------------------------------------------------------

    def change_level(self, *_):
        level = self.cb_level.get()
        self.pool = (list(QUESTION_BANK) if level == '全部'
                     else by_difficulty(level))
        self.load_index(0)

    def random_one(self):
        self.load_index(random.randrange(len(self.pool)))

    def move(self, delta):
        self.load_index(self.index + delta)

    def load_index(self, i):
        if not self.pool:
            return
        self.index = i % len(self.pool)
        self.lbl_pos.configure(text='第 %d / %d 题' % (self.index + 1,
                                                      len(self.pool)))
        self.card.set_question(self.pool[self.index])
        set_feedback(self.feedback, [('作答后这里显示判分与解析。', 'dim')])

    # ---- 判分 ---------------------------------------------------------------

    def submit(self, q, answer):
        if answer is None:
            set_feedback(self.feedback, [('⚠ 还没有输入答案。', 'err')])
            return
        if q['type'] == 'sql':
            ok, msg, user_res, std_res = judge_sql(q, answer[1])
            self.info.configure(text='你的 SQL 执行结果:')
            render_result(self.tree, user_res)
            parts = [('✅ 回答正确!' if ok else '❌ 回答错误: %s' % msg,
                      'ok' if ok else 'err')]
            if not ok:
                parts += [('— 标准答案 SQL:', 'dim'),
                          (q['answer_sql'], 'sql')]
            parts += [('— 解析:', 'dim'), (q['explanation'], None)]
        else:
            ok = answer[1] == q['answer']
            parts = [('✅ 回答正确!' if ok else '❌ 回答错误。',
                      'ok' if ok else 'err')]
            if not ok:
                parts.append(('正确答案: %s. %s' % (
                    q['answer'], q['options'][ord(q['answer']) - 65]), 'err'))
            parts += [('— 解析:', 'dim'), (q['explanation'], None)]
        set_feedback(self.feedback, parts)
        record_answer(q, ok)
        self.app.refresh_status()


# ---------------------------------------------------------------------------
# 功能 3:模拟考试
# ---------------------------------------------------------------------------

class ExamFrame(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app
        self.paper = []
        self.answers = {}   # qid -> ('sql', 文本) / ('choice', 字母)
        self.index = 0

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky='we')
        ttk.Label(top, text='范围:').pack(side='left')
        self.cb_scope = ttk.Combobox(
            top, state='readonly', width=8,
            values=['全题库', '初级', '中级', '高级'])
        self.cb_scope.current(0)
        self.cb_scope.pack(side='left', padx=(2, 8))
        ttk.Label(top, text='题数:').pack(side='left')
        self.sp_num = ttk.Spinbox(top, from_=1, to=42, width=5)
        self.sp_num.set(10)
        self.sp_num.pack(side='left', padx=(2, 8))
        ttk.Button(top, text='开始考试', command=self.start)\
            .pack(side='left', padx=4)
        ttk.Button(top, text='交卷', command=self.submit_paper)\
            .pack(side='left', padx=4)
        self.lbl_pos = ttk.Label(top, text='(未开考)', font=TEXT_FONT,
                                 foreground='#666666')
        self.lbl_pos.pack(side='right')

        self.card = QuestionCard(self, on_submit=self.save_answer,
                                 submit_text='记录答案(不判分)',
                                 show_hint=False)
        self.card.grid(row=1, column=0, sticky='we', pady=6)
        nav = ttk.Frame(self)
        nav.grid(row=2, column=0, sticky='w')
        ttk.Button(nav, text='上一题', command=lambda: self.move(-1))\
            .pack(side='left', padx=2)
        ttk.Button(nav, text='下一题', command=lambda: self.move(1))\
            .pack(side='left', padx=2)

        self.feedback = make_feedback(self, height=12)
        self.feedback.grid(row=3, column=0, sticky='we', pady=(6, 0))
        self.columnconfigure(0, weight=1)
        set_feedback(self.feedback, [
            ('模拟考试:选择范围和题数后点击「开始考试」。', None),
            ('考试中不判分;可回退修改答案;点击「交卷」出成绩单并计入统计。',
             'dim')])
        self.card.set_question(QUESTION_BANK[0])  # 占位展示

    # ---- 流程 ---------------------------------------------------------------

    def start(self):
        pools = {'全题库': QUESTION_BANK, '初级': by_difficulty('初级'),
                 '中级': by_difficulty('中级'), '高级': by_difficulty('高级')}
        pool = pools[self.cb_scope.get()]
        try:
            n = max(1, min(int(self.sp_num.get()), len(pool)))
        except ValueError:
            n = 10
        self.paper = random.sample(pool, n)
        self.answers = {}
        self.index = 0
        self.load_index(0)
        set_feedback(self.feedback, [
            ('已组卷 %d 题(考试中不判分,交卷后统一评分)。' % n, None),
            ('输入 exit 无法跳题,直接点「交卷」可提前结束。', 'dim')])

    def load_index(self, i):
        if not self.paper:
            return
        self.index = max(0, min(i, len(self.paper) - 1))
        q = self.paper[self.index]
        prev = self.answers.get(q['id'])
        self.card.set_question(q, restore=prev[1] if prev else None)
        self.lbl_pos.configure(text='第 %d / %d 题 | 已记录 %d 题'
                               % (self.index + 1, len(self.paper),
                                  len(self.answers)))

    def move(self, delta):
        self.load_index(self.index + delta)

    def save_answer(self, q, answer):
        if answer is None:
            set_feedback(self.feedback, [('⚠ 还没有输入答案。', 'err')])
            return
        self.answers[q['id']] = answer
        self.lbl_pos.configure(text='第 %d / %d 题 | 已记录 %d 题'
                               % (self.index + 1, len(self.paper),
                                  len(self.answers)))
        if self.index < len(self.paper) - 1:
            self.load_index(self.index + 1)
        else:
            set_feedback(self.feedback, [
                ('已到最后一题。确认无误后点击「交卷」。', 'dim')])

    def submit_paper(self):
        if not self.paper:
            set_feedback(self.feedback, [('⚠ 请先「开始考试」。', 'err')])
            return
        if len(self.answers) < len(self.paper):
            if not messagebox.askyesno(
                    '交卷确认', '还有 %d 题未作答, 未答题按错误计分, '
                    '确定交卷吗?' % (len(self.paper) - len(self.answers))):
                return
        total = len(self.paper)
        correct = 0
        wrong = []
        for q in self.paper:
            ans = self.answers.get(q['id'])
            ok = False
            if ans:
                if ans[0] == 'sql':
                    ok, _, _, _ = judge_sql(q, ans[1])
                else:
                    ok = ans[1] == q['answer']
            if ok:
                correct += 1
            else:
                wrong.append(q)
            record_answer(q, ok)   # 一次性计入统计与错题本
        score = 100.0 * correct / total if total else 0
        grade = ('优秀' if score >= 90 else '良好' if score >= 75
                 else '及格' if score >= 60 else '需加强')
        messagebox.showinfo(
            '模拟考试成绩单',
            '总分: %.0f / 100\n评级: %s\n答对 %d 题 | 答错(含未答)%d 题\n'
            '正确率: %.0f%%' % (score, grade, correct, total - correct,
                                100.0 * correct / total))
        parts = [('成绩单: %.0f 分 | %s | 答对 %d / %d 题'
                  % (score, grade, correct, total),
                  'title' if score >= 60 else 'err')]
        for q in wrong:
            parts.append(('— 第 %d 题(%s)' % (q['id'], q['topic']), 'dim'))
            if q['type'] == 'sql':
                parts.append(('标准答案: ' + q['answer_sql'], 'sql'))
            else:
                parts.append(('正确答案: %s. %s' % (
                    q['answer'], q['options'][ord(q['answer']) - 65]), None))
            parts.append((q['explanation'], None))
            parts.append(('', None))
        set_feedback(self.feedback, parts)
        self.app.refresh_status()
        self.paper = []
        self.lbl_pos.configure(text='(考试结束)')


# ---------------------------------------------------------------------------
# 功能 4:错题本
# ---------------------------------------------------------------------------

class WrongFrame(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master, padding=10)
        self.app = app

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky='we')
        ttk.Button(top, text='刷新', command=self.refresh)\
            .pack(side='left', padx=2)
        ttk.Button(top, text='重做选中题', command=self.redo)\
            .pack(side='left', padx=2)
        ttk.Label(top, text='选中一行后点击「重做选中题」, 答对自动移出错题本。',
                  foreground='#888888').pack(side='left', padx=8)

        box, self.tree = make_tree(self, height=6)
        box.grid(row=1, column=0, sticky='we', pady=4)
        self.tree.bind('<Double-1>', lambda e: self.redo())

        self.card = QuestionCard(self, on_submit=self.submit)
        self.card.grid(row=2, column=0, sticky='we', pady=6)
        self.feedback = make_feedback(self, height=7)
        self.feedback.grid(row=3, column=0, sticky='we', pady=(4, 0))
        self.columnconfigure(0, weight=1)
        self.refresh()

    def refresh(self):
        items = load_wrongbook().get('items', {})
        rows = []
        for key in sorted(items, key=int):
            q = get_question(int(key))
            if q:
                rows.append((q['id'], DIFF_TEXT.get(q['difficulty'],
                                                    q['difficulty']),
                             q['title'], q['topic'], items[key]))
        render_rows(self.tree, ['题号', '难度', '标题', '主题', '已错次数'],
                    rows)

    def redo(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('提示', '请先选中一道错题。')
            return
        qid = int(self.tree.item(sel[0], 'values')[0])
        q = get_question(qid)
        if q:
            self.card.set_question(q)
            set_feedback(self.feedback, [('重做中……答对即移出错题本。', 'dim')])

    def submit(self, q, answer):
        if answer is None:
            set_feedback(self.feedback, [('⚠ 还没有输入答案。', 'err')])
            return
        if q['type'] == 'sql':
            ok, msg, _, _ = judge_sql(q, answer[1])
            head = ('✅ 回答正确! 已移出错题本。' if ok
                    else '❌ 回答错误: %s' % msg)
        else:
            ok = answer[1] == q['answer']
            head = ('✅ 回答正确! 已移出错题本。' if ok else '❌ 回答错误。')
        parts = [(head, 'ok' if ok else 'err')]
        if not ok:
            if q['type'] == 'sql':
                parts += [('标准答案: ' + q['answer_sql'], 'sql')]
            else:
                parts.append(('正确答案: %s. %s' % (
                    q['answer'], q['options'][ord(q['answer']) - 65]), None))
            parts.append((q['explanation'], None))
        set_feedback(self.feedback, parts)
        record_answer(q, ok)
        self.refresh()
        self.app.refresh_status()


# ---------------------------------------------------------------------------
# 功能 5:学习统计
# ---------------------------------------------------------------------------

class StatsFrame(ttk.Frame):

    def __init__(self, master, app):
        super().__init__(master, padding=14)
        self.app = app
        self.lbl_total = ttk.Label(self, text='', font=TITLE_FONT)
        self.lbl_total.grid(row=0, column=0, sticky='w', pady=(0, 10))
        self.bars = {}
        for i, level in enumerate(('初级', '中级', '高级'), start=1):
            ttk.Label(self, text=DIFF_TEXT[level], font=META_FONT)\
                .grid(row=i, column=0, sticky='w', pady=6)
            var = tk.DoubleVar(value=0)
            ttk.Progressbar(self, variable=var, maximum=100, length=260)\
                .grid(row=i, column=1, padx=10)
            lbl = ttk.Label(self, text='', font=TEXT_FONT)
            lbl.grid(row=i, column=2, sticky='w')
            self.bars[level] = (var, lbl)
        ttk.Label(self, text='', font=TEXT_FONT, foreground='#888888')\
            .grid(row=5, column=0, columnspan=3, sticky='w', pady=(16, 0))
        self.lbl_path = ttk.Label(self, text='数据文件: %s'
                                  % DATA_DIR, foreground='#888888')
        self.lbl_path.grid(row=6, column=0, columnspan=3, sticky='w')

    def refresh(self):
        prog = load_progress()
        a, c = prog.get('answered', 0), prog.get('correct', 0)
        self.lbl_total.configure(
            text='总答题 %d 次 | 总答对 %d 次 | 总正确率 %s' % (
                a, c, ('%.0f%%' % (100.0 * c / a)) if a else '-'))
        for level in ('初级', '中级', '高级'):
            d = prog.get('by_difficulty', {}).get(level, {})
            da, dc = d.get('answered', 0), d.get('correct', 0)
            rate = (100.0 * dc / da) if da else 0
            var, lbl = self.bars[level]
            var.set(rate)
            lbl.configure(text='%5.1f%%(答对 %d / 作答 %d 次, 题库共 %d 题)'
                          % (rate, dc, da, len(by_difficulty(level))))


# ---------------------------------------------------------------------------
# 表结构预览(独立浮窗,写 SQL 时可边看边写)
# ---------------------------------------------------------------------------

class TableWindow(tk.Toplevel):

    def __init__(self, master, engine, initial='EMP'):
        super().__init__(master)
        self.title('表结构与数据(浮窗)')
        self.geometry('600x560')
        self.engine = engine

        top = ttk.Frame(self, padding=6)
        top.pack(fill='x')
        ttk.Label(top, text='选择表:').pack(side='left')
        self.cb = ttk.Combobox(top, state='readonly', width=14,
                               values=self.engine.tables() + ['DUAL'])
        self.cb.set(initial)
        self.cb.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        self.cb.pack(side='left', padx=4)
        ttk.Button(top, text='刷新', command=self.refresh)\
            .pack(side='left', padx=4)
        self.lbl_info = ttk.Label(top, text='', foreground='#444444')
        self.lbl_info.pack(side='left', padx=10)

        ttk.Label(self, text='表结构:', font=META_FONT)\
            .pack(anchor='w', padx=10, pady=(6, 2))
        box1, self.tree_desc = make_tree(self, height=5)
        box1.pack(fill='x', padx=10)
        ttk.Label(self, text='数据预览(前 20 行):', font=META_FONT)\
            .pack(anchor='w', padx=10, pady=(8, 2))
        box2, self.tree_data = make_tree(self, height=12)
        box2.pack(fill='both', expand=True, padx=10, pady=(0, 8))
        self.refresh()

    def select(self, table):
        self.cb.set(table)
        self.refresh()

    def refresh(self):
        t = self.cb.get()
        info = OracleEngine.describe(t)
        pv = self.engine.preview(t, 20)
        if info is None or pv is None:
            return
        render_rows(self.tree_desc, ['列名', '类型', '说明'], info)
        render_rows(self.tree_data, pv['columns'], pv['rows'])
        self.lbl_info.configure(text='表 %s | 共 %d 行' % (t, pv['total']))


# ---------------------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------------------

MENU_ITEMS = [
    ('自由练习', FreeFrame, '✍'),
    ('题库练习', BankFrame, '📚'),
    ('模拟考试', ExamFrame, '📝'),
    ('错题本', WrongFrame, '🔁'),
    ('学习统计', StatsFrame, '📊'),
]


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Oracle SQL 练习器(本地真实执行 · 零依赖)')
        self.geometry('860x660')
        self.minsize(780, 560)
        self.engine = OracleEngine()
        self.table_win = None

        side = ttk.Frame(self, padding=8)
        side.grid(row=0, column=0, sticky='ns')
        ttk.Label(side, text='Oracle SQL\n练 习 器', font=(
            'Microsoft YaHei UI', 13, 'bold'), justify='center',
            foreground='#1565c0').grid(row=0, column=0, pady=(0, 14))
        self.nav_buttons = []
        for i, (name, cls, icon) in enumerate(MENU_ITEMS, start=1):
            b = ttk.Button(side, text='%s  %s' % (icon, name), width=12,
                           command=lambda c=cls: self.show(c))
            b.grid(row=i, column=0, pady=3, sticky='we')
            self.nav_buttons.append((name, b))
        ttk.Separator(side, orient='horizontal')\
            .grid(row=len(MENU_ITEMS) + 1, column=0, sticky='we', pady=8)
        ttk.Button(side, text='🗂  表结构(浮窗)', width=12,
                   command=self.open_table_window)\
            .grid(row=len(MENU_ITEMS) + 2, column=0, pady=3, sticky='we')

        self.content = ttk.Frame(self, padding=4)
        self.content.grid(row=0, column=1, sticky='nsew')
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.frames = {}
        for name, cls, _ in MENU_ITEMS:
            f = cls(self.content, self)
            f.grid(row=0, column=0, sticky='nsew')
            self.frames[cls] = f
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.status = ttk.Label(self, text='', anchor='w',
                                relief='sunken', padding=(8, 4))
        self.status.grid(row=1, column=0, columnspan=2, sticky='we')
        self.show(FreeFrame)
        self.refresh_status()

    def open_table_window(self, table='EMP'):
        """打开或聚焦表结构浮窗。"""
        if self.table_win is not None and self.table_win.winfo_exists():
            self.table_win.select(table)
            self.table_win.lift()
            self.table_win.focus_force()
            return
        self.table_win = TableWindow(self, self.engine, table)

    def show(self, cls):
        for c, f in self.frames.items():
            f.grid_remove()
        frame = self.frames[cls]
        frame.grid()
        if hasattr(frame, 'refresh'):
            try:
                frame.refresh()
            except TypeError:
                pass

    def refresh_status(self):
        prog = load_progress()
        a, c = prog.get('answered', 0), prog.get('correct', 0)
        wb = load_wrongbook().get('items', {})
        self.status.configure(
            text='  学习统计: 已答 %d 次 | 答对 %d 次 | 正确率 %s | '
                 '错题本 %d 题' % (
                     a, c, ('%.0f%%' % (100.0 * c / a)) if a else '-',
                     len(wb)))


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()

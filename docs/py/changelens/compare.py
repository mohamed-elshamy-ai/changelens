"""Compare two documents and classify each change by how much it likely matters.

Rule based. No AI model. The severity is a guess from patterns (numbers, money,
dates, obligation words, negations, keywords like "terminate"), not legal advice.
"""
import difflib
import re
from dataclasses import dataclass, asdict
from enum import IntEnum

from .extract import extract
from . import rules


class Severity(IntEnum):
    FORMAT = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Change:
    severity: Severity
    kind: str          # added, removed, modified, format
    title: str
    location: str = ""
    old: str = ""
    new: str = ""

    def to_dict(self):
        d = asdict(self)
        d["severity"] = self.severity.name
        return d


_WS = re.compile(r"\s+")


def _norm(s):
    return _WS.sub(" ", s).strip()


def _loose(s):
    """Text with case, punctuation and spacing removed, used to spot format-only changes."""
    return re.sub(r"[\W_]+", "", s.lower())


def _tokens(s):
    return re.findall(r"[\w$€£%.,]+|[^\w\s]", s, re.UNICODE)


def _first_words(s, n=8):
    w = s.split()
    return " ".join(w[:n]) + ("..." if len(w) > n else "")


def _judge_modified(old, new, loc):
    if _loose(old) == _loose(new):
        return Change(Severity.FORMAT, "format", "Formatting, case or punctuation only", loc, old, new)
    on, nn = rules.numbers(old), rules.numbers(new)
    ot, nt = _tokens(old), _tokens(new)
    sm = difflib.SequenceMatcher(None, ot, nt, autojunk=False)
    removed, added = [], []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op in ("replace", "delete"):
            removed.append(" ".join(ot[a1:a2]))
        if op in ("replace", "insert"):
            added.append(" ".join(nt[b1:b2]))
    rem, add = " / ".join(removed), " / ".join(added)
    reasons = []
    sev = Severity.LOW
    if on != nn:
        reasons.append("number changed")
        sev = Severity.HIGH
    # obligation strength
    def strength(text):
        words = re.findall(r"\w+", text.lower())
        s = [rules.STRENGTH[w] for w in words if w in rules.STRENGTH]
        return s
    so, sn = strength(old), strength(new)
    if so != sn and (so or sn):
        reasons.append("obligation wording changed")
        sev = max(sev, Severity.HIGH)
    neg = lambda t: sum(1 for w in re.findall(r"\w+", t.lower()) if w in rules.NEGATIONS)
    if neg(old) != neg(new):
        reasons.append("negation changed")
        sev = max(sev, Severity.HIGH)
    kw_changed = set(rules.has_important_word(rem)) | set(rules.has_important_word(add))
    if kw_changed:
        reasons.append("touches: " + ", ".join(sorted(kw_changed)[:4]))
        sev = max(sev, Severity.MEDIUM if sev < Severity.MEDIUM else sev)
    ratio = sm.ratio()
    if sev == Severity.LOW and ratio < 0.7:
        reasons.append("mostly rewritten")
        sev = Severity.MEDIUM
    title = "; ".join(reasons) if reasons else "Wording changed"
    return Change(sev, "modified", title[0].upper() + title[1:], loc, old, new)


def _judge_block(kind, text, loc):
    words = rules.has_important_word(text)
    nums = rules.numbers(text)
    if words and nums:
        sev = Severity.HIGH
    elif words:
        sev = Severity.HIGH if kind == "added" else Severity.MEDIUM
    elif nums:
        sev = Severity.MEDIUM
    else:
        sev = Severity.LOW
    why = f" (touches: {', '.join(words[:3])})" if words else ""
    verb = "New text added" if kind == "added" else "Text removed"
    ch = Change(sev, kind, verb + why, loc)
    if kind == "added":
        ch.new = text
    else:
        ch.old = text
    return ch


def _label(text):
    """The clause label at the start of a block, such as '6. Ownership.' (used to pair rewritten clauses)."""
    m = re.match(r"^(\d+(?:\.\d+)*\.?\s+[A-Za-z\u0600-\u06FF]+)", text)
    return m.group(1).lower() if m else ""


def _compare_text(a, b):
    out = []
    at, bt = [_norm(t) for _, t in a], [_norm(t) for _, t in b]
    sm = difflib.SequenceMatcher(None, at, bt, autojunk=False)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            continue
        olds = list(range(a1, a2))
        news = list(range(b1, b2))
        # pair most similar blocks inside a replaced region
        used = set()
        for i in olds:
            best, bj = 0.0, None
            for j in news:
                if j in used:
                    continue
                r = difflib.SequenceMatcher(None, at[i], bt[j], autojunk=False).ratio()
                if r > best:
                    best, bj = r, j
            if best < 0.5:
                lab = _label(at[i])
                bj = next((j for j in news if j not in used and lab and _label(bt[j]) == lab), None)
                best = 0.5 if bj is not None else 0.0
            if bj is not None and best >= 0.5:
                used.add(bj)
                out.append((bj, _judge_modified(at[i], bt[bj], b[bj][0])))
            else:
                out.append((b1 + 0.5 - 1e-6 + (i - a1) * 1e-9, _judge_block("removed", at[i], a[i][0])))
        for j in news:
            if j not in used:
                out.append((j, _judge_block("added", bt[j], b[j][0])))
    out.sort(key=lambda t: t[0])
    return _merge_moves([c for _, c in out])


def _merge_moves(changes):
    """A removed block and an added block with (almost) the same text is a move, not two changes."""
    removed = [c for c in changes if c.kind == "removed"]
    added = [c for c in changes if c.kind == "added"]
    used_add, drop = set(), set()
    merged = {}
    for r in removed:
        best, bi = 0.0, None
        for i, a in enumerate(added):
            if i in used_add:
                continue
            ratio = difflib.SequenceMatcher(None, r.old, a.new, autojunk=False).ratio()
            if ratio > best:
                best, bi = ratio, i
        if best < 0.85 and _label(r.old):
            bi2 = next((i for i, a in enumerate(added) if i not in used_add and _label(a.new) == _label(r.old)), None)
            if bi2 is not None:
                bi, best = bi2, 0.85
        if bi is not None and best >= 0.85:
            a = added[bi]
            used_add.add(bi)
            drop.add(id(r)); drop.add(id(a))
            if r.old == a.new:
                mv = Change(Severity.LOW, "moved", f"Moved from {r.location} to {a.location}", a.location, r.old, "")
            else:
                inner = _judge_modified(r.old, a.new, a.location)
                mv = Change(max(inner.severity, Severity.LOW) if inner.severity != Severity.FORMAT else Severity.LOW, "moved",
                            f"Moved from {r.location} to {a.location} and edited: {inner.title.lower()}", a.location, r.old, a.new)
            merged[id(a)] = mv
    out = []
    for c in changes:
        if id(c) in merged:
            out.append(merged[id(c)])
        elif id(c) not in drop:
            out.append(c)
    return out


def _compare_cells(a, b):
    da, db = dict(a), dict(b)
    out = []
    for loc in sorted(set(da) | set(db), key=lambda x: (x.split("!")[0], len(x), x)):
        if loc in da and loc in db:
            if da[loc] != db[loc]:
                out.append(_judge_modified(da[loc], db[loc], loc))
        elif loc in da:
            out.append(_judge_block("removed", da[loc], loc))
        else:
            out.append(_judge_block("added", db[loc], loc))
    return out


def compare(old_path, new_path, important_only=False):
    """Compare two files of the same family. Returns a list of Change sorted by severity."""
    ka, a = extract(old_path)
    kb, b = extract(new_path)
    if ka != kb:
        raise ValueError("Cannot compare a spreadsheet with a text document.")
    changes = _compare_cells(a, b) if ka == "cells" else _compare_text(a, b)
    if important_only:
        changes = [c for c in changes if c.severity >= Severity.MEDIUM]
    return sorted(changes, key=lambda c: -int(c.severity))

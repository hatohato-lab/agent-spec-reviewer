#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oracle.py — 査読の検出力を「ラベル付き見本」で測るオラクル。

査読（レビュー）は正解出力が一意でない（指摘の書き方は自由）。だから golden では測れない。
そこで、欠陥が分かっている見本（正例＋既知欠陥）を用意し、査読エージェントが
各見本の欠陥を正しく見つけ、正例を通すかで採点する。＝検出力(recall)と誤検出のなさを、ラベルで測る。

採点対象は「査読結果(JSON)」: {"<ファイル名>": {"conformant": bool, "issues": [キー...]}, ...}

使い方:
  python oracle.py                  # お手本の査読結果(reference)を採点 → PASS
  python oracle.py --verdicts PATH  # 査読エージェントの出力(JSON)を採点
  python oracle.py --selftest       # オラクル自身を検証（正しい査読→PASS / 雑な査読→FAIL）
終了コード: PASS（または selftest 期待どおり）で 0、それ以外 1。
"""
import argparse
import json
import sys
from pathlib import Path

# Windows コンソール(cp932)でも日本語・記号を出せるよう出力を UTF-8 に統一。
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EVAL = Path(__file__).resolve().parent
SELFTEST = EVAL / "selftest"

# 見本ごとの正解ラベル： (conformant の正解, 必ず報告すべき issue キー)
EXPECTED = {
    "good_agent.md": (True, set()),
    "broken_missing_name.md": (False, {"missing-name"}),
    "broken_missing_description.md": (False, {"missing-description"}),
    "broken_bad_frontmatter.md": (False, {"invalid-frontmatter"}),
    "broken_obsolete_workaround.md": (True, {"obsolete-workaround"}),  # 構造は適合・中身が陳腐化
}


def grade(verdicts):
    for fx, (exp_conf, exp_issues) in EXPECTED.items():
        v = verdicts.get(fx)
        if not isinstance(v, dict) or "conformant" not in v or "issues" not in v:
            return ("FAIL", f"{fx}: 査読結果が無い／形式不正")
        reported = set(v["issues"])
        if v["conformant"] != exp_conf:
            return ("FAIL", f"{fx}: conformant={v['conformant']}（正解 {exp_conf}）")
        if not exp_issues.issubset(reported):
            miss = sorted(exp_issues - reported)
            return ("FAIL", f"{fx}: 欠陥 {miss} を見逃し（報告={sorted(reported)}）")
        if exp_issues == set() and reported != set():
            return ("FAIL", f"{fx}: 正例なのに誤検出（報告={sorted(reported)}）")
    return ("PASS", f"全{len(EXPECTED)}件を正しく判定（欠陥を検出・正例を通す）")


def grade_path(path):
    try:
        verdicts = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return ("FAIL", f"読込失敗: {e}")
    try:
        return grade(verdicts)
    except Exception as e:
        return ("FAIL", f"採点エラー: {type(e).__name__}: {e}")


def table(rows, title):
    print(f"\n### {title}")
    print("| 対象 | 判定 | 詳細 |")
    print("|---|---|---|")
    for n, v, d in rows:
        print(f"| {n} | {v} | {d} |")


def selftest():
    print("# オラクル自己検証 — agent-spec-reviewer（査読の検出力）")
    rv, rd = grade_path(SELFTEST / "reference_verdicts.json")
    table([("reference_verdicts.json", rv, rd)], "① 正しい査読（PASS であるべき）")
    controls = [
        ("broken_blind.json", "全部 conformant＝何も見つけない（早く切り上げ）"),
        ("broken_misses_obsolete.json", "構造は見るが陳腐化を見逃す（浅い査読）"),
    ]
    brows, caught = [], True
    for f, why in controls:
        v, d = grade_path(SELFTEST / f)
        ok = (v == "FAIL")
        caught = caught and ok
        brows.append((f, v, ("検出OK " if ok else "検出NG ") + d))
    table(brows, "② 雑な査読（FAIL であるべき）")
    valid = (rv == "PASS") and caught
    print(f"\n## オラクル判定: {'PASS（雑な査読を弾き正しい査読を通す＝信頼できる）' if valid else 'FAIL（オラクル自体に欠陥）'}")
    return valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdicts", help="査読結果 JSON のパス")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    path = a.verdicts if a.verdicts else (SELFTEST / "reference_verdicts.json")
    v, d = grade_path(path)
    table([(Path(path).name, v, d)], "採点（査読の検出力）")
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()

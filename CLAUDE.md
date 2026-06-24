# CLAUDE.md — agent-spec-reviewer

このリポジトリは「Claude Code のエージェント定義を査読する」エージェントと、その採点係（査読の検出力をラベル付き見本で測る）です。
査読は仕様適合（`conformant`）と問題一覧（`issues`：仕様違反も陳腐化も）を JSON で返します。深さ（`depth`：quick/standard/deep）を指定でき、deep は公式 docs を取得して照合します。

## 確認のしかた

- `python eval/oracle.py --selftest` … 採点係が正しいか（正しい査読=PASS／雑な査読=FAIL）
- `python eval/oracle.py --verdicts <査読結果JSONのパス>` … 査読結果を採点
- `python eval/oracle.py` … お手本の査読結果(reference)を採点

## いじるときの約束（評価駆動 / EDD）

- 先に eval（仕込んだ欠陥を全部検出）を満たすことを確認してから「完成」とする。雰囲気で done にしない。
- 終わりはモデルの気分でなく eval が決める（早く切り上げる査読は selftest で弾かれる）。
- `eval/corpus/` の見本と `eval/selftest/*.json` は採点係の検証用。むやみに変えない。
- Python 標準ライブラリのみ。秘密情報・個人情報・客先コードを入れない。

## ファイルの役割

- `.claude/agents/agent-spec-reviewer.md` … 査読エージェント定義
- `eval/oracle.py` … 採点係（検出力をラベルで採点）／`design/design.md` … 設計／`README.md` … 説明

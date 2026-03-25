# Observer Meaning Design Memo v0.1
## UEH Observer 引継ぎ設計メモ（意味設計フェーズ初期草案）

- Status: Draft
- Version: v0.1
- Date: 2026-03
- Scope: Observer meaning model / no-position handling / metric normalization
- Phase: 実データ接続後の意味設計

---

# 1. 背景

UEH Observer は、Aave 実データ接続に到達し、`getUserAccountData()` を通じた観測が可能になった。

この段階で、Observer は「動作するプロトタイプ」から、「取得した値にどのような意味を与えるか」を定義する段階へ移行した。

特に、借入のないウォレットに対して Health Factor が無限相当の巨大値として返る挙動が確認され、これをそのまま Observer の表示値として扱うと、意味上および UI 上の誤解を生むことが明らかになった。

この文書は、その問題に対する初期設計判断を固定するための草案である。

---

# 2. 現在地

## 2.1 到達済み事項

### アーキテクチャ
- CLI / Engine / Protocol 分離
- Observer 構造確立
- Board 形式 UI 整理済

### 状態モデル
- STABLE
- WATCH
- BOUNDARY_APPROACHING
- DEGRADED
- REFUSAL

### Trust モデル
- primary / secondary source
- Block / Lag 導入済

### 実データ接続
- web3.py 導入完了
- Ethereum RPC 接続成功
- Aave Pool contract 接続成功
- `getUserAccountData()` 呼び出し成功

## 2.2 実観測で見えた問題
- データ取得自体は成功している
- 借入なしウォレットでは Health Factor が巨大値になる
- これはプロトコル上は自然でも、Observer の意味モデル上は未整理
- 現状のままだと「値はあるが意味がない」表示になる

---

# 3. 問題定義

Observer の目的は、単に値を取得して並べることではなく、観測結果を意味のある状態へ変換することである。

その観点から、以下の問題が存在する。

## 3.1 Health Factor 無限相当問題
借入が存在しない場合、Health Factor は実質的に無限相当となるが、これをそのまま表示すると以下の誤解を招く。

- 非常に安全な借入ポジションであるように見える
- 「最強に健全」という誤読が発生する
- 実際には借入ポジション自体が存在しないという事実が隠れる

## 3.2 Liquidation Distance 不成立問題
借入が存在しない場合、清算距離の概念そのものが成立しない。

そのため、数値として `0` や任意値を置くのは誤りである。

## 3.3 状態モデルの欠落
既存状態モデルは「借入ポジションが存在する」ことを暗黙の前提としており、
「観測対象としての借入ポジションが存在しない」状態を表現できていない。

---

# 4. 設計目標

今回の設計で達成すべき目標は以下の通り。

1. 借入なし状態を独立した状態として表現する
2. 意味を持たない値を Observer 内部で正規化する
3. UI で誤読される表示を排除する
4. 将来の advice layer に備えて意味モデルを安定化する

---

# 5. 基本設計方針

Observer は、取得値をそのまま表示するのではなく、
「観測可能な値」と「意味を持つ指標」を分離して扱う。

そのため、以下を基本原則とする。

## 5.1 原則
- 定義不能なものは数値として表示しない
- 状態が存在しないことも状態として扱う
- UI の都合ではなく、意味モデルに基づいて正規化する
- 正規化はできるだけ早いレイヤーで行う

## 5.2 一行要約
Observer は「見えた値」を出すのではなく、「解釈可能な状態」を返す。

---

# 6. 新状態の導入

## 6.1 新規追加状態
`NO_POSITION`

## 6.2 定義
`NO_POSITION` は、借入ポジションが存在しないため、
清算リスク観測の前提が成立していない状態を表す。

これは「非常に安全」を意味しない。

また、「健全な借入状態」でもない。

意味としては以下である。

- borrow position absent
- liquidation risk not applicable
- health factor not applicable

## 6.3 判定条件
```python
if total_debt == 0:
    status = "NO_POSITION"
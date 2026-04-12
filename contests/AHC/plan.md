# 🐍 Snake AI 改善 実装書

## 🎯 目的

本ドキュメントは、既存のスネークAIコードをより高性能にするための実装指針をまとめたものである。

---

# 🧠 全体方針

現在のAIは以下の要素で構成されている：

* DFSによる経路探索
* ヒートマップによる将来評価
* flood fillによる安全判定

これを以下の4方向で改善する：

1. 探索アルゴリズムの強化
2. 評価関数の高度化
3. 詰み検出の強化
4. 計算時間の最適化

---

# ① 探索アルゴリズムの強化

## ❗ 問題点

* DFSは分岐が多いと非効率
* 深い良手を見逃す可能性

---

## ✅ 改善案1: ビームサーチ

### 概要

評価の高い状態のみを保持して探索を進める

### 実装

```cpp
struct State {
    vector<pair<int,int>> body;
    int curr_len;
    long long score;
    string path;
};

vector<State> beam;
beam.push_back(initial_state);

for (int step = 0; step < MAX_DEPTH; step++) {
    vector<State> next;

    for (auto &s : beam) {
        for (int d = 0; d < 4; d++) {
            State ns = simulate(s, d);
            if (!ns.valid) continue;
            next.push_back(ns);
        }
    }

    sort(next.begin(), next.end(), [](auto &a, auto &b){ return a.score > b.score; });
    if (next.size() > BEAM_WIDTH) next.resize(BEAM_WIDTH);
    beam = next;
}
```

### パラメータ

* BEAM_WIDTH: 20〜100 推奨

---

## ✅ 改善案2: A*風評価

```cpp
score = 現在スコア - 距離 * 重み
```

距離は「次に必要な餌」までのマンハッタン距離

---

# ② 評価関数の強化

## ✅ 改善案3: ループ回避

```cpp
map<pair<int,int>, int> visit_count;

visit_count[{x,y}]++;
score -= visit_count[{x,y}] * 100;
```

---

## ✅ 改善案4: 尾との距離

```cpp
int dist = abs(head.x - tail.x) + abs(head.y - tail.y);
score += dist * 50;
```

効果:

* 閉じ込め防止

---

## ✅ 改善案5: 空間形状評価

```cpp
if (通路の幅 == 1) score -= 2000;
```

例:

* 一本道 → 危険
* 分岐あり → 安全

---

# ③ 詰み検出の強化

## ❗ 現状

flood fillのみ

---

## ✅ 改善案6: 未来詰み検出

```cpp
if (次の状態でmobility == 0) {
    score -= 1000000;
}
```

さらに2〜3手先まで確認すると効果大

---

# ④ 計算時間の最適化

## ✅ 改善案7: ターン重要度で時間配分

```cpp
if (近くに餌あり) {
    探索深さ += 5;
}
```

---

## ✅ 改善案8: メモ化

```cpp
unordered_map<string, long long> memo;

if (memo.count(state_key)) return memo[state_key];
```

state_key:

* head位置
* body形状

```

平均スコアで評価

---

## ⑩ ハミルトン経路

### 概要

全マスを巡る固定ルートを作る

### 利点

* 絶対に詰まない

### 使い方

* 通常は従う
* 餌が近い時だけ逸脱

---

# 🎯 優先順位

## 🥇 最優先

* ビームサーチ
* 尾との距離

## 🥈 次

* ループ回避
* 未来詰み検出

## 🥉 上級

* モンテカルロ
* ハミルトン経路

---

# 🧪 チューニング指針

調整対象:

* 重み係数
* 深さ
* ビーム幅

方法:

* スコアをログ出力
* ケースごとに調整

---

# ✅ まとめ

本AIを強化するための鍵は：

* 探索の効率化（ビームサーチ）
* 評価の高度化（未来・空間）
* 詰み回避の精度向上

これらを組み合わせることで、安定して高スコアを狙えるAIになる。

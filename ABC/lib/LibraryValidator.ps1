# ライブラリ検証システム
# 実装したデータ構造やアルゴリズムの正確性を検証

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("DSU", "BIT", "SegTree", "RMQ", "Dijkstra", "All")]
    [string]$TestTarget,
    
    [string]$Language = "cpp"
)

function Test-DSU {
    Write-Host "🔍 DSU (Union-Find) の検証を開始..." -ForegroundColor Cyan
    
    # テストケース生成
    $testCode = @"
#include <bits/stdc++.h>
using namespace std;

// DSUの実装をここに貼り付け
struct DSU {
    vector<int> parent, sz;
    DSU(int n = 0) { init(n); }
    void init(int n) {
        parent.resize(n);
        sz.assign(n, 1);
        iota(parent.begin(), parent.end(), 0);
    }
    int leader(int x) {
        if (parent[x] == x) return x;
        return parent[x] = leader(parent[x]);
    }
    bool merge(int a, int b) {
        a = leader(a);
        b = leader(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a;
        sz[a] += sz[b];
        return true;
    }
    bool same(int a, int b) { return leader(a) == leader(b); }
    int size(int x) { return sz[leader(x)]; }
};

int main() {
    DSU uf(5);
    
    // テスト1: 初期状態
    assert(!uf.same(0, 1));
    assert(uf.size(0) == 1);
    
    // テスト2: 結合
    assert(uf.merge(0, 1));
    assert(uf.same(0, 1));
    assert(uf.size(0) == 2);
    
    // テスト3: 重複結合
    assert(!uf.merge(0, 1));
    
    // テスト4: 複数結合
    uf.merge(2, 3);
    uf.merge(1, 2);
    assert(uf.same(0, 3));
    assert(uf.size(0) == 4);
    
    cout << "✅ DSU: All tests passed!" << endl;
    return 0;
}
"@
    
    # 一時ファイルに書き込み
    $testFile = "$env:TEMP\test_dsu.cpp"
    $testCode | Out-File -FilePath $testFile -Encoding UTF8
    
    # コンパイル・実行
    try {
        & g++ -o "$env:TEMP\test_dsu.exe" $testFile -std=c++17
        & "$env:TEMP\test_dsu.exe"
        Write-Host "✅ DSU検証完了" -ForegroundColor Green
    } catch {
        Write-Host "❌ DSU検証失敗: $_" -ForegroundColor Red
    } finally {
        Remove-Item $testFile -ErrorAction SilentlyContinue
        Remove-Item "$env:TEMP\test_dsu.exe" -ErrorAction SilentlyContinue
    }
}

function Test-BIT {
    Write-Host "🔍 BIT (Fenwick Tree) の検証を開始..." -ForegroundColor Cyan
    
    $testCode = @"
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct BIT {
    int n; vector<ll> bit;
    BIT(int n=0){ init(n); }
    void init(int n_){ n = n_; bit.assign(n+1, 0); }
    void add(int i, ll x){ for(++i; i<=n; i += i & -i) bit[i] += x; }
    ll sum_prefix(int i){ ll s=0; for(++i; i>0; i -= i & -i) s += bit[i]; return s; }
    ll sum_range(int l,int r){ if(r<=l) return 0; return sum_prefix(r-1) - (l? sum_prefix(l-1):0); }
};

int main() {
    BIT bit(10);
    
    // テスト1: 初期状態
    assert(bit.sum_range(0, 10) == 0);
    
    // テスト2: 点更新
    bit.add(3, 5);
    bit.add(7, 3);
    assert(bit.sum_range(0, 10) == 8);
    assert(bit.sum_range(3, 4) == 5);
    assert(bit.sum_range(7, 8) == 3);
    assert(bit.sum_range(3, 8) == 8);
    
    // テスト3: 累積和
    assert(bit.sum_prefix(3) == 5);
    assert(bit.sum_prefix(7) == 8);
    
    cout << "✅ BIT: All tests passed!" << endl;
    return 0;
}
"@
    
    $testFile = "$env:TEMP\test_bit.cpp"
    $testCode | Out-File -FilePath $testFile -Encoding UTF8
    
    try {
        & g++ -o "$env:TEMP\test_bit.exe" $testFile -std=c++17
        & "$env:TEMP\test_bit.exe"
        Write-Host "✅ BIT検証完了" -ForegroundColor Green
    } catch {
        Write-Host "❌ BIT検証失敗: $_" -ForegroundColor Red
    } finally {
        Remove-Item $testFile -ErrorAction SilentlyContinue
        Remove-Item "$env:TEMP\test_bit.exe" -ErrorAction SilentlyContinue
    }
}

function Test-All {
    Write-Host "🚀 全ライブラリの検証を開始..." -ForegroundColor Yellow
    Test-DSU
    Test-BIT
    Write-Host "🎉 全検証完了!" -ForegroundColor Green
}

# メイン実行
switch ($TestTarget) {
    "DSU" { Test-DSU }
    "BIT" { Test-BIT }
    "All" { Test-All }
    default {
        Write-Host "指定されたテスト対象が見つかりません: $TestTarget" -ForegroundColor Red
    }
}
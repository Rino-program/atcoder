# AtCoder Competition Template v2.4.0 ALL (PyPy 7.3.20 / Python 3.11)
# ↑ https://github.com/Rino-program/atcoder/blob/main/.template/template.py

import os, sys
from collections import deque, defaultdict, Counter
from itertools import permutations, combinations, accumulate, product, chain
from sortedcontainers import SortedSet, SortedList, SortedDict
from bisect import bisect_left, bisect_right
from collections.abc import Callable
from copy import deepcopy
import operator
import heapq
import math
import string

# ===== JIT 設定・制限解除 =====
# 深い再帰のアンロールを無効化 (実測で約8.9倍高速 TLE/MLE防止)
try:
    import pypyjit
    pypyjit.set_param('max_unroll_recursion=-1')
except ImportError:
    pass
# 再帰深度の上限引き上げ
sys.setrecursionlimit(2*10**6)
# 巨大整数の文字列変換エラーを防止
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

# ===== 入力ヘルパ =====
input = lambda: sys.stdin.readline().rstrip()
INT = lambda: int(input())
INT0 = lambda: int(input()) - 1
MAP = lambda: map(int, input().split())
MAP0 = lambda: (int(x) - 1 for x in input().split())
LIST = lambda: list(map(int, input().split()))
LIST0 = lambda: [int(x) - 1 for x in input().split()]
TUPLE = lambda: tuple(map(int, input().split()))
TUPLE0 = lambda: tuple(int(x) - 1 for x in input().split())
LISTS = lambda n: [list(map(int, input().split())) for _ in range(n)]
LISTS0 = lambda n: [[int(x) - 1 for x in input().split()] for _ in range(n)]
TUPLES = lambda n: [tuple(map(int, input().split())) for _ in range(n)]
TUPLES0 = lambda n: [tuple(int(x) - 1 for x in input().split()) for _ in range(n)]
LISTSI = lambda n: [int(input()) for _ in range(n)]
LISTSI0 = lambda n: [int(input()) - 1 for _ in range(n)]
STR = lambda: input()
STRS = lambda n: [input() for _ in range(n)]
CHARS = lambda: list(input())
CHARSL = lambda n: [list(input()) for _ in range(n)]
CHARSLI = lambda n: [list(map(int, input())) for _ in range(n)]

# ===== 高速 print =====
def print(*args, sep=' ', end='\n', file=None, flush=False):
    file = file or sys.stdout
    sep = ' ' if sep is None else sep
    end = '\n' if end is None else end
    file.write(sep.join(map(str, args)) + end)
    flush and file.flush()

# ===== 定数 =====
INF = 10 ** 18
MOD = 998244353
# MOD = 10**9 + 7

# ===== 関数短縮 =====
pr = print
en = enumerate
hepu = heapq.heappush
hepo = heapq.heappop
bil = bisect_left
bir = bisect_right
dedict = defaultdict

# ===== 方向ベクトル(上(負)から時計回り) =====
DIR4 = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIR8 = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
DIR9 = DIR8 + ((0, 0),) # 中央は最後

# ===== 文字列のリスト =====
LOWER = list(string.ascii_lowercase) # 小文字 a-z の文字列リスト
UPPER = list(string.ascii_uppercase) # 大文字 A-Z の文字列リスト
DIGITS = list(string.digits) # 数字 0-9 の文字列リスト

# ===== よく使う出力関数 =====
Yes = lambda **kwargs: print("Yes", **kwargs)
No = lambda **kwargs: print("No", **kwargs)
yes = lambda **kwargs: print("yes", **kwargs)
no = lambda **kwargs: print("no", **kwargs)
YES = lambda **kwargs: print("YES", **kwargs)
NO = lambda **kwargs: print("NO", **kwargs)

def yn(cond: bool, yes: str = "Yes", no: str = "No", **kwargs) -> None:
    """条件に応じてYes/No出力"""
    print(yes if cond else no, **kwargs)

def print_grid(grid: list[list], sep: str = '') -> None:
    """グリッド表示"""
    print('\n'.join(sep.join(map(str, row)) for row in grid))

# ============================================================
# 数学・整数論
# ============================================================

import random
def is_prime(n: int, k_random: int = 15) -> bool:
    """
    整数 n が素数かどうかを判定する (ミラー-ラビン素数判定法)。

    対応範囲:
        - n < 2^64: 100% 決定論的判定 (反例が存在しない底を選択、完全AC保証)
        - n >= 2^64: 確率的判定 (固定12底 + ランダム k_random 底によるHack完全耐性)

    計算量:
        【時間計算量】(テストする基底の合計個数を K とする)
        - 最悪ケース (素数の場合):
            - n < 2^64  : O(K log n)  (K <= 7, 約450演算, 数μs〜数十μs)
            - n >= 2^64 : O(K log^3 n) [K = 12 + k_random, 2^1024 規模でも約 0.1 秒]
        - 平均ケース (合成数の場合):
            - 99.9% 以上の合成数は「最初の1基底」で脱出するため、素数の 1/5〜1/10 以下の時間で終了

        【空間計算量】
        - n < 2^64  : O(1)
        - n >= 2^64 : O(log n) (n のビット長を保持するメモリのみ)

    引数:
        n (int): 判定対象の整数
        k_random (int, optional):
            n >= 2^64 の場合に追加するランダム基底の個数 (デフォルト: 15)。
            最悪誤判定確率は ≦ (1/4)^k_random。(実際に使用する場合はさらに低くなります)
            [目安]
            5: 高速優先 (誤判定率 ≦ 10^-3, 約 80ms @ 2^1024)
            15: 競プロ推奨 (誤判定率 ≦ 10^-9, 約 124ms @ 2^1024, Hack完全防御)
            40: 暗号標準水準 (誤判定率 ≦ 10^-24, 約 270ms @ 2^1024)

    戻り値:
        bool: 素数なら True, 合成数または 1 以下なら False
    """
    if n < 2:
        return False

    # 1. 小さな素数の事前判定 (37以下の素数での試し割り)
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # 37^2 = 1369 未満の合成数は上記で全て弾かれているため素数確定
    if n < 1369:
        return True

    # 2. n - 1 = 2^s * d (d は奇数) の形に分解
    d = n - 1
    s = (d & -d).bit_length() - 1
    d >>= s

    # 3. サイズに応じた基底の選択
    if n < 4759123141:
        # 3基底で決定論的 (Jaeschke, 1993)
        bases = (2, 7, 61)
    elif n < 18446744073709551616:  # 2^64
        # 7基底で決定論的 (Jim Sinclair, 2011)
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    else:
        # 2^64 以上の場合は固定12底 + 指定個数のランダム底
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        bases += [random.randrange(41, n - 1) for _ in range(k_random)]

    # 4. ミラー-ラビン判定メインループ
    for a in bases:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False

    return True


import random
def pollard_rho(n: int) -> int:
    """
    合成数 n の非自明な約数 (1 と n 以外の約数) を 1 つ見つける (ポラード・ロー法)。

    アルゴリズム:
        - Brent の循環検出法 + GCD バッチ処理 (128 ステップごとにまとめて gcd 計算)
        - 誕生日のパラドックスを利用し、最小素因数 p に対して O(√p) で衝突を検出

    計算量:
        【時間計算量】
        - 期待値: O(n^(1/4))
            - n ≦ 10^18 に対し、最大でも約 3×10^4 ステップ (数ms〜数十ms)
            - n が偶数または素数の場合は O(1) または O(log n) で即座に返却
        【空間計算量】
        - O(1)

    引数:
        n (int): 約数を探索する整数

    戻り値:
        int: n の非自明な約数 (n が素数の場合は n 自身、偶数の場合は 2)
    """
    if n % 2 == 0:
        return 2
    if is_prime(n):
        return n

    # 高速化: 最初の試行は固定値 (x=2, c=1) から開始して乱数生成オーバーヘッドを削減
    step_count = 0
    c = 1
    x = 2

    while True:
        if step_count > 0:
            c = random.randrange(1, n)
            x = random.randrange(1, n)
        step_count += 1

        y = x
        d = 1
        q = 1
        r = 1
        m = 128
        while d == 1:
            y = x
            for _ in range(r):
                x = (x * x + c) % n  # pow(x, 2, n) より高速
            k = 0
            while k < r and d == 1:
                ys = x
                limit = min(m, r - k)
                for _ in range(limit):
                    x = (x * x + c) % n
                    q = (q * abs(y - x)) % n
                d = math.gcd(q, n)
                k += m
            r *= 2

        if d == n:
            d = 1
            x = ys
            while d == 1:
                x = (x * x + c) % n
                d = math.gcd(abs(y - x), n)

        if d != 1 and d != n:
            return d


def prime_factors(n: int) -> dict[int, int]:
    """
    整数 n を高速に完全素因数分解し、{素因数: 指数} の昇順辞書を返す。

    アルゴリズム:
        - ポラード・ロー法 (pollard_rho) とミラー-ラビン法 (is_prime) の分割統治
        - 2 のべき乗は LSB ビット演算により O(1) で事前除去
        - 100 以下の小さな素因数を事前に試し割りで高速除去

    計算量:
        【時間計算量】
        - 期待値: O(n^(1/4))
            - n ≦ 10^18 に対して 0.01 秒以内 (AtCoder の 2.0s 制限で余裕で AC)
            - n 自体が素数の場合は is_prime により O(log n) (約 0.1 ms) で即答
        【空間計算量】
        - O(log n) (分割用のスタックおよび素因数格納辞書のみ)

    引数:
        n (int): 素因数分解する整数 (n >= 1)

    戻り値:
        dict[int, int]: {素因数: 指数} の昇順辞書 (例: 60 -> {2: 2, 3: 1, 5: 1})
                        n <= 1 の場合は空辞書 {}
    """
    if n <= 1:
        return {}

    factors = {}

    # 1. 2 で割れる回数を高速処理 (LSB ビット演算)
    s = (n & -n).bit_length() - 1
    if s > 0:
        factors[2] = s
        n >>= s
    if n == 1:
        return factors

    # 2. 小さな奇素数 (3〜97) の事前試し割り (ポラード・ロー法の呼び出し回数を大幅削減)
    small_primes = (
        3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
        43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
    )
    for p in small_primes:
        if p * p > n:
            break
        if n % p == 0:
            count = 0
            while n % p == 0:
                count += 1
                n //= p
            factors[p] = count
            if n == 1:
                return dict(sorted(factors.items()))

    if n == 1:
        return dict(sorted(factors.items()))

    # 3. ポラード・ロー法 + ミラー-ラビン法で残りの素因数を分解
    stack = [n]
    while stack:
        cur = stack.pop()
        if cur == 1:
            continue
        if is_prime(cur):
            factors[cur] = factors.get(cur, 0) + 1
            continue
        d = pollard_rho(cur)
        stack.append(d)
        stack.append(cur // d)

    return dict(sorted(factors.items()))

def divisors(n: int) -> list[int]:
    """概要:
        整数 n の正の約数を全列挙して昇順で返す。
    入力:
        n (int): 約数を求める対象の正整数。
    出力:
        list[int]: n の約数を昇順に並べたリスト。
    補足:
        計算量は O(√n)。
    """
    small = []
    large = []
    for i in range(1, math.isqrt(n) + 1):
        if n % i == 0:
            small.append(i)
            if i != n // i:
                large.append(n // i)
    return small + large[::-1]

def sieve(n: int) -> tuple[list[bool], list[int]]:
    """概要:
        0..n の素数判定配列と素数一覧をエラトステネスの篩で構築する。
    入力:
        n (int): 上限値。
    出力:
        tuple[list[bool], list[int]]: (is_prime配列, 素数リスト)。
    補足:
        計算量は O(n log log n)。偶数スキップにより高速化。
    """
    is_prime_arr = [True] * (n + 1)
    if n >= 0: is_prime_arr[0] = False
    if n >= 1: is_prime_arr[1] = False
    if n >= 4: is_prime_arr[4::2] = [False] * (((n - 4) // 2) + 1)
    for p in range(3, math.isqrt(n) + 1, 2):
        if is_prime_arr[p]:
            is_prime_arr[p * p : n + 1 : 2 * p] = [False] * (((n - p * p) // (2 * p)) + 1)
    primes = ([2] if n >= 2 else []) + [i for i in range(3, n + 1, 2) if is_prime_arr[i]]
    return is_prime_arr, primes

def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """概要:
        拡張ユークリッド互除法で ax + by = gcd(a, b) を満たす係数を求める。
    入力:
        a (int), b (int): 対象整数。
    出力:
        tuple[int, int, int]: (g, x, y)。g = gcd(a, b)、ax + by = g。
    補足:
        逆元計算や一次不定方程式で利用できる。計算量は O(log(min(a, b)))。
    """
    sign_a = -1 if a < 0 else 1
    sign_b = -1 if b < 0 else 1
    aa, bb = abs(a), abs(b)
    x0, y0, x1, y1 = 1, 0, 0, 1
    while bb:
        q, aa, bb = aa // bb, bb, aa % bb
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return aa, x0 * sign_a, y0 * sign_b

def mod_inverse(a: int, mod: int = MOD) -> int:
    """概要:
        a の mod における乗法逆元を返す。
    入力:
        a (int): 逆元を求める値。
        mod (int): 法。
    出力:
        int: a^{-1} mod mod。
    補足:
        mod が素数で a と mod が互いに素である前提（フェルマーの小定理）。
        計算量は O(log mod)。
    """
    return pow(a, -1, mod)

def ntt_convolution(a,b,mod=998244353,root=3):
    """概要:
        数論変換（NTT）で多項式 a,b の畳み込みを計算する。
    入力:
        a, b (list[int]): 係数列。mod は適切な原始根を持つ素数。
    出力:
        list[int]: mod を法とする畳み込み係数。
    計算量:
        時間 O((|a|+|b|) log(|a|+|b|))、空間 O(|a|+|b|)。
    補足:
        mod-1 が必要な2冪で割り切れ、root が原始根である必要がある。
    入力を mod 正規化し、空配列は []。998244353 の root=3 が標準。"""
    if not a or not b: return []
    n=1
    while n<len(a)+len(b)-1: n<<=1
    if mod <= 1 or not is_prime(mod) or not 1 <= root < mod or pow(root, mod - 1, mod) != 1 or (mod-1) % n:
        raise ValueError("mod must be prime and support the transform length")
    xmod=mod-1; q=2
    while q*q <= xmod:
        if xmod % q == 0:
            if pow(root,xmod//q,mod)==1: raise ValueError("root is not primitive")
            while xmod % q == 0: xmod//=q
        q+=1
    if xmod > 1 and pow(root,(mod-1)//xmod,mod)==1:
        raise ValueError("root is not primitive")
    def ntt(x,inv=False):
        j=0
        for i in range(1,n):
            bit=n>>1
            while j&bit: j^=bit; bit>>=1
            j^=bit
            if i<j: x[i],x[j]=x[j],x[i]
        l=2
        while l<=n:
            w=pow(root,(mod-1)//l,mod)
            if inv: w=pow(w,mod-2,mod)
            for i in range(0,n,l):
                z=1
                for j in range(i,i+l//2):
                    u=x[j]; v=x[j+l//2]*z%mod; x[j]=(u+v)%mod; x[j+l//2]=(u-v)%mod; z=z*w%mod
            l<<=1
        if inv:
            z=pow(n,mod-2,mod)
            for i in range(n): x[i]=x[i]*z%mod
    x=[z%mod for z in a]+[0]*(n-len(a)); y=[z%mod for z in b]+[0]*(n-len(b))
    ntt(x); ntt(y); x=[u*v%mod for u,v in zip(x,y)]; ntt(x,True)
    return x[:len(a)+len(b)-1]

def mat_mul(a,b,mod=None):
    """概要:
        行列 a と b の積を計算する。
    入力:
        a, b (list[list[int]]): 乗算可能な行列。mod は任意の法。
    出力:
        list[list[int]]: 行列積。mod が指定された場合は各要素を剰余にする。
    計算量:
        行列サイズを n×k, k×m とすると O(nkm)、空間 O(nm)。
    補足:
        mod=None では整数演算を行い、空行列にも対応する。
    """
    n=len(a); k=len(b); m=len(b[0]) if k else 0
    c=[[0]*m for _ in range(n)]
    for i in range(n):
        for t in range(k):
            for j in range(m): c[i][j]+=a[i][t]*b[t][j]
        if mod: c[i]=[x%mod for x in c[i]]
    return c

def mat_pow(a,e,mod=None):
    """概要:
        正方行列 a の e 乗を二分累乗で計算する。
    入力:
        a (list[list[int]]): 正方行列。e は 0 以上の整数。
    出力:
        list[list[int]]: a**e。e=0 では単位行列を返す。
    計算量:
        n×n 行列に対して O(n^3 log e)。
    補足:
        mod を指定すると各乗算後に剰余を取る。
    """
    n=len(a); r=[[int(i==j) for j in range(n)] for i in range(n)]
    while e:
        if e&1: r=mat_mul(r,a,mod)
        a=mat_mul(a,a,mod); e>>=1
    return r

def divisor_transform(a, zeta=False, multiple=False, inverse=False, mod=None):
    """概要:
        添字を整数とする約数側・倍数側のゼータ変換または Möbius 逆変換を行う。
    入力:
        a (list[int]): 添字 0..N-1 の値。multiple は倍数側を指定する。
        inverse は逆変換、mod は任意の法を指定する。
    出力:
        list[int]: 変換後の新しい配列（入力は変更しない）。
    計算量:
        時間 O(N log log N)、空間 O(N)。
    補足:
        zeta=False でも通常のゼータ変換として扱う（互換のための引数）。
    """
    n=len(a); b=a[:]
    for p in range(2,n):
        if all(p%d for d in range(2,int(p**0.5)+1)):
            js=range(p,n,p) if (multiple != inverse) else range(((n-1)//p)*p,p-1,-p)
            for j in js:
                if multiple:
                    if inverse: b[j//p]=(b[j//p]-b[j])%mod if mod else b[j//p]-b[j]
                    else: b[j//p]=(b[j//p]+b[j])%mod if mod else b[j//p]+b[j]
                else:
                    if inverse: b[j]=(b[j]-b[j//p])%mod if mod else b[j]-b[j//p]
                    else: b[j]=(b[j]+b[j//p])%mod if mod else b[j]+b[j//p]
    return b

class XorBasis:
    """概要:
        整数ベクトルの XOR 線形基底を管理する。
    入力:
        bits は扱う最大ビット数。insert(x) でベクトルを追加する。
    出力:
        can(x) は表現可能性、max_xor(x) は得られる最大値を返す。
    計算量:
        各操作 O(B)、空間 O(B)（B はビット数）。
    補足:
        非負整数を想定し、従属ベクトルの追加は False を返す。
    """
    def __init__(self,bits=61): self.b=[0]*bits
    def insert(self,x):
        for i in range(len(self.b)-1,-1,-1):
            if not (x>>i&1): continue
            if self.b[i]: x^=self.b[i]
            else:
                self.b[i]=x
                for j in range(i):
                    if self.b[j] and self.b[i]>>j&1: self.b[i]^=self.b[j]
                return True
        return False
    def can(self,x):
        for i in range(len(self.b)-1,-1,-1):
            if x>>i&1: x^=self.b[i]
        return x==0
    def max_xor(self,x=0):
        for v in self.b[::-1]: x=max(x,x^v)
        return x

def gf2_solve(rows, m=None):
    """概要:
        GF(2) 上の連立一次方程式を Gauss-Jordan 法で解く。
    入力:
        rows は係数と右辺をビットで表した整数列。m は変数数（省略可）。
    出力:
        tuple[int, list[int]]: 一つの解と自由変数の基底。不能なら None。
    計算量:
        時間 O(rm)、空間 O(r)。
    補足:
        各 row の m ビット目を右辺として扱う。
    """
    if m is None: m=max((x.bit_length() for x in rows),default=1)-1
    a=rows[:]; piv=[]; r=0
    for c in range(m):
        q=next((i for i in range(r,len(a)) if a[i]>>c&1),None)
        if q is None: continue
        a[r],a[q]=a[q],a[r]
        for i in range(len(a)):
            if i!=r and a[i]>>c&1: a[i]^=a[r]
        piv.append(c); r+=1
    mask=(1<<m)-1
    if any((x&mask)==0 and (x>>m&1) for x in a): return None
    x=0
    for i,c in enumerate(piv):
        if a[i]>>m&1: x|=1<<c
    free=[1<<c for c in range(m) if c not in piv]
    return x,free

# ============================================================
# 平面幾何 (2D Geometry)
# ============================================================

GEOM_EPS = 1e-9
class Point:
    """概要:
        2次元平面上の点・ベクトルを表すクラス。
        整数 (int) と実数 (float) の両方に完全対応。

    属性:
        x (float | int): X座標。
        y (float | int): Y座標。

    メソッド:
        dot(other): 内積。
        cross(other): 外積（2D 行列式）。
        norm2(): 長さの2乗。
        norm(): ユークリッドノルム（長さ）。
        dist2(other): 2点間距離の2乗。
        dist(other): 2点間距離。
        unit(): 単位ベクトル。
        normal(): 法線ベクトル（反時計回りに90度回転）。
        rotate(rad): 反時計回りに rad ラジアン回転したベクトル。
        angle(): 偏角 [-π, π]。

    計算量:
        四則演算・比較・各メソッドともにすべて O(1)。

    補足:
        整数座標同士の演算では除算を避けることで浮動小数点誤差を一切生じさせない。
    """
    __slots__ = ("x", "y")

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Point":
        return Point(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar: int) -> "Point":
        return Point(self.x // scalar, self.y // scalar)

    def __neg__(self) -> "Point":
        return Point(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        if isinstance(self.x, int) and isinstance(self.y, int) and isinstance(other.x, int) and isinstance(other.y, int):
            return self.x == other.x and self.y == other.y
        return abs(self.x - other.x) < GEOM_EPS and abs(self.y - other.y) < GEOM_EPS

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __lt__(self, other: "Point") -> bool:
        if isinstance(self.x, int) and isinstance(self.y, int) and isinstance(other.x, int) and isinstance(other.y, int):
            return (self.x, self.y) < (other.x, other.y)
        if abs(self.x - other.x) >= GEOM_EPS:
            return self.x < other.x
        return self.y < other.y - GEOM_EPS

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def dot(self, other: "Point") -> float | int:
        """内積 (dot product)"""
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Point") -> float | int:
        """外積 (cross product / 2D det)"""
        return self.x * other.y - self.y * other.x

    def norm2(self) -> float | int:
        """長さの2乗 (x^2 + y^2)"""
        return self.x * self.x + self.y * self.y

    def norm(self) -> float:
        """ユークリッドノルム（長さ）"""
        return math.hypot(self.x, self.y)

    def dist2(self, other: "Point") -> float | int:
        """2点間距離の2乗"""
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def dist(self, other: "Point") -> float:
        """2点間距離"""
        return math.hypot(self.x - other.x, self.y - other.y)

    def unit(self) -> "Point":
        """単位ベクトル"""
        l = self.norm()
        return Point(self.x / l, self.y / l)

    def normal(self) -> "Point":
        """反時計回りに90度回転した直交ベクトル"""
        return Point(-self.y, self.x)

    def rotate(self, rad: float) -> "Point":
        """反時計回りに rad ラジアン回転"""
        c = math.cos(rad)
        s = math.sin(rad)
        return Point(self.x * c - self.y * s, self.x * s + self.y * c)

    def angle(self) -> float:
        """偏角 [-π, π]"""
        return math.atan2(self.y, self.x)


class AngleSortKey:
    """概要:
        atan2 を一切使わず、完全整数演算（半平面判定＋外積）で偏角ソートを行うキー。
        浮動小数点誤差による WA を 100% 回避する。

    計算量:
        初期化 O(1)、比較 (__lt__) O(1)。
        N 個の点に対するソート全体で O(N log N)。

    補足:
        - 基準点 origin から見た偏角の昇順 [0, 2π) でソートする。
        - 偏角が同一の場合は origin からの距離昇順。
        - origin 自身は最も小さい要素として先頭に来る。

    使用例:
        points.sort(key=AngleSortKey)
        points.sort(key=lambda p: AngleSortKey(p, origin=P0))
    """
    __slots__ = ("p", "area", "dist2")

    def __init__(self, p: Point, origin: Point = Point(0, 0)):
        self.p = p - origin
        x, y = self.p.x, self.p.y
        # 領域: 0: 原点, 1: 上半平面(y>0 or (y==0 and x>0)), 2: 下半平面(y<0 or (y==0 and x<0))
        if x == 0 and y == 0:
            self.area = 0
        elif y > 0 or (y == 0 and x > 0):
            self.area = 1
        else:
            self.area = 2
        self.dist2 = x * x + y * y

    def __lt__(self, other: "AngleSortKey") -> bool:
        if self.area != other.area:
            return self.area < other.area
        crs = self.p.cross(other.p)
        if crs != 0:
            return crs > 0
        return self.dist2 < other.dist2


GEOM_EPS = 1e-9
CCW_COUNTER_CLOCKWISE = 1  # 反時計回り
CCW_CLOCKWISE = -1         # 時計回り
CCW_ONLINE_BACK = 2        # c-a-b 直線上 (c が a の後方)
CCW_ONLINE_FRONT = -2      # a-b-c 直線上 (c が b の前方)
CCW_ON_SEGMENT = 0         # a-c-b 線分上 (c が線分 ab 上)
def ccw(a: Point, b: Point, c: Point) -> int:
    """概要:
        点 a, b に対する点 c の位置関係を判定する。
    入力:
        a, b, c (Point): 判定対象の3点。
    出力:
        int: 位置関係を表す定数 (+1, -1, +2, -2, 0)。
    計算量:
        O(1)。
    補足:
        整数座標なら除算を行わず完全精度で判定。凸包や交差判定の基礎となる。
    使用例:
        res = ccw(Point(0, 0), Point(2, 0), Point(1, 1))  # 1 (反時計回り)
    """
    ba = b - a
    ca = c - a
    crs = ba.cross(ca)
    if isinstance(a.x, int) and isinstance(a.y, int) and isinstance(b.x, int) and isinstance(b.y, int) and isinstance(c.x, int) and isinstance(c.y, int):
        if crs > 0: return CCW_COUNTER_CLOCKWISE
        if crs < 0: return CCW_CLOCKWISE
        if ba.dot(ca) < 0: return CCW_ONLINE_BACK
        if ba.norm2() < ca.norm2(): return CCW_ONLINE_FRONT
        return CCW_ON_SEGMENT
    if crs > GEOM_EPS: return CCW_COUNTER_CLOCKWISE
    if crs < -GEOM_EPS: return CCW_CLOCKWISE
    if ba.dot(ca) < -GEOM_EPS: return CCW_ONLINE_BACK
    if ba.norm2() < ca.norm2() - GEOM_EPS: return CCW_ONLINE_FRONT
    return CCW_ON_SEGMENT


GEOM_EPS = 1e-9
def is_parallel(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    """概要:
        ベクトル a1->a2 と b1->b2 が平行かどうかを判定する。
    入力:
        a1, a2 (Point): ベクトル1の始点と終点。
        b1, b2 (Point): ベクトル2の始点と終点。
    出力:
        bool: 平行なら True、そうでなければ False。
    計算量:
        O(1)。
    """
    crs = (a2 - a1).cross(b2 - b1)
    if isinstance(a1.x, int) and isinstance(a1.y, int) and isinstance(a2.x, int) and isinstance(a2.y, int) and isinstance(b1.x, int) and isinstance(b1.y, int) and isinstance(b2.x, int) and isinstance(b2.y, int):
        return crs == 0
    return abs(crs) < GEOM_EPS


GEOM_EPS = 1e-9
def is_orthogonal(a1: Point, a2: Point, b1: Point, b2: Point) -> bool:
    """概要:
        ベクトル a1->a2 と b1->b2 が垂直かどうかを判定する。
    入力:
        a1, a2 (Point): ベクトル1の始点と終点。
        b1, b2 (Point): ベクトル2の始点と終点。
    出力:
        bool: 垂直なら True、そうでなければ False。
    計算量:
        O(1)。
    """
    dt = (a2 - a1).dot(b2 - b1)
    if isinstance(a1.x, int) and isinstance(a1.y, int) and isinstance(a2.x, int) and isinstance(a2.y, int) and isinstance(b1.x, int) and isinstance(b1.y, int) and isinstance(b2.x, int) and isinstance(b2.y, int):
        return dt == 0
    return abs(dt) < GEOM_EPS


class Line:
    """概要:
        異なる2点 a, b を通る直線を定義するクラス。

    属性:
        a (Point): 直線上の点1。
        b (Point): 直線上の点2。

    メソッド:
        projection(p): 点 p から直線への垂線の足（射影）を返す。
        reflection(p): 直線に関する点 p の線対称な点（反射）を返す。
        dist_to_point(p): 点 p と直線の最短距離を返す。

    計算量:
        初期化および全メソッド O(1)。
        a と b が同一点の場合は ValueError。
    """
    __slots__ = ("a", "b")

    def __init__(self, a: Point, b: Point):
        if a == b:
            raise ValueError("Line requires two distinct points")
        self.a = a
        self.b = b

    def projection(self, p: Point) -> Point:
        """点 p から直線への垂線の足"""
        v = self.b - self.a
        t = (p - self.a).dot(v) / v.norm2()
        return self.a + v * t

    def reflection(self, p: Point) -> Point:
        """直線に関する点 p の線対称な点"""
        return p + (self.projection(p) - p) * 2.0

    def dist_to_point(self, p: Point) -> float:
        """点 p と直線の最短距離"""
        v = self.b - self.a
        return abs(v.cross(p - self.a)) / v.norm()

    def __repr__(self) -> str:
        return f"Line({self.a}, {self.b})"


class Segment:
    """概要:
        2端点 a, b を結ぶ線分を定義するクラス。

    属性:
        a (Point): 線分の端点1。
        b (Point): 線分の端点2。

    メソッド:
        intersects(other): 線分同士が交差するか判定する。
        dist_to_point(p): 点 p と線分の最短距離を返す。
        dist_to_segment(other): 線分同士の最短距離を返す。

    計算量:
        初期化および全メソッド O(1)。
    """
    __slots__ = ("a", "b")

    def __init__(self, a: Point, b: Point):
        self.a = a
        self.b = b

    def intersects(self, other: "Segment") -> bool:
        """線分同士が交差するか判定（端点の接触も含む）"""
        if self.a == self.b:
            return other.dist_to_point(self.a) < GEOM_EPS
        if other.a == other.b:
            return self.dist_to_point(other.a) < GEOM_EPS
        return (
            ccw(self.a, self.b, other.a) * ccw(self.a, self.b, other.b) <= 0
            and ccw(other.a, other.b, self.a) * ccw(other.a, other.b, self.b) <= 0
        )

    def dist_to_point(self, p: Point) -> float:
        """点 p と線分の最短距離"""
        if self.a == self.b:
            return self.a.dist(p)
        if (self.b - self.a).dot(p - self.a) < 0:
            return (p - self.a).norm()
        if (self.a - self.b).dot(p - self.b) < 0:
            return (p - self.b).norm()
        return Line(self.a, self.b).dist_to_point(p)

    def dist_to_segment(self, other: "Segment") -> float:
        """線分同士の最短距離"""
        if self.intersects(other):
            return 0.0
        return min(
            self.dist_to_point(other.a),
            self.dist_to_point(other.b),
            other.dist_to_point(self.a),
            other.dist_to_point(self.b),
        )

    def __repr__(self) -> str:
        return f"Segment({self.a}, {self.b})"


GEOM_EPS = 1e-9
def line_intersection(l1: Line, l2: Line) -> Point | None:
    """概要:
        直線 l1 と l2 の交点を求める。
    入力:
        l1, l2 (Line): 交点を求める2本の直線。
    出力:
        Point | None: 交点座標。平行・同一直線の場合は None。
    計算量:
        O(1)。
    """
    v1 = l1.b - l1.a
    v2 = l2.b - l2.a
    d = v1.cross(v2)
    is_int = (
        isinstance(l1.a.x, int) and isinstance(l1.a.y, int) and
        isinstance(l1.b.x, int) and isinstance(l1.b.y, int) and
        isinstance(l2.a.x, int) and isinstance(l2.a.y, int) and
        isinstance(l2.b.x, int) and isinstance(l2.b.y, int)
    )
    if d == 0 if is_int else abs(d) < GEOM_EPS:
        return None
    return l1.a + v1 * ((l2.a - l1.a).cross(v2) / d)


def segment_intersection(s1: Segment, s2: Segment) -> Point | None:
    """概要:
        線分 s1 と s2 の交点を求める。
    入力:
        s1, s2 (Segment): 交点を求める2本の線分。
    出力:
        Point | None: 交点座標。交差しない場合は None。
    計算量:
        O(1)。
    """
    if not s1.intersects(s2):
        return None
    return line_intersection(Line(s1.a, s1.b), Line(s2.a, s2.b))


def polygon_area_2x(points: list[Point]) -> int | float:
    """概要:
        多角形の「有向面積の2倍」を靴ひも公式で求める。
    入力:
        points (list[Point]): 多角形の頂点列（反時計回りまたは時計回り）。
    出力:
        int | float: 反時計回りなら正、時計回りなら負の面積の2倍値。
    計算量:
        O(N)（N は頂点数）。
        点が空の場合は ValueError、1点の場合は (0.0, 0, 0)。
    補足:
        全頂点が整数座標の場合、除算を行わないため完全整数演算となり誤差が発生しない。
    """
    n = len(points)
    area2 = 0
    for i in range(n):
        area2 += points[i].cross(points[(i + 1) % n])
    return area2


def polygon_area(points: list[Point]) -> float:
    """概要:
        多角形の面積を求める。
    入力:
        points (list[Point]): 多角形の頂点列。
    出力:
        float: 多角形の正の面積。
    計算量:
        O(N)（N は頂点数）。
    """
    return abs(polygon_area_2x(points)) / 2.0


CCW_ON_SEGMENT = 0
def point_in_polygon(p: Point, poly: list[Point]) -> int:
    """概要:
        点 p と多角形の内外判定を行う（Winding Number 法）。
    入力:
        p (Point): 判定対象の点。
        poly (list[Point]): 多角形の頂点列。
    出力:
        int: 2: 内部 (IN), 1: 辺上 (ON), 0: 外部 (OUT)。
    計算量:
        O(N)（N は頂点数）。
    補足:
        凹多角形・自己交差のない一般多角形に対して有効。
    """
    n = len(poly)
    wn = 0
    for i in range(n):
        p1 = poly[i]
        p2 = poly[(i + 1) % n]
        if ccw(p1, p2, p) == CCW_ON_SEGMENT:
            return 1
        if p1.y <= p.y:
            if p2.y > p.y and (p2 - p1).cross(p - p1) > 0:
                wn += 1
        else:
            if p2.y <= p.y and (p2 - p1).cross(p - p1) < 0:
                wn -= 1
    return 2 if wn != 0 else 0


CCW_COUNTER_CLOCKWISE = 1
CCW_CLOCKWISE = -1
def convex_hull(points: list[Point], allow_on_edge: bool = False) -> list[Point]:
    """概要:
        アンドリューのアルゴリズム (Monotone Chain) で点集合の凸包を構築する。
    入力:
        points (list[Point]): 点集合。
        allow_on_edge (bool): 凸包の辺上（一直線上）の点も含めるかどうか。
    出力:
        list[Point]: 最左下から反時計回りに並んだ凸包の頂点列。
    計算量:
        O(N log N)（N は点数、ソートが支配的）。
    補足:
        同一直線上の点や縮退ケースも含め、境界点の順序・重複を完全対策済み。
    """
    pts = sorted(points)
    n = len(pts)
    if n <= 2:
        return pts

    def check(p1, p2, p3):
        c = ccw(p1, p2, p3)
        return (c == CCW_CLOCKWISE) if allow_on_edge else (c != CCW_COUNTER_CLOCKWISE)

    lower = []
    for p in pts:
        while len(lower) >= 2 and check(lower[-2], lower[-1], p):
            lower.pop()
        lower.append(p)

    # 全点が同一直線上にある場合の特別処理
    if len(lower) == n:
        return pts if allow_on_edge else [pts[0], pts[-1]]

    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and check(upper[-2], upper[-1], p):
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def convex_diameter(poly: list[Point]) -> tuple[float, int, int]:
    """概要:
        凸多角形の最遠点対間距離（直径）をキャリパー法（Rotating Calipers）で求める。
    入力:
        poly (list[Point]): 反時計回りの凸多角形頂点列。
    出力:
        tuple[float, int, int]: (最大距離, 頂点インデックス1, 頂点インデックス2)。
    計算量:
        O(N)（N は頂点数）。
    """
    n = len(poly)
    if n == 0:
        raise ValueError("convex_diameter requires at least one point")
    if n == 1:
        return 0.0, 0, 0
    if n == 2:
        return poly[0].dist(poly[1]), 0, 1

    is_min_x = min(range(n), key=lambda i: (poly[i].x, poly[i].y))
    is_max_x = max(range(n), key=lambda i: (poly[i].x, poly[i].y))

    i, j = is_min_x, is_max_x
    max_d2 = poly[i].dist2(poly[j])
    best_pair = (i, j)

    si, sj = i, j
    while i != sj or j != si:
        ni = (i + 1) % n
        nj = (j + 1) % n
        if (poly[ni] - poly[i]).cross(poly[nj] - poly[j]) >= 0:
            j = nj
        else:
            i = ni
        d2 = poly[i].dist2(poly[j])
        if d2 > max_d2:
            max_d2 = d2
            best_pair = (i, j)

    return math.sqrt(max_d2), best_pair[0], best_pair[1]


CCW_COUNTER_CLOCKWISE = 1
CCW_CLOCKWISE = -1
def convex_cut(poly: list[Point], line: Line) -> list[Point]:
    """概要:
        凸多角形を有向直線 line.a -> line.b で切断し、進行方向左側の多角形を返す。
    入力:
        poly (list[Point]): 切断対象の凸多角形頂点列。
        line (Line): 切断線（line.a -> line.b の向き）。
    出力:
        list[Point]: 直線の左側に残った凸多角形の頂点列。
    計算量:
        O(N)（N は頂点数）。
    """
    n = len(poly)
    res = []
    for i in range(n):
        cur = poly[i]
        nxt = poly[(i + 1) % n]
        c1 = ccw(line.a, line.b, cur)
        c2 = ccw(line.a, line.b, nxt)
        if c1 != CCW_CLOCKWISE:
            res.append(cur)
        if (c1 == CCW_COUNTER_CLOCKWISE and c2 == CCW_CLOCKWISE) or (c1 == CCW_CLOCKWISE and c2 == CCW_COUNTER_CLOCKWISE):
            p = line_intersection(Line(cur, nxt), line)
            if p is not None:
                res.append(p)
    return res


def closest_pair(points: list[Point]) -> tuple[float, Point, Point]:
    """概要:
        分割統治法により最近点対間の距離とその2点を求める。
    入力:
        points (list[Point]): 点集合。
    出力:
        tuple[float, Point, Point]: (最小距離, 点1, 点2)。
    計算量:
        O(N log N)（N は点数）。
    """
    pts = sorted(points, key=lambda p: (p.x, p.y))
    n = len(pts)

    def rec(l: int, r: int):
        if r - l <= 1:
            return float("inf"), None, None
        mid = (l + r) // 2
        mid_x = pts[mid].x
        d1, p1a, p1b = rec(l, mid)
        d2, p2a, p2b = rec(mid, r)
        d = min(d1, d2)
        best_p = (p1a, p1b) if d == d1 else (p2a, p2b)

        strip = [p for p in pts[l:r] if abs(p.x - mid_x) < d]
        strip.sort(key=lambda p: p.y)

        for i in range(len(strip)):
            for j in range(i + 1, len(strip)):
                if strip[j].y - strip[i].y >= d:
                    break
                dist = strip[i].dist(strip[j])
                if dist < d:
                    d = dist
                    best_p = (strip[i], strip[j])
        return d, best_p[0], best_p[1]

    return rec(0, n)


def lattice_points_on_segment(p1: Point, p2: Point) -> int:
    """概要:
        線分 p1-p2 上にある格子点の個数を求める（両端点を含む）。
    入力:
        p1, p2 (Point): 格子点座標（整数）。
    出力:
        int: 線分上の格子点数。
    計算量:
        O(log(min(|dx|, |dy|)))（ユークリッド互除法）。
    """
    return math.gcd(abs(p1.x - p2.x), abs(p1.y - p2.y)) + 1


def picks_theorem(poly: list[Point]) -> tuple[int, int]:
    """概要:
        ピックの定理 (S = I + B/2 - 1) を用いて、格子多角形の内部と境界上の格子点数を求める。
    入力:
        poly (list[Point]): 格子多角形の頂点列（全座標が整数）。
    出力:
        tuple[int, int]: (内部の格子点数 I, 境界上の格子点数 B)。
    計算量:
        O(N log(座標最大値))（N は頂点数）。
    """
    n = len(poly)
    b = 0
    for i in range(n):
        b += math.gcd(abs(poly[i].x - poly[(i + 1) % n].x), abs(poly[i].y - poly[(i + 1) % n].y))
    area2 = abs(polygon_area_2x(poly))
    inside = (area2 - b + 2) // 2
    return inside, b


GEOM_EPS = 1e-9
class Circle:
    """概要:
        中心 c と非負の半径 r を持つ円。

    属性:
        c (Point): 円の中心点。
        r (float): 半径。

    メソッド:
        intersect_line(line): 円と直線の交点リスト（0〜2個）を返す。
        intersect_circle(other): 2円の交点リスト（0〜2個）を返す。
        tangents_from_point(p): 点 p から円へ引いた接線の接点リスト（0〜2個）を返す。

    計算量:
        初期化および全メソッド O(1)。
        半径が負の場合は ValueError。
    """
    __slots__ = ("c", "r")

    def __init__(self, c: Point, r: float):
        if r < 0:
            raise ValueError("Circle radius must be non-negative")
        self.c = c
        self.r = r

    def intersect_line(self, line: Line) -> list[Point]:
        """円と直線の交点（0〜2個）"""
        pr = line.projection(self.c)
        d = (pr - self.c).norm()
        if d > self.r + GEOM_EPS:
            return []
        if abs(d - self.r) < GEOM_EPS:
            return [pr]
        base = math.sqrt(max(0.0, self.r * self.r - d * d))
        e = (line.b - line.a).unit()
        return [pr - e * base, pr + e * base]

    def intersect_circle(self, other: "Circle") -> list[Point]:
        """2円の交点を返す（0〜2個）"""
        d = self.c.dist(other.c)
        if d > self.r + other.r + GEOM_EPS or d < abs(self.r - other.r) - GEOM_EPS or abs(d) < GEOM_EPS:
            return []
        a = (self.r * self.r - other.r * other.r + d * d) / (2.0 * d)
        h = math.sqrt(max(0.0, self.r * self.r - a * a))
        v = (other.c - self.c).unit()
        n = v.normal()
        p = self.c + v * a
        if abs(h) < GEOM_EPS:
            return [p]
        return [p + n * h, p - n * h]

    def tangents_from_point(self, p: Point) -> list[Point]:
        """点 p から円へ引いた接線の接点（0〜2個）"""
        d2 = self.c.dist2(p)
        diff = d2 - self.r * self.r
        if diff < -GEOM_EPS:
            return []
        if abs(diff) < GEOM_EPS:
            return [p]
        d = math.sqrt(d2)
        l = math.sqrt(diff)
        sin_t = self.r / d
        cos_t = l / d
        v = (self.c - p).unit()
        p1 = p + Point(v.x * cos_t - v.y * sin_t, v.x * sin_t + v.y * cos_t) * l
        p2 = p + Point(v.x * cos_t + v.y * sin_t, -v.x * sin_t + v.y * cos_t) * l
        return [p1, p2]

    def __repr__(self) -> str:
        return f"Circle({self.c}, {self.r})"


GEOM_EPS = 1e-9
def circle_intersection_area(c1: Circle, c2: Circle) -> float:
    """概要:
        2つの円の共通部分（交差面積）を求める。
    入力:
        c1, c2 (Circle): 対象の2円。
    出力:
        float: 共通部分の面積。
    計算量:
        O(1)。
    """
    d = c1.c.dist(c2.c)
    if d >= c1.r + c2.r - GEOM_EPS:
        return 0.0
    if d <= abs(c1.r - c2.r) + GEOM_EPS:
        min_r = min(c1.r, c2.r)
        return math.pi * min_r * min_r
    theta1 = 2 * math.acos((c1.r * c1.r + d * d - c2.r * c2.r) / (2 * c1.r * d))
    theta2 = 2 * math.acos((c2.r * c2.r + d * d - c1.r * c1.r) / (2 * c2.r * d))
    s1 = 0.5 * c1.r * c1.r * (theta1 - math.sin(theta1))
    s2 = 0.5 * c2.r * c2.r * (theta2 - math.sin(theta2))
    return s1 + s2


GEOM_EPS = 1e-9
def circumscribed_circle(p1: Point, p2: Point, p3: Point) -> Circle | None:
    """概要:
        3点を通る円（外接円）を求める。
    入力:
        p1, p2, p3 (Point): 3点。
    出力:
        Circle | None: 外接円。同一直線上の場合は None。
    計算量:
        O(1)。
    """
    d = 2 * (p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y))
    if abs(d) < GEOM_EPS:
        return None
    p1_sq = p1.norm2()
    p2_sq = p2.norm2()
    p3_sq = p3.norm2()
    cx = (p1_sq * (p2.y - p3.y) + p2_sq * (p3.y - p1.y) + p3_sq * (p1.y - p2.y)) / d
    cy = (p1_sq * (p3.x - p2.x) + p2_sq * (p1.x - p3.x) + p3_sq * (p2.x - p1.x)) / d
    c = Point(cx, cy)
    return Circle(c, c.dist(p1))


import random
GEOM_EPS = 1e-9
def minimum_enclosing_circle(points: list[Point]) -> Circle:
    """概要:
        点集合を全て包含する最小包含円を Welzl のアルゴリズムで求める。
    入力:
        points (list[Point]): 点集合。
    出力:
        Circle: 最小包含円。
    計算量:
        期待値 O(N)、最悪 O(N^3)（N は点数）。
    """
    pts = list(points)
    random.shuffle(pts)

    def welzl(p_list: list[Point], r_list: list[Point], n: int) -> Circle:
        if n == 0 or len(r_list) == 3:
            if len(r_list) == 0:
                return Circle(Point(0, 0), 0.0)
            elif len(r_list) == 1:
                return Circle(r_list[0], 0.0)
            elif len(r_list) == 2:
                c = (r_list[0] + r_list[1]) / 2.0
                return Circle(c, c.dist(r_list[0]))
            else:
                return circumscribed_circle(r_list[0], r_list[1], r_list[2])

        p = p_list[n - 1]
        c = welzl(p_list, r_list, n - 1)
        if c.c.dist(p) <= c.r + GEOM_EPS:
            return c
        return welzl(p_list, r_list + [p], n - 1)

    return welzl(pts, [], len(pts))


# ============================================================
# 組み合わせ計算
# ============================================================

class Combination:
    """概要:
        階乗・逆階乗を前計算して組み合わせ関連値を高速に返すクラス。
        標準でONになるMODに注意。

    メソッド:
        nCr(n, r): 組み合わせ数 C(n, r) を返す。
        nPr(n, r): 順列数 P(n, r) を返す。
        nHr(n, r): 重複組み合わせ数 H(n, r) を返す。
        catalan(n): n 番目のカタラン数を返す。

    計算量:
        初期化 O(n + √mod + log mod)。nCr/nPr/nHr は O(1)、
        catalan は O(log mod)。mod を固定定数とみなせば、初期化 O(n)、
        catalan 以外の各クエリ O(1)。

    使用例:
        comb = Combination(200000)
        print(comb.nCr(10, 3))  # 120
    """
    def __init__(self, n: int, mod: int = MOD):
        if n < 0:
            raise ValueError("n must be non-negative")
        if mod <= 1 or not is_prime(mod) or n >= mod:
            raise ValueError("requires a prime mod and 0 <= n < mod")
        self.mod = mod
        self.fact = [1] * (n + 1)
        self.inv_fact = [1] * (n + 1)

        for i in range(1, n + 1):
            self.fact[i] = self.fact[i - 1] * i % mod

        self.inv_fact[n] = pow(self.fact[n], mod - 2, mod)
        for i in range(n - 1, -1, -1):
            self.inv_fact[i] = self.inv_fact[i + 1] * (i + 1) % mod

    def nCr(self, n: int, r: int) -> int:
        """組み合わせ nCr"""
        if n < 0 or r < 0 or r > n: return 0
        if n >= len(self.fact):
            raise ValueError("n exceeds the initialized limit")
        return self.fact[n] * self.inv_fact[r] % self.mod * self.inv_fact[n - r] % self.mod

    def nPr(self, n: int, r: int) -> int:
        """順列 nPr"""
        if n < 0 or r < 0 or r > n: return 0
        if n >= len(self.fact):
            raise ValueError("n exceeds the initialized limit")
        return self.fact[n] * self.inv_fact[n - r] % self.mod

    def nHr(self, n: int, r: int) -> int:
        """重複組み合わせ nHr = C(n+r-1, r)"""
        if n == 0 and r == 0: return 1
        if n <= 0 or r < 0: return 0
        return self.nCr(n + r - 1, r)

    def catalan(self, n: int) -> int:
        """カタラン数 C_n"""
        if n < 0 or 2 * n >= len(self.fact):
            raise ValueError("catalan(n) requires 0 <= 2*n <= initialized limit")
        return self.nCr(2 * n, n) * pow(n + 1, self.mod - 2, self.mod) % self.mod

def fast_mod_nCr(n: int, r: int, MOD: int = MOD) -> int:
    """概要:
        逐次積で組み合わせ nCr を求める。
    入力:
        n (int): 項数
        r (int): 選ぶ個数
        MOD (int): MOD
    出力:
        int: C(n, r) mod MOD
    補足:
        反復回数を少なくするため、r と n-r の小さい方を使う。
        計算量は O(√MOD + min(r, n-r) + log MOD)。
        MOD を固定定数とみなせば O(min(r, n-r))。
    """
    if MOD <= 1 or not is_prime(MOD) or n >= MOD:
        raise ValueError("requires a prime MOD and 0 <= n < MOD")
    if n < 0 or r < 0 or n < r:
        return 0
    if r == 0 or r == n:
        return 1
    if n-r < r:
        r = n-r
    comb = 1
    for x in range(n-r+1, n+1):
        comb = (comb * x) % MOD
    d = 1
    for x in range(1, r+1):
        d = (d * x) % MOD
    comb *= pow(d, MOD-2, MOD)
    return comb % MOD


# ============================================================
# 累積和
# ============================================================

def prefix_sum_2d(grid: list[list[int]]) -> list[list[int]]:
    """概要:
        2次元配列の累積和テーブルを構築する。
    入力:
        grid (list[list[int]]): 数値グリッド。
    出力:
        list[list[int]]: (H+1)×(W+1) の2次元累積和。
    補足:
        構築計算量は O(HW)。矩形和は inclusion-exclusion で O(1) 取得できる。
    """
    H = len(grid)
    if H == 0:
        return [[0]]
    W = len(grid[0])
    ps = [[0] * (W + 1) for _ in range(H + 1)]
    for i in range(H):
        for j in range(W):
            ps[i + 1][j + 1] = ps[i][j + 1] + ps[i + 1][j] - ps[i][j] + grid[i][j]
    return ps

def range_sum_2d(ps: list[list[int]], y1: int, x1: int, y2: int, x2: int) -> int:
    """概要:
        2次元累積和から矩形 [y1, y2) × [x1, x2) の総和を返す。
    入力:
        ps (list[list[int]]): 2次元累積和テーブル。
        y1, x1, y2, x2 (int): 半開区間の境界。
    出力:
        int: 指定矩形の総和。
    補足:
        `prefix_sum_2d` の戻り値を前提とする。計算量は O(1)。
    """
    return ps[y2][x2] - ps[y1][x2] - ps[y2][x1] + ps[y1][x1]


# ============================================================
# いもす法
# ============================================================

class Imos1D:
    """概要:
        1次元いもす法（差分配列）を扱うクラス。

    メソッド:
        add(l, r, x): 区間 [l, r) に x を加算予約する。
        build(): 全予約を反映した最終配列を返す。

    計算量:
        add は O(1)、build は O(n)。

    補足:
        複数区間更新をまとめて行い、最後に一度だけ累積して確定する。

    使用例:
        imos = Imos1D(10)
        imos.add(2, 5, 1)   # [2, 5) に +1
        imos.add(3, 7, 2)   # [3, 7) に +2
        result = imos.build()
    """
    def __init__(self, n: int):
        self.n = n
        self.diff = [0] * (n + 1)

    def add(self, l: int, r: int, x: int = 1) -> None:
        """[l, r) に x を加算"""
        self.diff[l] += x
        self.diff[r] -= x

    def build(self) -> list[int]:
        """累積和を計算して結果を返す"""
        result = [0] * self.n
        current = 0
        for i in range(self.n):
            current += self.diff[i]
            result[i] = current
        return result


class Imos2D:
    """概要:
        2次元いもす法（差分グリッド）を扱うクラス。

    メソッド:
        add(y1, x1, y2, x2, x): 矩形 [y1,y2)×[x1,x2) に x を加算予約する。
        build(): 全予約を反映した最終グリッドを返す。

    計算量:
        add は O(1)、build は O(HW)。

    補足:
        多数の矩形更新をまとめて処理したいときに有効。

    使用例:
        imos = Imos2D(H, W)
        imos.add(y1, x1, y2, x2, 1)  # [y1,y2) × [x1,x2) に +1
        result = imos.build()
    """
    def __init__(self, h: int, w: int):
        self.h = h
        self.w = w
        self.diff = [[0] * (w + 1) for _ in range(h + 1)]

    def add(self, y1: int, x1: int, y2: int, x2: int, x: int = 1) -> None:
        """[y1, y2) × [x1, x2) に x を加算（0-indexed）"""
        self.diff[y1][x1] += x
        self.diff[y1][x2] -= x
        self.diff[y2][x1] -= x
        self.diff[y2][x2] += x

    def build(self) -> list[list[int]]:
        """累積和を計算して結果を返す"""
        result = [row[:self.w] for row in self.diff[:self.h]]
        for i in range(self.h):
            for j in range(self.w):
                if j:
                    result[i][j] += result[i][j - 1]
        for j in range(self.w):
            for i in range(1, self.h):
                result[i][j] += result[i - 1][j]
        return result


# ============================================================
# union-Find
# ============================================================

class DSU:
    """概要:
        Union-Find（Disjoint Set Union）を提供するクラス。

    メソッド:
        leader(x): x の属する連結成分の代表元を返す。
        merge(a, b): a と b の成分を併合する。
        same(a, b): 同一成分か判定する。
        size(x): x の成分サイズを返す。
        group_count(): 現在の成分数を返す。
        groups(): 全成分を頂点リストで返す。

    計算量:
        leader/merge/same/size は償却 O(α(N))、group_count は O(1)、groups は O(Nα(N))。

    補足:
        経路圧縮とサイズ併合でほぼ償却 O(α(N))。

    使用例:
        uf = DSU(n)
        uf.merge(0, 1)
        print(uf.same(0, 1))  # True
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.n = n
        self._group_count = n

    def leader(self, x: int) -> int:
        """根を取得"""
        if self.parent[x] != x:
            self.parent[x] = self.leader(self.parent[x])
        return self.parent[x]

    def merge(self, a: int, b: int) -> bool:
        """併合（成功でTrue）"""
        a, b = self.leader(a), self.leader(b)
        if a == b: return False
        if self.rank[a] < self.rank[b]: a, b = b, a
        self.parent[b] = a
        self.rank[a] += self.rank[b]
        self._group_count -= 1
        return True

    def same(self, a: int, b: int) -> bool:
        """同じグループか"""
        return self.leader(a) == self.leader(b)

    def size(self, x: int) -> int:
        """xが属するグループのサイズ"""
        return self.rank[self.leader(x)]

    def group_count(self) -> int:
        """グループ数"""
        return self._group_count

    def groups(self) -> list[list[int]]:
        """全グループを取得"""
        result = defaultdict(list)
        for i in range(self.n):
            result[self.leader(i)].append(i)
        return list(result.values())


class WeightedDSU:
    """概要:
        ポテンシャル（重み差）付き Union-Find を提供するクラス。

    メソッド:
        merge(x, y, w): weight[x] - weight[y] = w を満たすように併合。
        diff(x, y): weight[x] - weight[y] を返す。
        same(x, y): 同一成分か判定する。
        leader(x), get_weight(x): 内部補助として重み情報を取得する。

    計算量:
        leader/get_weight/merge/diff/same は償却 O(α(N))。

    補足:
        差分制約の整合管理に使える。

    weight(x) - weight(y) = w となるような重みを管理
    使用例:
        wuf = WeightedDSU(n)
        wuf.merge(x, y, w)  # weight[x] - weight[y] = w
        diff = wuf.diff(x, y)  # weight[x] - weight[y]
    """
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.weight = [0] * n  # 親への重み

    def leader(self, x: int) -> int:
        if self.parent[x] == x:
            return x
        root = self.leader(self.parent[x])
        self.weight[x] += self.weight[self.parent[x]]
        self.parent[x] = root
        return root

    def get_weight(self, x: int) -> int:
        """xの重みを取得"""
        self.leader(x)
        return self.weight[x]

    def diff(self, x: int, y: int) -> int:
        """weight[x] - weight[y] を返す"""
        return self.get_weight(x) - self.get_weight(y)

    def merge(self, x: int, y: int, w: int) -> bool:
        """weight[x] - weight[y] = w となるよう併合"""
        if self.same(x, y):
            return self.diff(x, y) == w
        w += self.get_weight(y) - self.get_weight(x)
        x, y = self.leader(x), self.leader(y)
        if x == y: return False
        if self.rank[x] < self.rank[y]:
            x, y = y, x
            w = -w
        self.parent[y] = x
        self.weight[y] = -w
        self.rank[x] += self.rank[y]
        return True

    def same(self, x: int, y: int) -> bool:
        return self.leader(x) == self.leader(y)


# ============================================================
# グラフアルゴリズム
# ============================================================

def build_graph(n: int, edges: list[tuple[int, int]], idx: bool = True, directed: bool = False) -> list[list[int]]:
    """概要:
        辺集合から重みなしグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数（0-indexed を想定）。
        edges (list[tuple[int, int]]): 辺 (a, b) の配列。
        idx (bool): True なら頂点番号を0-indexedに調整する。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[int]]: 隣接リスト。
    補足:
        無向時は両方向に辺を追加する。計算量は O(n + m)（m は辺数）。
    """
    g = [[] for _ in range(n)]
    for a, b in edges:
        if idx:
            a -= 1
            b -= 1
        g[a].append(b)
        if not directed:
            g[b].append(a)
    return g

def build_weighted_graph(n: int, edges: list[tuple[int, int, int]], idx: bool = True, directed: bool = False) -> list[list[tuple[int, int]]]:
    """概要:
        辺集合から重み付きグラフの隣接リストを構築する。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (a, b, cost) の配列。
        idx (bool): True なら頂点番号を0-indexedに調整する。
        directed (bool): True なら有向、False なら無向。
    出力:
        list[list[tuple[int, int]]]: 隣接リスト（要素は (to, cost)）。
    補足:
        無向時は両方向に辺を追加する。計算量は O(n + m)（m は辺数）。
    """
    g = [[] for _ in range(n)]
    for a, b, c in edges:
        if idx:
            a -= 1
            b -= 1
        g[a].append((b, c))
        if not directed:
            g[b].append((a, c))
    return g

def bfs(g: list[list[int]], s: int) -> list[int]:
    """概要:
        重みなしグラフで始点 s からの最短距離を BFS で求める。
    入力:
        g (list[list[int]]): 隣接リスト。
        s (int): 始点。
    出力:
        list[int]: 各頂点への距離。未到達は -1。
    補足:
        計算量は O(V+E)。
    """
    dist = [-1] * len(g)
    dist[s] = 0
    q = deque([s])
    while q:
        v = q.popleft()
        for to in g[v]:
            if dist[to] == -1:
                dist[to] = dist[v] + 1
                q.append(to)
    return dist

def bfs_path(g: list[list[int]], s: int, t: int) -> list[int] | None:
    """概要:
        重みなしグラフで s から t への最短経路を BFS で求めて返す。
    入力:
        g (list[list[int]]): 隣接リスト。
        s (int): 始点。
        t (int): 終点。
    出力:
        list[int] | None: s から t への頂点列。到達不能なら None。
    補足:
        計算量は O(V+E)。経路が複数ある場合は最短の1つを返す。
    """
    n = len(g)
    parent = [-1] * n
    visited = [False] * n
    visited[s] = True
    q = deque([s])
    while q:
        v = q.popleft()
        if v == t:
            break
        for to in g[v]:
            if not visited[to]:
                visited[to] = True
                parent[to] = v
                q.append(to)
    if not visited[t]:
        return None
    path = []
    v = t
    while v != -1:
        path.append(v)
        v = parent[v]
    path.reverse()
    return path

def multi_source_bfs(g: list[list[int]], sources: list[int]) -> list[int]:
    """概要:
        複数始点から同時に BFS を行い最短距離を求める。
    入力:
        g (list[list[int]]): 隣接リスト。
        sources (list[int]): 始点集合。
    出力:
        list[int]: 各頂点への最短距離。未到達は -1。
    補足:
        始点を距離0で同時投入することで最近始点への距離になる。計算量は O(V+E)。
    """
    dist = [-1] * len(g)
    q = deque()
    for s in sources:
        if dist[s] == -1:
            dist[s] = 0
            q.append(s)
    while q:
        v = q.popleft()
        for to in g[v]:
            if dist[to] == -1:
                dist[to] = dist[v] + 1
                q.append(to)
    return dist

def bfs_grid(grid: list[list[str]], sy: int, sx: int, wall: str = '#') -> list[list[int]]:
    """概要:
        4近傍グリッド上で始点からの最短距離を BFS で求める。
    入力:
        grid (list[list[str]]): 盤面。
        sy, sx (int): 始点座標。
        wall (str): 通行不可セル文字。
    出力:
        list[list[int]]: 距離グリッド。未到達は -1。
    補足:
        `DIR4`（上下左右）を使用する。計算量は O(HW)。
    """
    H, W = len(grid), len(grid[0])
    dist = [[-1] * W for _ in range(H)]
    if grid[sy][sx] == wall:
        return dist
    dist[sy][sx] = 0
    q = deque([(sy, sx)])
    while q:
        y, x = q.popleft()
        for dy, dx in DIR4:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and dist[ny][nx] == -1 and grid[ny][nx] != wall:
                dist[ny][nx] = dist[y][x] + 1
                q.append((ny, nx))
    return dist

def dijkstra(g: list[list[tuple[int, int]]], s: int) -> list[int]:
    """概要:
        非負重みグラフで始点 s からの最短距離を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト。
        s (int): 始点。
    出力:
        list[int]: 各頂点への最短距離（未到達は INF）。
    補足:
        計算量は O((V+E)logE)。単純グラフなど E = O(V^2) の場合は
        O((V+E)logV) と書ける。負辺は非対応。
    """
    dist = [INF] * len(g)
    dist[s] = 0
    pq = [(0, s)]
    heappop = heapq.heappop
    heappush = heapq.heappush
    while pq:
        d, v = heappop(pq)
        if d > dist[v]: continue
        for to, w in g[v]:
            nd = d + w
            if nd < dist[to]:
                dist[to] = nd
                heappush(pq, (nd, to))
    return dist

def dijkstra_multi(
    g: list[list[tuple]],
    s: int,
    n_criteria: int = 2,
    better: Callable[[tuple, tuple], bool] | None = None,
) -> list[tuple]:
    """概要:
        複数基準（主: 距離最小, 副: 任意）を持つダイクストラ法。

    入力:
        g (list[list[tuple]]): 隣接リスト。各要素は (to, *values) の形式。
            values[0] が主コスト（最小化）、残りは副基準。
        s (int): 始点。
        n_criteria (int): 基準数（デフォルト2: 距離+1つの副基準）。
        better (Callable): (新状態tuple, 旧状態tuple) -> bool。
            None の場合は「主: 最小, 副: 最大」をデフォルト適用。

    出力:
        list[tuple]: dist[v] = (主コスト, 副基準1, ...) の最良値タプル。
                     未到達は (INF, 0, 0, ...) 相当。

    補足:
        主コストは非負で最小化する。better を指定すると、同じ主コストを
        含む状態の採否をカスタマイズできる。副基準の順序はヒープに依存せず、
        数値の単項マイナスも要求しない。任意の better に対する計算量と停止性は
        保証されない。better が Dijkstra 法の単調性を満たし、各頂点が高々 K 回
        更新される場合は、概ね O(K(V+E)log(KV) * n_criteria)。

    使用例（距離最小・木の数最大の2基準）:
        # g[v] = [(to, cost, tree_count), ...]
        dist = dijkstra_multi(g, 0)
        print(dist[N-1])  # (最短距離, 最大木の数)
    """
    INF_VAL = 10 ** 18
    n = len(g)
    if n_criteria < 1:
        raise ValueError("n_criteria must be at least 1")
    if not (0 <= s < n):
        raise ValueError("source must be a valid vertex")
    init = tuple([INF_VAL] + [0] * (n_criteria - 1))
    dist = [init] * n
    start = tuple([0] * n_criteria)
    dist[s] = start

    def default_better(new_state: tuple, old_state: tuple) -> bool:
        """主: 小さいほど良い, 副: 大きいほど良い"""
        if new_state[0] < old_state[0]:
            return True
        if new_state[0] == old_state[0]:
            return new_state[1:] > old_state[1:]
        return False

    _better = better if better else default_better

    # 主コストだけをヒープ順に使い、副基準の比較は better に委ねる。
    sequence = 0
    pq = [(start[0], sequence, s, start)]

    while pq:
        _, _, v, cur_state = heapq.heappop(pq)

        if not _better(cur_state, dist[v]) and cur_state != dist[v]:
            continue

        for edge in g[v]:
            to = edge[0]
            values = edge[1:]
            new_state = tuple(cur_state[i] + values[i] for i in range(n_criteria))
            if _better(new_state, dist[to]):
                dist[to] = new_state
                sequence += 1
                heapq.heappush(pq, (new_state[0], sequence, to, new_state))

    return dist

def dijkstra_path(g: list[list[tuple[int, int]]], s: int, t: int) -> tuple[int, list[int] | None]:
    """概要:
        非負重みグラフで s から t への最短距離と経路を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト（要素は (to, cost)）。
        s (int): 始点。
        t (int): 終点。
    出力:
        tuple[int, list[int] | None]:
            (最短距離, s から t への頂点列)。
            到達不能なら (INF, None)。
    補足:
        計算量は O((V+E)logE + V)。単純グラフなど E = O(V^2) の場合は
        O((V+E)logV) と書ける。負辺は非対応。
        経路が複数ある場合は最短の1つを返す。
    """
    n = len(g)
    dist = [INF] * n
    parent = [-1] * n
    dist[s] = 0
    pq = [(0, s)]
    heappop = heapq.heappop
    heappush = heapq.heappush
    while pq:
        d, v = heappop(pq)
        if d > dist[v]:
            continue
        for to, w in g[v]:
            nd = d + w
            if nd < dist[to]:
                dist[to] = nd
                parent[to] = v
                heappush(pq, (nd, to))

    if dist[t] == INF:
        return INF, None

    path = []
    v = t
    while v != -1:
        path.append(v)
        v = parent[v]
    path.reverse()
    return dist[t], path

def zero_one_bfs(g: list[list[tuple[int, int]]], s: int) -> list[int]:
    """概要:
        辺重みが 0/1 のグラフで最短距離を求める。
    入力:
        g (list[list[tuple[int, int]]]): 重み付き隣接リスト（重みは0または1）。
        s (int): 始点。
    出力:
        list[int]: 各頂点への最短距離（未到達は INF）。
    補足:
        0重みは deque の前、1重みは後ろへ投入して O(V+E)。
    """
    dist = [INF] * len(g)
    dist[s] = 0
    q = deque([s])
    while q:
        v = q.popleft()
        for to, w in g[v]:
            if w not in (0, 1):
                raise ValueError("zero_one_bfs requires edge weights 0 or 1")
            nd = dist[v] + w
            if nd < dist[to]:
                dist[to] = nd
                if w == 0:
                    q.appendleft(to)
                else:
                    q.append(to)
    return dist

def bellman_ford(n: int, edges: list[tuple[int, int, int]], s: int) -> tuple[list[int], bool]:
    """概要:
        Bellman-Ford 法で最短距離と負閉路有無を求める。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
        s (int): 始点。
    出力:
        tuple[list[int], bool]: (距離配列, 負閉路が検出されたか)。
    補足:
        計算量は O(VE)。
    """
    dist = [INF] * n
    dist[s] = 0
    for i in range(n):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated: break
        if i == n - 1: return dist, True
    return dist, False

def warshall_floyd(n: int, edges: list[tuple[int, int, int]]) -> list[list[int]]:
    """概要:
        Warshall-Floyd 法で全点対最短距離を求める。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
    出力:
        list[list[int]]: dist[i][j] = i から j への最短距離。
    補足:
        計算量は O(V^3)。頂点数が小さいケース向け。
    """
    dist = [[INF] * n for _ in range(n)]
    for i in range(n): dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] != INF and dist[k][j] != INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist

def topological_sort(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフをトポロジカルソートする。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: トポロジカル順序。閉路があれば None。
    補足:
        Kahn 法（入次数管理）を使用する。計算量は O(V+E)。
    """
    n = len(g)
    indeg = [0] * n
    for v in range(n):
        for to in g[v]:
            indeg[to] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    result = []
    while q:
        v = q.popleft()
        result.append(v)
        for to in g[v]:
            indeg[to] -= 1
            if indeg[to] == 0:
                q.append(to)
    return result if len(result) == n else None

def detect_cycle(g: list[list[int]]) -> list[int] | None:
    """概要:
        有向グラフで1つの閉路を DFS により検出する。
    入力:
        g (list[list[int]]): 有向グラフの隣接リスト。
    出力:
        list[int] | None: 閉路を構成する頂点列。なければ None。
    補足:
        色管理（未訪問/訪問中/訪問済）で後退辺を検出する。計算量は O(V+E)。
    """
    n = len(g)
    color = [0] * n  # 0:未訪問, 1: 訪問中, 2:訪問済
    parent = [-1] * n
    cycle = []

    def dfs(v: int) -> bool:
        color[v] = 1
        for to in g[v]:
            if color[to] == 1:  # 閉路発見
                cycle.append(to)
                u = v
                while u != to:
                    cycle.append(u)
                    u = parent[u]
                cycle.reverse()
                return True
            if color[to] == 0:
                parent[to] = v
                if dfs(to): return True
        color[v] = 2
        return False

    for i in range(n):
        if color[i] == 0:
            if dfs(i): return cycle
    return None

def bipartite_coloring(g: list[list[int]]) -> tuple[bool, list[int]]:
    """概要:
        グラフが二部グラフか判定し、可能なら2彩色を返す。
    入力:
        g (list[list[int]]): 無向グラフの隣接リスト。
    出力:
        tuple[bool, list[int]]: (二部グラフか, 色配列)。
    補足:
        非連結グラフにも対応し、各連結成分を BFS で処理する。計算量は O(V+E)。
    """
    n = len(g)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for to in g[v]:
                if color[to] == -1:
                    color[to] = color[v] ^ 1
                    q.append(to)
                elif color[to] == color[v]:
                    return False, color
    return True, color

def kruskal(n: int, edges: list[tuple[int, int, int]]) -> tuple[int, list[tuple[int, int, int]], bool]:
    """概要:
        Kruskal 法で最小全域木（または最小全域森）を構築する。
    入力:
        n (int): 頂点数。
        edges (list[tuple[int, int, int]]): 辺 (u, v, w) の配列。
    出力:
        tuple[int, list[tuple[int, int, int]], bool]:
            (総コスト, 採用辺リスト, グラフが連結でMST完成か)。
    補足:
        辺を重み昇順に処理し、DSUで閉路を回避する。計算量は O(ElogE)。
    """
    uf = DSU(n)
    cost = 0
    used = []
    for u, v, w in sorted(edges, key=lambda x: x[2]):
        if uf.merge(u, v):
            cost += w
            used.append((u, v, w))
    return cost, used, len(used) == n - 1

class MaxFlow:
    """概要:
        Dinic 法による最大流を提供するクラス。

    メソッド:
        add_edge(u, v, cap): u→v に容量 cap の辺を追加する。
        max_flow(s, t): s→t の最大流量を返す。

    計算量:
        add_edge は O(1)、_bfs は O(E)、_dfs は 1回あたり O(E)、max_flow は O(V^2E)。

    補足:
        計算量は O(V²E)。頂点数・辺数が数百程度なら十分高速。
        逆辺を自動管理するため、無向辺は add_edge を双方向で呼ぶか
        cap を同じ値で両方向に追加すること。

    使用例:
        mf = MaxFlow(n)
        mf.add_edge(0, 1, 10)
        mf.add_edge(1, 2, 5)
        print(mf.max_flow(0, 2))  # 5
    """
    def __init__(self, n: int):
        self.n = n
        self.graph = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, cap: int) -> None:
        """u→v に容量 cap の有向辺を追加（逆辺も自動追加）"""
        if cap < 0:
            raise ValueError("capacity must be non-negative")
        self.graph[u].append([v, cap, len(self.graph[v])])
        self.graph[v].append([u, 0, len(self.graph[u]) - 1])

    def _bfs(self, s: int) -> list[int]:
        """BFS でレベルグラフを構築"""
        level = [-1] * self.n
        level[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for to, cap, _ in self.graph[v]:
                if cap > 0 and level[to] == -1:
                    level[to] = level[v] + 1
                    q.append(to)
        return level

    def _dfs(self, v: int, t: int, f: int, level: list[int], it: list[int]) -> int:
        """DFS でブロッキングフローを流す"""
        if v == t:
            return f
        while it[v] < len(self.graph[v]):
            e = self.graph[v][it[v]]
            to, cap, rev = e
            if cap > 0 and level[v] < level[to]:
                d = self._dfs(to, t, min(f, cap), level, it)
                if d > 0:
                    e[1] -= d
                    self.graph[to][rev][1] += d
                    return d
            it[v] += 1
        return 0

    def max_flow(self, s: int, t: int) -> int:
        """s→t の最大流量を返す"""
        if not (0 <= s < self.n and 0 <= t < self.n):
            raise ValueError("source and sink must be valid vertices")
        if s == t:
            raise ValueError("source and sink must be distinct")
        flow = 0
        while True:
            level = self._bfs(s)
            if level[t] == -1:
                return flow
            it = [0] * self.n
            while True:
                f = self._dfs(s, t, INF, level, it)
                if f == 0:
                    break
                flow += f

class LowerBoundFlow:
    """概要:
        下限付きフロー（実行可能性判定 / 最小流）を扱うクラス。

    メソッド:
        add_edge(u, v, lo, hi): 下限 lo, 上限 hi の辺を追加する。
        is_feasible(): 実行可能かどうかを判定する。
        min_flow(s, t): s から t への実行可能な最小流量を求める。
    計算量:
        add_circulation/add_edge は O(1)。V を元の頂点数、E' を補助辺を含む
        ネットワークの辺数とすると、is_feasible は O(V^2 E')、
        min_flow は O((log U + 1)V^2 E')。U は探索する流量上限。

    補足:
        循環フロー (T→S) が必要な場合は add_circulation() を先に呼ぶ。

    使用例:
        lbf = LowerBoundFlow(n)
        lbf.add_circulation(T, S)   # 必要な場合のみ
        lbf.add_edge(u, v, lo, hi)
        print(lbf.is_feasible())
    """
    def __init__(self, n: int):
        self.n = n
        self.SS = n      # 超始点
        self.TT = n + 1  # 超終点
        self.mf = MaxFlow(n + 2)
        self.required = 0
        self.edges = []
        self.circulations = []

    def add_circulation(self, t: int, s: int) -> None:
        """T → S の循環辺（∞容量）を追加"""
        self.circulations.append((t, s, 0, INF))

    def add_edge(self, u: int, v: int, lo: int, hi: int) -> None:
        """下限 lo、上限 hi の辺を追加"""
        if lo < 0 or hi < lo:
            raise ValueError("requires 0 <= lo <= hi")
        self.edges.append((u, v, lo, hi))

    def is_feasible(self) -> bool:
        """実行可能かどうかを返す"""
        network = MaxFlow(self.n + 2)
        demand = [0] * self.n
        for u, v, lo, hi in self.edges + self.circulations:
            network.add_edge(u, v, hi - lo)
            demand[u] -= lo
            demand[v] += lo
        required = 0
        for v, value in enumerate(demand):
            if value > 0:
                network.add_edge(self.SS, v, value)
                required += value
            elif value < 0:
                network.add_edge(v, self.TT, -value)
        self.mf = network
        self.required = required
        return network.max_flow(self.SS, self.TT) == required

    def min_flow(self, s: int, t: int) -> int | None:
        """s から t への実行可能な最小流量を返す。

        下限・上限付き辺を使って s から t へ流す問題として扱う。
        実行不可能な場合は `None` を返す。既に `add_circulation` で
        追加した辺も制約の一部として含める。
        """
        if not (0 <= s < self.n and 0 <= t < self.n) or s == t:
            raise ValueError("requires distinct vertices in range")

        constraints = self.edges + self.circulations

        def build(upper: int, lower: int = 0):
            if lower < 0 or upper < lower:
                return None
            network = MaxFlow(self.n + 2)
            demand = [0] * self.n
            for u, v, lo, hi in constraints:
                network.add_edge(u, v, hi - lo)
                demand[u] -= lo
                demand[v] += lo

            artificial_index = len(network.graph[t])
            network.add_edge(t, s, upper - lower)
            demand[t] -= lower
            demand[s] += lower

            required = 0
            for v, value in enumerate(demand):
                if value > 0:
                    network.add_edge(self.SS, v, value)
                    required += value
                elif value < 0:
                    network.add_edge(v, self.TT, -value)

            return network, artificial_index, required

        network, artificial_index, required = build(INF)
        if network.max_flow(self.SS, self.TT) != required:
            return None
        artificial = network.graph[t][artificial_index]
        upper = network.graph[s][artificial[2]][1]

        def feasible(value: int) -> bool:
            network, _, required = build(value, value)
            return network.max_flow(self.SS, self.TT) == required

        low, high = -1, upper
        while high - low > 1:
            middle = (low + high) // 2
            if feasible(middle):
                high = middle
            else:
                low = middle
        return high

def bipartite_matching(
    n: int, m: int, adj: list[list[int]], return_matching: bool = False
) -> int | tuple[int, list[int]]:
    """概要:
        二部グラフの最大マッチング数を増加路DFSで求める。
    入力:
        n   (int)            : 左側頂点数（例: 生徒数）。0-indexed。
        m   (int)            : 右側頂点数（例: 席数）。0-indexed。
        adj (list[list[int]]): adj[i] = 左i から行ける右頂点リスト。
    出力:
        int | tuple[int, list[int]]: 最大マッチング数。`return_matching=True` の場合は
        (最大マッチング数, 右側から左側への対応) を返す。
    補足:
        計算量 O(V * E)。N≦数百程度なら十分高速。
        match_r[j] に最終的なマッチング結果が入る（右jに割り当てた左頂点）。
    使用例:
        adj = [[] for _ in range(N)]
        for i in range(N):
            for j in range(M):
                if ok[i][j]:
                    adj[i].append(j)
        ans = bipartite_matching(N, M, adj)
    """
    match_r = [-1] * m

    def dfs(i: int, visited: list[bool]) -> bool:
        for j in adj[i]:
            if visited[j]:
                continue
            visited[j] = True
            if match_r[j] == -1 or dfs(match_r[j], visited):
                match_r[j] = i
                return True
        return False

    ans = 0
    for i in range(n):
        visited = [False] * m
        if dfs(i, visited):
            ans += 1
    return (ans, match_r) if return_matching else ans

def scc(n, edges):
    """概要:
        有向グラフを Tarjan 法で強連結成分分解する。
    入力:
        n (int): 頂点数。edges (list[tuple[int,int]]): 有向辺。
    出力:
        tuple[int, list[int], list[list[int]]]: 成分数、各頂点の成分番号、
        重複辺を除いた縮約 DAG。
    計算量:
        時間 O(n+m)、空間 O(n+m)。
    補足:
        再帰を使わないため、深いグラフでも再帰上限に依存しない。
    使用例:
        count, comp, dag = scc(n, edges)
    """
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a].append(b)
    idx = [-1] * n; low = [0] * n; st = []; inst = [False] * n
    comp = [-1] * n; timer = 0; cc = 0
    for root in range(n):
        if idx[root] >= 0: continue
        idx[root] = low[root] = timer; timer += 1; st.append(root); inst[root] = True
        stack = [(root, 0)]
        while stack:
            v, i = stack[-1]
            if i < len(g[v]):
                to = g[v][i]; stack[-1] = (v, i + 1)
                if idx[to] < 0:
                    idx[to] = low[to] = timer; timer += 1
                    st.append(to); inst[to] = True; stack.append((to, 0))
                elif inst[to]:
                    low[v] = min(low[v], idx[to])
            else:
                stack.pop()
                if stack:
                    p = stack[-1][0]; low[p] = min(low[p], low[v])
                if low[v] == idx[v]:
                    while True:
                        x = st.pop(); inst[x] = False; comp[x] = cc
                        if x == v: break
                    cc += 1
    dag = [set() for _ in range(cc)]
    for a, b in edges:
        if comp[a] != comp[b]: dag[comp[a]].add(comp[b])
    return cc, comp, [list(x) for x in dag]

class LowLink:
    """概要:
        無向グラフの low-link 値、橋、関節点を求める。
    入力:
        LowLink(n, edges) の edges は (u, v)。多重辺にも対応する。
    出力:
        ord, low, bridges（入力辺番号）, articulation（頂点集合）を属性に保持する。
    計算量:
        構築 O(n+m)、空間 O(n+m)。
    補足:
        非連結グラフ、孤立点、多重辺を扱い、再帰を使わない。
    """
    def __init__(self, n, edges):
        self.n = n; self.edges = list(edges); g = [[] for _ in range(n)]
        for i, (a, b) in enumerate(self.edges):
            g[a].append((b, i)); g[b].append((a, i))
        self.ord = [-1] * n; self.low = [0] * n; self.parent_edge = [-1] * n
        self.bridges = []; self.articulation = set(); t = 0
        for root in range(n):
            if self.ord[root] >= 0: continue
            self.ord[root] = self.low[root] = t; t += 1
            st = [(root, -1, 0, 0)]
            while st:
                v, pe, i, child = st[-1]
                if i < len(g[v]):
                    to, ei = g[v][i]; st[-1] = (v, pe, i + 1, child)
                    if ei == pe: continue
                    if self.ord[to] < 0:
                        st[-1] = (v, pe, i + 1, child + 1)
                        self.parent_edge[to] = ei
                        self.ord[to] = self.low[to] = t; t += 1
                        st.append((to, ei, 0, 0))
                    else: self.low[v] = min(self.low[v], self.ord[to])
                else:
                    st.pop()
                    if pe != -1:
                        p = self.edges[pe][0] if self.edges[pe][1] == v else self.edges[pe][1]
                        self.low[p] = min(self.low[p], self.low[v])
                        if self.low[v] > self.ord[p]: self.bridges.append(pe)
                        if self.low[v] >= self.ord[p] and self.parent_edge[p] != -1:
                            self.articulation.add(p)
                    elif child > 1: self.articulation.add(v)
        self.bridges.sort()

class TwoSAT:
    """概要:
        含意グラフを用いて 2-SAT を解く。
    入力:
        add_clause(a, va, b, vb) は (x_a=va) または (x_b=vb) を追加する。
    出力:
        solve() は充足時に bool 配列、不能時に None を返す。
    計算量:
        追加 O(1)、solve は O(V+E) 時間・空間。
    補足:
        変数番号は 0-indexed。空の変数集合にも対応する。
    """
    def __init__(self,n):
        if n < 0: raise ValueError("n must be non-negative")
        self.n=n; self.g=[[] for _ in range(2*n)]
    def _id(self,i,v): return 2*i+int(v)
    def add_clause(self,a,va,b,vb):
        if not (0 <= a < self.n and 0 <= b < self.n): raise IndexError("variable index")
        x=self._id(a,va); y=self._id(b,vb); self.g[x^1].append(y); self.g[y^1].append(x)
    def solve(self):
        _,c,_=scc(2*self.n,[(u,v) for u in range(2*self.n) for v in self.g[u]])
        for i in range(self.n):
            if c[2*i]==c[2*i+1]: return None
        return [c[2*i]>c[2*i+1] for i in range(self.n)]

class MinCostFlow:
    """概要:
        ポテンシャル付き Dijkstra による最小費用流を扱う。
    入力:
        add_edge(u,v,cap,cost) で非負容量の有向辺を追加する。
        flow(s,t,limit) は最大 limit の流量を送る。
    出力:
        flow は (流量, 総費用) を返す。
    計算量:
        初期化 O(VE)、各増加路 O(E log V)。
    補足:
        負費用辺は許すが、負閉路がない入力を前提とする。
    使用例:
        f, cost = MinCostFlow(n).flow(s, t)
    """
    def __init__(self,n): self.n=n; self.g=[[] for _ in range(n)]
    def add_edge(self,u,v,cap,cost):
        self.g[u].append([v,cap,cost,len(self.g[v])]); self.g[v].append([u,0,-cost,len(self.g[u])-1])
    def flow(self,s,t,limit=10**30):
        if not (0 <= s < self.n and 0 <= t < self.n): raise IndexError("vertex index")
        if s == t or limit <= 0: return 0, 0
        n=self.n; pot=[0]*n
        # 負費用辺があっても reduced cost を非負にする初期ポテンシャル。
        for _ in range(n-1):
            changed=False
            for v in range(n):
                for to,cap,c,_ in self.g[v]:
                    if cap and pot[to] > pot[v] + c:
                        pot[to]=pot[v]+c; changed=True
            if not changed: break
        total=cost=0
        while total<limit:
            d=[INF]*n; pv=[None]*n; d[s]=0; h=[(0,s)]
            while h:
                x,v=heapq.heappop(h)
                if x!=d[v]: continue
                for i,e in enumerate(self.g[v]):
                    if e[1] and d[e[0]]>x+e[2]+pot[v]-pot[e[0]]:
                        d[e[0]]=x+e[2]+pot[v]-pot[e[0]]; pv[e[0]]=(v,i); heapq.heappush(h,(d[e[0]],e[0]))
            if d[t]==INF: break
            for v in range(n):
                if d[v]<INF: pot[v]+=d[v]
            f=limit-total; v=t
            while v!=s: p,i=pv[v]; f=min(f,self.g[p][i][1]); v=p
            v=t
            while v!=s:
                p,i=pv[v]; e=self.g[p][i]; e[1]-=f; self.g[v][e[3]][1]+=f; v=p
            total+=f; cost+=f*pot[t]
        return total,cost

def euler_path(n, edges, directed=False):
    """概要:
        Hierholzer 法でオイラー路またはオイラー閉路を求める。
    入力:
        n (int): 頂点数。edges: (u,v) の辺列。directed は有向指定。
    出力:
        list[int] | None: 辺を一度ずつ通る頂点列。存在しなければ None。
    計算量:
        時間 O(n+m)、空間 O(n+m)。
    補足:
        次数条件と全辺の連結性を検査し、多重辺にも対応する。
    """
    g=[[] for _ in range(n)]; deg=[0]*n; indeg=[0]*n
    for i,(a,b) in enumerate(edges):
        g[a].append((b,i)); deg[a]+=1; indeg[b]+=1
        if not directed: g[b].append((a,i)); deg[b]+=1
    start=next((i for i,x in enumerate(deg) if x),0)
    if directed:
        delta=[deg[i]-indeg[i] for i in range(n)]
        plus=[i for i,x in enumerate(delta) if x==1]
        minus=[i for i,x in enumerate(delta) if x==-1]
        if any(x not in (-1,0,1) for x in delta) or len(plus)!=len(minus) or len(plus)>1: return None
        if plus: start=plus[0]
    elif sum(x&1 for x in deg) not in (0,2): return None
    if not directed:
        odd=[i for i,x in enumerate(deg) if x&1]
        if odd: start=odd[0]
    used=[False]*len(edges); st=[start]; ans=[]
    while st:
        v=st[-1]
        while g[v] and used[g[v][-1][1]]: g[v].pop()
        if g[v]:
            to,i=g[v].pop(); used[i]=True; st.append(to)
        else: ans.append(st.pop())
    if len(ans)!=len(edges)+1: return None
    # Hierholzer's length check also rejects disconnected components for
    # undirected graphs, but directed equal-degree components need this test.
    reach=[[] for _ in range(n)]
    for a,b in edges:
        reach[a].append(b)
        if not directed: reach[b].append(a)
    stack=[start]; seen={start}
    while stack:
        v=stack.pop()
        for to in reach[v]:
            if to not in seen: seen.add(to); stack.append(to)
    if any((deg[i] or indeg[i]) and i not in seen for i in range(n)): return None
    return ans[::-1]

def bipartite_max_independent(left, right, edges):
    """概要:
        二部グラフの最大独立集合を求める。
    入力:
        left, right は左右の頂点数、edges は (左, 右) の辺。
    出力:
        tuple[list[int], list[int]]: 最大独立集合に含まれる左右頂点。
    計算量:
        時間 O(VE)、空間 O(V+E)。
    補足:
        König の定理と増加路法を使う。孤立点や空グラフにも対応する。
    """
    g=[[] for _ in range(left)]
    for a,b in edges: g[a].append(b)
    mt=[-1]*right
    def dfs(v,seen):
        for u in g[v]:
            if seen[u]: continue
            seen[u]=1
            if mt[u]<0 or dfs(mt[u],seen): mt[u]=v; return True
        return False
    for v in range(left): dfs(v,[0]*right)
    matched={v for v in mt if v>=0}; visL=set(); visR=set()
    st=[v for v in range(left) if v not in matched]
    while st:
        v=st.pop()
        if v in visL: continue
        visL.add(v)
        for u in g[v]:
            if u not in visR and mt[u]!=v: visR.add(u); st.append(mt[u]) if mt[u]>=0 else None
    return ([v for v in range(left) if v in visL],
            [u for u in range(right) if u not in visR])

def hungarian(a):
    """概要:
        Hungarian 法で最小コスト完全割当を求める。
    入力:
        a (list[list[int]]): 行数 n が列数 m 以下の n×m コスト行列。
    出力:
        tuple[int, list[int]]: 最小費用と、各行に割り当てた列番号。
    計算量:
        時間 O(n^2 m)、空間 O(n+m)。
    補足:
        負のコスト、n=0 に対応する。長方形で n<=m が必要。
    """
    n=len(a)
    if not n: return 0,[]
    m=len(a[0]); u=[0]*(n+1); v=[0]*(m+1); p=[0]*(m+1); way=[0]*(m+1)
    if m < n or any(len(row) != m for row in a):
        raise ValueError("Hungarian requires a rectangular matrix with rows <= columns")
    for i in range(1,n+1):
        p[0]=i; j0=0; mn=[INF]*(m+1); used=[False]*(m+1)
        while True:
            used[j0]=True; i0=p[j0]; delta=INF; j1=0
            for j in range(1,m+1):
                if not used[j]:
                    cur=a[i0-1][j-1]-u[i0]-v[j]
                    if cur<mn[j]: mn[j]=cur; way[j]=j0
                    if mn[j]<delta: delta=mn[j]; j1=j
            for j in range(m+1):
                if used[j]: u[p[j]]+=delta; v[j]-=delta
                else: mn[j]-=delta
            j0=j1
            if p[j0]==0: break
        while True:
            j1=way[j0]; p[j0]=p[j1]; j0=j1
            if j0==0: break
    ass=[0]*n
    for j in range(1,m+1):
        if p[j]: ass[p[j]-1]=j-1
    return -v[0],ass

# ============================================================
# 木アルゴリズム
# ============================================================

def _validate_tree_input(g: list[list[int]], root: int = 0) -> None:
    """木アルゴリズム共通の空グラフ・根・連結性を検証する。"""
    n = len(g)
    if n == 0 or not (0 <= root < n):
        raise ValueError("requires a non-empty graph and a valid root")
    visited = [False] * n
    visited[root] = True
    q = deque([root])
    count = 0
    while q:
        v = q.popleft()
        count += 1
        for to in g[v]:
            if not (0 <= to < n):
                raise ValueError("tree edge contains an invalid vertex")
            if not visited[to]:
                visited[to] = True
                q.append(to)
    if count != n:
        raise ValueError("tree graph must be connected")

def tree_diameter(g: list[list[int]]) -> tuple[int, int, int]:
    """概要:
        木の直径長とその端点2つを返す。
    入力:
        g (list[list[int]]): 木の隣接リスト。
    出力:
        tuple[int, int, int]: (直径長, 端点u, 端点v)。
    補足:
        BFS を2回行う定番手法を用いる。計算量は O(V)。
    """
    _validate_tree_input(g)

    def bfs_farthest(s: int) -> tuple[int, int]:
        dist = bfs(g, s)
        farthest = max(range(len(g)), key=lambda x: dist[x])
        return farthest, dist[farthest]

    u, _ = bfs_farthest(0)
    v, d = bfs_farthest(u)
    return d, u, v

def tree_depth(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根 root からの深さ（距離）を返す。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: 各頂点の深さ配列。
    補足:
        実装は `bfs` を利用している。計算量は O(V)。
    """
    _validate_tree_input(g, root)
    return bfs(g, root)

def tree_parent(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木における各頂点の親配列を構築する。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: parent[v]（根は -1）。
    補足:
        BFS で訪問順に親を設定する。計算量は O(V)。
    """
    _validate_tree_input(g, root)
    n = len(g)
    parent = [-1] * n
    visited = [False] * n
    visited[root] = True
    q = deque([root])
    while q:
        v = q.popleft()
        for to in g[v]:
            if not visited[to]:
                visited[to] = True
                parent[to] = v
                q.append(to)
    return parent

def subtree_size(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木の各頂点について部分木サイズを求める。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: size[v] = v を根とする部分木サイズ。
    補足:
        深い頂点から親へサイズを集約する。計算量は O(V)。
    """
    _validate_tree_input(g, root)
    n = len(g)
    size = [1] * n
    parent = [-1] * n
    order = [root]
    q = deque([root])
    while q:
        v = q.popleft()
        for to in g[v]:
            if to == root or parent[to] != -1:
                continue
            parent[to] = v
            order.append(to)
            q.append(to)
    order.reverse()
    for v in order:
        if parent[v] != -1:
            size[parent[v]] += size[v]
    return size

def subtree_height(g: list[list[int]], root: int = 0) -> list[int]:
    """概要:
        根付き木の各頂点について部分木の高さ（階級）を求める。
    入力:
        g (list[list[int]]): 木の隣接リスト。
        root (int): 根頂点。
    出力:
        list[int]: height[v] = v を根とする部分木の高さ。
                   葉は 0、それ以外は直属の子の高さの最大値 + 1。
    補足:
        深い頂点から親へ max(子の高さ) + 1 を伝播する。計算量は O(V)。
    """
    _validate_tree_input(g, root)
    n = len(g)
    height = [0] * n
    parent = [-1] * n
    order = [root]
    q = deque([root])
    while q:
        v = q.popleft()
        for to in g[v]:
            if to == root or parent[to] != -1:
                continue
            parent[to] = v
            order.append(to)
            q.append(to)
    order.reverse()
    for v in order:
        if parent[v] != -1:
            height[parent[v]] = max(height[parent[v]], height[v] + 1)
    return height

class LCA:
    """概要:
        ダブリング法で LCA（最小共通祖先）と頂点間距離を高速計算するクラス。

    メソッド:
        query(u, v): u と v の LCA を返す。
        dist(u, v): u-v 間の辺数距離を返す。

    計算量:
        初期化は O(NlogN)、query と dist は O(logN)。

    補足:
        初期化時に BFS と親テーブル構築を行い、クエリは O(logN)。

    使用例:
        lca = LCA(g, root=0)
        print(lca.query(u, v))
        print(lca.dist(u, v))
    """
    def __init__(self, g: list[list[int]], root: int = 0):
        _validate_tree_input(g, root)
        self.n = len(g)
        self.log = max(1, (self.n - 1).bit_length())
        self.depth = [-1] * self.n
        self.parent = [[-1] * self.n for _ in range(self.log)]

        # BFSで深さと親を計算
        self.depth[root] = 0
        q = deque([root])
        while q:
            v = q.popleft()
            for to in g[v]:
                if self.depth[to] == -1:
                    self.depth[to] = self.depth[v] + 1
                    self.parent[0][to] = v
                    q.append(to)

        # ダブリングテーブル構築
        for k in range(1, self.log):
            for v in range(self.n):
                if self.parent[k-1][v] != -1:
                    self.parent[k][v] = self.parent[k-1][self.parent[k-1][v]]

    def query(self, u: int, v: int) -> int:
        """u, v のLCAを返す"""
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        # 深さを揃える
        diff = self.depth[v] - self.depth[u]
        for k in range(self.log):
            if (diff >> k) & 1:
                v = self.parent[k][v]
        if u == v: return u
        # 二分探索でLCAを求める
        for k in range(self.log - 1, -1, -1):
            if self.parent[k][u] != self.parent[k][v]:
                u = self.parent[k][u]
                v = self.parent[k][v]
        return self.parent[0][u]

    def dist(self, u: int, v: int) -> int:
        """u-v間の距離"""
        return self.depth[u] + self.depth[v] - 2 * self.depth[self.query(u, v)]

def euler_tour(n, g, root=0):
    """概要:
        木を DFS して Euler tour 順序と部分木区間を作る。
    入力:
        n (int): 頂点数。g: 頂点または (頂点,重み) の隣接リスト。
        root (int): 根。n=0 も許す。
    出力:
        (order, tin, tout, parent, depth)。部分木は [tin[v], tout[v])。
    計算量:
        時間 O(n)、空間 O(n)。
    補足:
        木でない場合は root から到達できる連結成分だけを処理する。
    使用例:
        order, tin, tout, parent, depth = euler_tour(n, g)
    """
    order=[]; tin=[-1]*n; tout=[-1]*n; par=[-1]*n; dep=[0]*n
    if not n: return order,tin,tout,par,dep
    st=[(root,-1,0)]; seen={root}
    while st:
        v,p,i=st[-1]
        if i==0: tin[v]=len(order); order.append(v)
        if i<len(g[v]):
            z=g[v][i]; to=z[0] if isinstance(z,tuple) else z
            st[-1]=(v,p,i+1)
            if to==p or to in seen: continue
            seen.add(to); par[to]=v; dep[to]=dep[v]+1; st.append((to,v,0))
        else: tout[v]=len(order); st.pop()
    return order,tin,tout,par,dep

class HLD:
    """概要:
        木の Heavy-Light Decomposition を構築する。
    入力:
        HLD(n, edges, root) の edges は木の辺、root は根。
    出力:
        path(u,v) は頂点区間 [l,r) の列、subtree(v) は部分木区間を返す。
    計算量:
        構築 O(n)、path/subtree O(log n) 以下、空間 O(n)。
    補足:
        配列を pos 順に並べ、値は頂点に対応させる。
    """
    def __init__(self,n,edges,root=0):
        if n == 0:
            self.n=0; self.g=[]; self.parent=[]; self.depth=[]; self.size=[]
            self.heavy=[]; self.head=[]; self.pos=[]; self.rev=[]; return
        if not 0 <= root < n: raise ValueError("root is out of range")
        if len(edges) != n - 1: raise ValueError("HLD requires a tree")
        self.n=n; self.g=[[] for _ in range(n)]
        for a,b in edges: self.g[a].append(b); self.g[b].append(a)
        self.parent=[-1]*n; self.depth=[0]*n; self.size=[1]*n
        self.heavy=[-1]*n; order=[root]; self.parent[root]=-2
        for v in order:
            for to in self.g[v]:
                if self.parent[to]==-1: self.parent[to]=v; self.depth[to]=self.depth[v]+1; order.append(to)
        for v in order[::-1]:
            if self.parent[v]>=0:
                p=self.parent[v]; self.size[p]+=self.size[v]
                if self.heavy[p]<0 or self.size[v]>self.size[self.heavy[p]]: self.heavy[p]=v
        self.head=[0]*n; self.pos=[0]*n; self.rev=[]; q=[root]
        while q:
            h=q.pop(); v=h
            while v!=-1:
                self.head[v]=h; self.pos[v]=len(self.rev); self.rev.append(v)
                q.extend(to for to in self.g[v] if self.parent[to]==v and to!=self.heavy[v])
                v=self.heavy[v]
        if len(self.rev) != n: raise ValueError("HLD requires a connected tree")
    def path(self,u,v):
        if not self.n: return []
        if not (0 <= u < self.n and 0 <= v < self.n): raise IndexError("vertex index")
        out=[]
        while self.head[u]!=self.head[v]:
            if self.depth[self.head[u]]<self.depth[self.head[v]]: u,v=v,u
            out.append((self.pos[self.head[u]],self.pos[u]+1)); u=self.parent[self.head[u]]
        a,b=sorted((self.pos[u],self.pos[v])); out.append((a,b+1)); return out
    def subtree(self,v):
        if not 0 <= v < self.n: raise IndexError("vertex index")
        return self.pos[v], self.pos[v]+self.size[v]

def rerooting_dp(n, g, merge, add_root, identity=0, root=0):
    """概要:
        全頂点を根とした木 DP（全方位木 DP）を計算する。
    入力:
        g は隣接頂点または (頂点, 辺情報) のリスト。merge は値の統合、
        add_root(value, edge) は辺を越える変換、identity は単位元。
    出力:
        list: 各頂点を根にした DP 値。
    計算量:
        時間 O(n)、空間 O(n)。
    補足:
        merge は可換でなくてもよい。空木では [] を返す。
    """
    if n == 0: return []
    if len(g) != n or not 0 <= root < n: raise ValueError("invalid tree")
    parent=[-1]*n; pedge=[None]*n; order=[root]; parent[root]=-2
    for v in order:
        for e in g[v]:
            to, data=(e if isinstance(e,tuple) else (e,None))
            if not 0 <= to < n: raise ValueError("invalid endpoint")
            if to == parent[v]: continue
            if parent[to] != -1: raise ValueError("g must be a tree")
            parent[to]=v; pedge[to]=data; order.append(to)
    if len(order) != n: raise ValueError("g must be connected")
    down=[identity]*n
    for v in order[::-1]:
        x=identity
        for e in g[v]:
            to,data=(e if isinstance(e,tuple) else (e,None))
            if parent[to]==v: x=merge(x,add_root(down[to],data))
        down[v]=x
    ans=[identity]*n; up=[identity]*n
    for v in order:
        vals=[]
        for e in g[v]:
            to,data=(e if isinstance(e,tuple) else (e,None))
            vals.append((to,add_root(down[to] if parent[to]==v else up[v],data)))
        pref=[identity]
        for _,x in vals: pref.append(merge(pref[-1],x))
        suf=[identity]*(len(vals)+1)
        for i in range(len(vals)-1,-1,-1): suf[i]=merge(vals[i][1],suf[i+1])
        ans[v]=pref[-1]
        for i,(to,_) in enumerate(vals):
            if parent[to]==v: up[to]=merge(pref[i],suf[i+1])
    return ans

# ============================================================
# データ構造
# ============================================================

from typing import List, Sequence, Union
class BIT:
    """概要:
        1次元 Binary Indexed Tree（Fenwick Tree）を提供するクラス。

    メソッド:
        build(a): 配列 a から O(N) で木を再構築する。
        add(i, x): a[i] に x を加算する。
        sum(i): 区間 [0, i] の和を返す。
        range_sum(l, r): 区間 [l, r) の和を返す。
        lower_bound(w): 累積和が w 以上になる最小インデックスを返す (各要素が非負の場合)。

    補足:
        すべて 0-indexed インターフェース。
        初期化および build は O(N)。
        add, sum, range_sum, lower_bound は O(log N)。
    """
    def __init__(self, arg: Union[int, Sequence[int]]):
        """
        引数に整数 n を渡した場合は要素数 n (初期値 0) で初期化する。
        引数に配列などのシーケンスを渡した場合は、その要素で O(N) で初期化する。
        """
        if isinstance(arg, int):
            self.n = arg
            self.data = [0] * (self.n + 1)
        else:
            self.n = len(arg)
            self.data = [0] * (self.n + 1)
            self.build(arg)

    def build(self, a: Sequence[int]) -> None:
        """与えられたシーケンス a に基づいて O(N) で木を構築する。"""
        self.n = len(a)
        # 1-indexed に合わせるため先頭に 0 を配置
        self.data = [0] + list(a)
        for i in range(1, self.n + 1):
            parent = i + (i & -i)
            if parent <= self.n:
                self.data[parent] += self.data[i]

    def add(self, i: int, x: int) -> None:
        """a[i] に x を加算する (0-indexed)。"""
        i += 1
        while i <= self.n:
            self.data[i] += x
            i += i & -i

    def sum(self, i: int) -> int:
        """区間 [0, i] の総和 (a[0] + ... + a[i]) を返す (0-indexed)。"""
        s = 0
        i += 1
        while i > 0:
            s += self.data[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        """区間 [l, r) の総和 (a[l] + ... + a[r-1]) を返す (0-indexed)。"""
        if l >= r:
            return 0
        return self.sum(r - 1) - (self.sum(l - 1) if l > 0 else 0)

    def lower_bound(self, w: int) -> int:
        """累積和が w 以上になる最小のインデックスを返す (0-indexed)。
        ※配列の全要素が非負であることが前提条件。
        """
        if w <= 0:
            return 0
        if self.n == 0:
            return 0
        x, k = 0, 1 << (self.n.bit_length() - 1)
        while k > 0:
            if x + k <= self.n and self.data[x + k] < w:
                w -= self.data[x + k]
                x += k
            k //= 2
        return x


from collections.abc import Callable, Sequence
from typing import Any
import operator
class SegTree:
    """概要:
        モノイド演算を扱う汎用 Segment Tree。

    メソッド:
        build(arr): 初期配列から構築する。
        set(i, v) / update(i, v): 1点更新を行う。
        get(i): 1点取得を行う。
        query(l, r): 区間 [l, r) の集約値を返す。
        max_right(l, f): [l, r) の集約が条件 f を満たす最大の r を返す。
        min_left(r, f): [l, r) の集約が条件 f を満たす最小の l を返す。
        all_query(): 全区間の集約値を返す。

    計算量:
        初期化(配列指定)/build は O(N)、set/update/get/query/max_right/min_left は O(logN)、all_query は O(1)。

    補足:
        `op` は結合的、`e` は単位元を与える。

    使用例:
        # 配列から初期化
        arr = [1, 2, 3, 4, 5]
        st = SegTree(arr, op=operator.add, e=0)

        # 要素数から初期化
        st = SegTree(5, op=min, e=float("inf"))
    """

    def __init__(
        self,
        n_or_arr: int | Sequence[Any],
        op: Callable[[Any, Any], Any] = operator.add,
        e: Any = 0,
    ):
        self.op = op
        self.e = e

        if isinstance(n_or_arr, int):
            self.n = n_or_arr
            self.size = 1
            while self.size < self.n:
                self.size <<= 1
            self.data = [e] * (2 * self.size)
        else:
            self.n = len(n_or_arr)
            self.size = 1
            while self.size < self.n:
                self.size <<= 1
            self.data = [e] * (2 * self.size)
            self.build(n_or_arr)

    def build(self, arr: Sequence[Any]) -> None:
        """初期配列から構築する (O(N))"""
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def set(self, i: int, v: Any) -> None:
        """a[i] = v"""
        i += self.size
        self.data[i] = v
        while i > 1:
            i >>= 1
            self.data[i] = self.op(self.data[i << 1], self.data[i << 1 | 1])

    def get(self, i: int) -> Any:
        """a[i]を取得"""
        return self.data[self.size + i]

    def query(self, l: int, r: int) -> Any:
        """[l, r) の演算結果"""
        sml = self.e
        smr = self.e
        l += self.size
        r += self.size
        while l < r:
            if l & 1:
                sml = self.op(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op(sml, smr)

    def max_right(self, l: int, f: Callable[[Any], bool]) -> int:
        """最大の r を返す（f(query(l, r)) が True）"""
        if l == self.n:
            return self.n
        assert 0 <= l <= self.n
        assert f(self.e)

        l += self.size
        sm = self.e
        while True:
            while l % 2 == 0:
                l >>= 1
            nxt = self.op(sm, self.data[l])
            if not f(nxt):
                while l < self.size:
                    l <<= 1
                    nxt = self.op(sm, self.data[l])
                    if f(nxt):
                        sm = nxt
                        l += 1
                return l - self.size
            sm = nxt
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r: int, f: Callable[[Any], bool]) -> int:
        """最小の l を返す（f(query(l, r)) が True）"""
        if r == 0:
            return 0
        assert 0 <= r <= self.n
        assert f(self.e)

        r += self.size
        sm = self.e
        while True:
            r -= 1
            while r > 1 and r % 2:
                r >>= 1
            nxt = self.op(self.data[r], sm)
            if not f(nxt):
                while r < self.size:
                    r = (r << 1) | 1
                    nxt = self.op(self.data[r], sm)
                    if f(nxt):
                        sm = nxt
                        r -= 1
                return r + 1 - self.size
            sm = nxt
            if (r & -r) == r:
                break
        return 0

    def all_query(self) -> Any:
        """全区間の演算結果"""
        return self.data[1]

    update = set  # エイリアス


from collections.abc import Callable, Sequence
from typing import Any
import operator
class LazySegTree:
    """概要:
        作用付きモノイドを扱う汎用遅延セグメント木。

    メソッド:
        build(arr): 初期配列から木を構築する。
        set(p, x): 1点代入を行う。
        get(p): 1点値を取得する（必要な遅延伝播込み）。
        query(l, r): 区間 [l, r) の集約値を返す。
        all_query(): 全区間の集約値を返す。
        apply(l, r, f): 区間 [l, r) に作用 f を適用する。
        max_right(l, g): [l, r) の集約値が条件 g を満たす最大の r を返す (O(logN))。
        min_left(r, g): [l, r) の集約値が条件 g を満たす最小の l を返す (O(logN))。

    計算量:
        build は O(N)、
        set/get/query/apply/max_right/min_left は O(logN)、
        all_query は O(1)。
    """

    def __init__(
        self,
        n_or_arr: int | Sequence[Any],
        op: Callable,
        e: Any,
        mapping: Callable,
        composition: Callable,
        identity: Any,
    ):
        self.op = op
        self.e = e
        self.mapping = mapping
        self.composition = composition
        self.identity = identity

        if isinstance(n_or_arr, int):
            self.n = n_or_arr
            self.log = max(1, (self.n - 1).bit_length())
            self.size = 1 << self.log
            self.data = [e] * (2 * self.size)
            self.lazy = [identity] * self.size
        else:
            self.n = len(n_or_arr)
            self.log = max(1, (self.n - 1).bit_length())
            self.size = 1 << self.log
            self.data = [e] * (2 * self.size)
            self.lazy = [identity] * self.size
            self.build(n_or_arr)

    def build(self, arr: Sequence[Any]) -> None:
        """初期配列から木を構築する (O(N))"""
        for i, v in enumerate(arr):
            self.data[self.size + i] = v
        for i in range(self.size - 1, 0, -1):
            self._update(i)

    def _update(self, k: int) -> None:
        self.data[k] = self.op(self.data[k << 1], self.data[k << 1 | 1])

    def _all_apply(self, k: int, f: Any) -> None:
        self.data[k] = self.mapping(f, self.data[k])
        if k < self.size:
            self.lazy[k] = self.composition(f, self.lazy[k])

    def _push(self, k: int) -> None:
        if self.lazy[k] != self.identity:
            self._all_apply(k << 1, self.lazy[k])
            self._all_apply(k << 1 | 1, self.lazy[k])
            self.lazy[k] = self.identity

    def set(self, p: int, x: Any) -> None:
        p += self.size
        for i in range(self.log, 0, -1):
            self._push(p >> i)
        self.data[p] = x
        for i in range(1, self.log + 1):
            self._update(p >> i)

    def get(self, p: int) -> Any:
        p += self.size
        for i in range(self.log, 0, -1):
            self._push(p >> i)
        return self.data[p]

    def query(self, l: int, r: int) -> Any:
        """[l, r) の演算結果"""
        if l >= r:
            return self.e
        l += self.size
        r += self.size
        for i in range(self.log, 0, -1):
            if ((l >> i) << i) != l:
                self._push(l >> i)
            if ((r >> i) << i) != r:
                self._push((r - 1) >> i)
        sml = self.e
        smr = self.e
        while l < r:
            if l & 1:
                sml = self.op(sml, self.data[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self.op(self.data[r], smr)
            l >>= 1
            r >>= 1
        return self.op(sml, smr)

    def all_query(self) -> Any:
        """全区間の演算結果"""
        return self.data[1]

    def apply(self, l: int, r: int, f: Any) -> None:
        """[l, r) に作用fを適用"""
        if l >= r:
            return
        l += self.size
        r += self.size
        l2, r2 = l, r
        for i in range(self.log, 0, -1):
            if ((l2 >> i) << i) != l2:
                self._push(l2 >> i)
            if ((r2 >> i) << i) != r2:
                self._push((r2 - 1) >> i)
        while l < r:
            if l & 1:
                self._all_apply(l, f)
                l += 1
            if r & 1:
                r -= 1
                self._all_apply(r, f)
            l >>= 1
            r >>= 1
        l, r = l2, r2
        for i in range(1, self.log + 1):
            if ((l >> i) << i) != l:
                self._update(l >> i)
            if ((r >> i) << i) != r:
                self._update((r - 1) >> i)

    def max_right(self, l: int, g: Callable[[Any], bool]) -> int:
        """最大の r を返す（g(query(l, r)) が True となる最大の r）"""
        assert 0 <= l <= self.n
        assert g(self.e)
        if l == self.n:
            return self.n

        l += self.size
        for i in range(self.log, 0, -1):
            self._push(l >> i)

        sm = self.e
        while True:
            while l % 2 == 0:
                l >>= 1
            if not g(self.op(sm, self.data[l])):
                while l < self.size:
                    self._push(l)
                    l <<= 1
                    if g(self.op(sm, self.data[l])):
                        sm = self.op(sm, self.data[l])
                        l += 1
                return l - self.size
            sm = self.op(sm, self.data[l])
            l += 1
            if (l & -l) == l:
                break
        return self.n

    def min_left(self, r: int, g: Callable[[Any], bool]) -> int:
        """最小の l を返す（g(query(l, r)) が True となる最小の l）"""
        assert 0 <= r <= self.n
        assert g(self.e)
        if r == 0:
            return 0

        r += self.size
        for i in range(self.log, 0, -1):
            self._push((r - 1) >> i)

        sm = self.e
        while True:
            r -= 1
            while r > 1 and (r % 2):
                r >>= 1
            if not g(self.op(self.data[r], sm)):
                while r < self.size:
                    self._push(r)
                    r = (r << 1) | 1
                    if g(self.op(self.data[r], sm)):
                        sm = self.op(self.data[r], sm)
                        r -= 1
                return r + 1 - self.size
            sm = self.op(self.data[r], sm)
            if (r & -r) == r:
                break
        return 0


class BIT2:
    """概要:
        BITを2本使って「区間加算・区間和」を処理するクラス。

    メソッド:
        add_range(l, r, x): 区間 [l, r) へ x を加算する。
        range_sum(l, r): 区間 [l, r) の総和を返す。

    補足:
        内部的に一次関数係数を2本のBITで管理し、各操作 O(logN)。

    使用例:
        bit2 = BIT2(n)
        bit2.add_range(l, r, x)  # [l, r) に +x
        total = bit2.range_sum(l, r)
    """
    def __init__(self, n: int):
        self.n = n
        self.bit1 = [0] * (n + 1)
        self.bit2 = [0] * (n + 1)

    def _add(self, bit: list[int], i: int, x: int) -> None:
        while i <= self.n:
            bit[i] += x
            i += i & -i

    def _sum(self, bit: list[int], i: int) -> int:
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s

    def _prefix_sum(self, r: int) -> int:
        """[0, r) の和"""
        return self._sum(self.bit1, r) * r + self._sum(self.bit2, r)

    def add_range(self, l: int, r: int, x: int) -> None:
        """[l, r) に x を加算"""
        l += 1
        r += 1
        self._add(self.bit1, l, x)
        self._add(self.bit1, r, -x)
        self._add(self.bit2, l, -x * (l - 1))
        self._add(self.bit2, r, x * (r - 1))

    def range_sum(self, l: int, r: int) -> int:
        """[l, r) の和"""
        return self._prefix_sum(r) - self._prefix_sum(l)


class BIT2D:
    """概要:
        2次元 Binary Indexed Tree（2D Fenwick Tree）を提供するクラス。

    メソッド:
        add(y, x, v): 1点 (y, x) に v を加算する。
        range_sum(y1, x1, y2, x2): 矩形 [y1,y2)×[x1,x2) の和を返す。

    補足:
        各操作は O(logH * logW)。0-indexed の半開区間で扱う。

    使用例:
        bit = BIT2D(H, W)
        bit.add(y, x, v)                  # A[y][x] += v
        s = bit.range_sum(y1, x1, y2, x2) # [y1,y2) × [x1,x2)
    """
    def __init__(self, h: int, w: int):
        self.h = h
        self.w = w
        self.data = [[0] * (w + 1) for _ in range(h + 1)]

    def add(self, y: int, x: int, v: int) -> None:
        y += 1
        while y <= self.h:
            xx = x + 1
            while xx <= self.w:
                self.data[y][xx] += v
                xx += xx & -xx
            y += y & -y

    def _sum(self, y: int, x: int) -> int:
        """[0, y) × [0, x) の和"""
        s = 0
        yy = y
        while yy > 0:
            xx = x
            while xx > 0:
                s += self.data[yy][xx]
                xx -= xx & -xx
            yy -= yy & -yy
        return s

    def range_sum(self, y1: int, x1: int, y2: int, x2: int) -> int:
        """[y1, y2) × [x1, x2) の和"""
        return self._sum(y2, x2) - self._sum(y1, x2) - self._sum(y2, x1) + self._sum(y1, x1)


# https://github.com/tatyam-prime/SortedSet/blob/main/BucketList.py
# T->_T, 補足や計算量など
import math
from typing import Generic, Iterable, Iterator, TypeVar
_T = TypeVar('_T')
class BucketList(Generic[_T]):
    """概要:
        バケット分割で高速に任意の場所に挿入と削除を行えるデータ構造
    計算量:
        初期化(__init__): O(N)
        長さ取得(__len__): O(1)
        参照(__getitem__): O(√N)  ※末尾近く(i = -1 など)は O(1)
        挿入(insert): O(√N)
        末尾追加(append): ならし O(1)
        一括追加(extend): ならし O(K)  ※K は追加する要素数
        削除(pop): O(√N)  ※末尾削除(i = -1)は O(1)
        要素の存在判定(in, __contains__): O(N)
        要素の出現回数(count): O(N)
        要素の検索(index): O(N)
        要素の削除(remove): O(N)
        全走査(__iter__, __reversed__): O(N)
        反転(reverse): O(N)
        比較(__eq__): O(N)
        複製(copy): O(N)
        文字列表現(__repr__, __str__): O(N)
        全消去(clear): O(1)
    """
    
    BUCKET_RATIO = 16
    SPLIT_RATIO = 24
    
    def __init__(self, a: Iterable[_T] = []) -> None:
        a = list(a)
        n = self.size = len(a)
        num_bucket = int(math.ceil(math.sqrt(n / self.BUCKET_RATIO)))
        self.a = [a[n * i // num_bucket : n * (i + 1) // num_bucket] for i in range(num_bucket)]
    def __iter__(self) -> Iterator[_T]:
        for i in self.a:
            for j in i: yield j
    def __reversed__(self) -> Iterator[_T]:
        for i in reversed(self.a):
            for j in reversed(i): yield j
    
    def __eq__(self, other) -> bool:
        if len(self) != len(other): return False
        for x, y in zip(self, other):
            if x != y: return False
        return True
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return "BucketList" + str(self.a)
    
    def __str__(self) -> str:
        return str(list(self))
    def __contains__(self, x: _T) -> bool:
        "Return True if x is in the bucket list. / O(N)"
        for y in self:
            if x == y: return True
        return False
    
    def _insert(self, a: list[_T], b: int, i: int, x: _T) -> None:
        a.insert(i, x)
        self.size += 1
        if len(a) > len(self.a) * self.SPLIT_RATIO:
            mid = len(a) >> 1
            self.a[b:b+1] = [a[:mid], a[mid:]]
    def insert(self, i: int, x: _T) -> None:
        "Insert x at the i-th position. / O(√N)"
        if self.size == 0:
            if i != 0 and i != -1: raise IndexError
            self.a = [[x]]
            self.size = 1
            return
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0: return self._insert(a, len(self.a) + ~b, i, x)
        else:
            for b, a in enumerate(self.a):
                if i <= len(a): return self._insert(a, b, i, x)
                i -= len(a)
        raise IndexError
    def append(self, x: _T) -> None:
        "Append x to the end of the list. / amortized O(1)"
        if self.size == 0:
            self.a = [[x]]
            self.size = 1
            return
        a = self.a[-1]
        return self._insert(a, len(self.a) - 1, len(a), x)
    
    def extend(self, a: Iterable[_T]) -> None:
        for x in a: self.append(x)
    
    def __getitem__(self, i: int) -> _T:
        if i < 0:
            for a in reversed(self.a):
                i += len(a)
                if i >= 0: return a[i]
        else:
            for a in self.a:
                if i < len(a): return a[i]
                i -= len(a)
        raise IndexError
    
    def _pop(self, a: list[_T], b: int, i: int) -> _T:
        ans = a.pop(i)
        self.size -= 1
        if not a: del self.a[b]
        return ans
    
    def pop(self, i: int = -1) -> _T:
        "Remove and return the i-th element. / O(√N) / O(-i) if i < 0"
        if i < 0:
            for b, a in enumerate(reversed(self.a)):
                i += len(a)
                if i >= 0: return self._pop(a, ~b, i)
        else:
            for b, a in enumerate(self.a):
                if i < len(a): return self._pop(a, b, i)
                i -= len(a)
        raise IndexError
    def count(self, x: _T) -> int:
        "Return the number of occurrences of x. / O(N)"
        return sum(1 for y in self if x == y)
    def index(self, x: _T) -> int:
        "Return the index of the first occurrence of x, raise ValueError if not found. / O(N)"
        for i, y in enumerate(self):
            if x == y: return i
        raise ValueError
    
    def remove(self, x: _T) -> None:
        "Remove the first occurrence of x, raise ValueError if not found. / O(N)"
        self.pop(self.index(x))
    def clear(self) -> None:
        self.a = []
        self.size = 0
    def reverse(self) -> None:
        self.a.reverse()
        for a in self.a: a.reverse()
    def copy(self) -> 'BucketList[_T]':
        return BucketList(self)

class Mo:
    """概要:
        Mo's Algorithm（オフライン区間クエリ高速処理）クラス。
        区間 [l, r) に対するクエリをまとめて O((N+Q)√N) で処理する。

    使い方:
        1. Mo(n, queries) でインスタンス化（queries は (l, r) のリスト）
        2. add_left / add_right / remove_left / remove_right を実装して渡すか、
           外部変数を使うクロージャで定義する。
        3. mo.run(add_left, add_right, remove_left, remove_right, query_func)
           を呼ぶと、クエリ順に query_func の結果が返る。

    計算量:
        区間移動を M 回、各コールバックのコストを C とすると、
        _order は O(Q log N + Q log Q)、run 全体は O(Q log N + Q log Q + M C)。
        ブロック順を採用する通常の Mo では M = O((N + Q)√N) と評価できる。

    制約:
        オフライン処理のみ（クエリを事前に全部受け取れる場合のみ使用可能）。
        追加・削除が逆操作可能な場合にのみ正確に動く。

    使用例:
        # 区間内の異なる要素数を数える例
        from collections import defaultdict
        cnt = defaultdict(int)
        distinct = [0]

        def add(i):
            if cnt[A[i]] == 0:
                distinct[0] += 1
            cnt[A[i]] += 1

        def remove(i):
            cnt[A[i]] -= 1
            if cnt[A[i]] == 0:
                distinct[0] -= 1

        mo = Mo(N, queries)
        answers = mo.run(add, add, remove, remove, lambda: distinct[0])
    """

    def __init__(self, n: int, queries: list[tuple[int, int]], order: str = "block"):
        """
        入力:
            n (int): 配列長
            queries (list[tuple[int, int]]): (l, r) のクエリリスト（半開区間 [l, r)）
            order (str): クエリ順。"block" または "hilbert"。
        """
        if order not in ("block", "hilbert"):
            raise ValueError("order must be 'block' or 'hilbert'")
        self.n = n
        self.queries = queries
        self.q = len(queries)
        self.block = max(1, int(n ** 0.5))
        self.order = order

    def _order(self) -> list[int]:
        """ヒルベルト曲線順でクエリをソートしたインデックスを返す（定数倍改善）"""
        if self.order == "block":
            return sorted(
                range(self.q),
                key=lambda i: (
                    self.queries[i][0] // self.block,
                    self.queries[i][1]
                    if (self.queries[i][0] // self.block) % 2 == 0
                    else -self.queries[i][1],
                ),
            )

        def hilbert_order(x: int, y: int, pow_: int, rotate: int) -> int:
            if pow_ == 0:
                return 0
            half = 1 << (pow_ - 1)
            rx = 1 if (x & half) else 0
            ry = 1 if (y & half) else 0
            result = hilbert_order(
                x if ry == 1 else (half - 1 - x if rx == 1 else x),
                y if ry == 1 else (half - 1 - y if rx == 1 else y),
                pow_ - 1,
                (rotate + 2 * (1 - rx) * (1 - ry) + 3 * rx * (1 - ry) + rx * ry) % 4
            )
            if rx == 1:
                x, y = half - 1 - y, half - 1 - x
            elif ry == 0:
                x, y = half - 1 - x, half - 1 - y
            if rx == 0 and ry == 0:
                x, y = y, x
            return result + half * half * (rx + 2 * ry)

        # ヒルベルト順が重い場合は通常のブロックソートに切り替え可
        # return sorted(range(self.q), key=lambda i: (
        #     self.queries[i][0] // self.block,
        #     self.queries[i][1] if (self.queries[i][0] // self.block) % 2 == 0 else -self.queries[i][1]
        # ))

        LOG = max(1, self.n.bit_length())
        return sorted(
            range(self.q),
            key=lambda i: hilbert_order(self.queries[i][0], self.queries[i][1], LOG, 0)
        )

    def run(
        self,
        add_left,    # add_left(i)  : 区間左端に index i を追加
        add_right,   # add_right(i) : 区間右端に index i を追加
        rem_left,    # rem_left(i)  : 区間左端から index i を削除
        rem_right,   # rem_right(i) : 区間右端から index i を削除
        query_func,  # query_func() : 現在の区間の答えを返す
    ) -> list:
        """
        概要:
            クエリをソート順に処理し、各クエリの答えをリストで返す。
        入力:
            add_left(i)   : 左端を1つ広げるとき（l を l-1 に）呼ばれる
            add_right(i)  : 右端を1つ広げるとき（r を r+1 に）呼ばれる
            rem_left(i)   : 左端を1つ縮めるとき（l を l+1 に）呼ばれる
            rem_right(i)  : 右端を1つ縮めるとき（r を r-1 に）呼ばれる
            query_func()  : 現在の区間 [cur_l, cur_r) の答えを返す
        出力:
            list: answers[i] = i番目のクエリの答え
        補足:
            [l, r) の半開区間で管理。
            cur_r は「現在含まれている最大インデックス + 1」。
        """
        order = self._order()
        answers = [None] * self.q

        cur_l, cur_r = 0, 0  # 現在の区間 [cur_l, cur_r)（初期は空）

        for qi in order:
            l, r = self.queries[qi]
            # r を広げる（右端を追加）
            while cur_r < r:
                add_right(cur_r)
                cur_r += 1
            # l を狭める（左端を削除）
            while cur_l > l:
                cur_l -= 1
                add_left(cur_l)
            # r を縮める（右端を削除）
            while cur_r > r:
                cur_r -= 1
                rem_right(cur_r)
            # l を広げる（左端を削除）
            while cur_l < l:
                rem_left(cur_l)
                cur_l += 1

            answers[qi] = query_func()

        return answers

class ImplicitTreap:
    """概要:
    配列のように振る舞い、強力な区間操作や検索をO(log N)で処理する拡張版の平衡二分探索木（Treap）。
    PyPyでの高速化のため、全てのノード情報を1次元配列で管理。区間加算・反転の遅延評価に対応。

    メソッド:
    - build(arr): 配列からO(N log N)で初期木を構築する。
    - insert(index, value): 指定したインデックスに要素を挿入する。
    - erase(index): 指定したインデックスの要素を削除する。
    - pop(index): 指定したインデックスの要素を削除し、その値を返す（デフォルトは末尾）。
    - pop_max(): 配列内の最大値を検索して削除し、その値を返す。
    - update(index, value): 指定したインデックスの要素の値をvalueに更新する。
    - add_val(l, r, value): 区間 [l, r) の全ての要素に value を加算する。
    - query(l, r): 区間 [l, r) の (和, 最小値, 最大値) のタプルを返す。
    - reverse(l, r): 区間 [l, r) の要素の並びを反転させる。
    - rotate(l, r, k): 区間 [l, r) の要素を右に k 個分シフト（巡回シフト）させる。
    - bisect_left(value): 配列が昇順ソートされている前提で、value 以上となる最初のインデックスを返す。
    - get(index): 指定したインデックスの要素の値を取得する。
    - to_list(): 現在の配列の状態をPythonのリストとして返す。

    入力:
    - init: capacity (予測される最大ノード数)
    - 各メソッド: インデックス(l, r, index)は0-indexed。区間は半開区間 [l, r)。

    出力:
    - query(l, r) は (区間和, 区間最小値, 区間最大値) のタプル。
    - pop系, get系は該当する要素の値を返す。

        計算量:
        - 時間計算量: 各操作は期待 O(log N)、最悪 O(N)。build は期待 O(N log N)、
            最悪 O(N^2)、to_list は O(N)。
    - 空間計算量: O(capacity)

    補足:
    - 遅延評価は `rev` (反転) と `add` (加算) の2種類を管理。
    """

    def __init__(self, capacity: int = 300005, default_min: int = 10**18, default_max: int = -10**18):
        self.capacity = capacity
        self.default_min = default_min
        self.default_max = default_max
        
        self.val = [0] * capacity
        self.pri = [0] * capacity
        self.size = [0] * capacity
        self.sum_v = [0] * capacity
        self.min_v = [default_min] * capacity
        self.max_v = [default_max] * capacity
        
        self.rev = [0] * capacity
        self.add = [0] * capacity
        
        self.left = [0] * capacity
        self.right = [0] * capacity
        
        self.root = 0
        self.node_count = 0
        
        self._x = 123456789
        self._y = 362436069
        self._z = 521288629
        self._w = 88675123

    def _rand(self) -> int:
        t = self._x ^ ((self._x << 11) & 0xFFFFFFFF)
        self._x, self._y, self._z = self._y, self._z, self._w
        self._w = (self._w ^ (self._w >> 19) ^ (t ^ (t >> 8))) & 0xFFFFFFFF
        return self._w

    def _create_node(self, value: int) -> int:
        self.node_count += 1
        u = self.node_count
        self.val[u] = value
        self.pri[u] = self._rand()
        self.size[u] = 1
        self.sum_v[u] = value
        self.min_v[u] = value
        self.max_v[u] = value
        self.rev[u] = 0
        self.add[u] = 0
        self.left[u] = 0
        self.right[u] = 0
        return u

    def _push_up(self, u: int):
        if u == 0:
            return
        l, r = self.left[u], self.right[u]
        self.size[u] = self.size[l] + 1 + self.size[r]
        self.sum_v[u] = self.sum_v[l] + self.val[u] + self.sum_v[r]
        self.min_v[u] = min(self.min_v[l], self.val[u], self.min_v[r])
        self.max_v[u] = max(self.max_v[l], self.val[u], self.max_v[r])

    def _push_down(self, u: int):
        if u == 0:
            return
        l, r = self.left[u], self.right[u]
        
        # 反転の伝播
        if self.rev[u]:
            if l:
                self.rev[l] ^= 1
                self.left[l], self.right[l] = self.right[l], self.left[l]
            if r:
                self.rev[r] ^= 1
                self.left[r], self.right[r] = self.right[r], self.left[r]
            self.rev[u] = 0
            
        # 加算の伝播
        if self.add[u]:
            add_val = self.add[u]
            if l:
                self.add[l] += add_val
                self.val[l] += add_val
                self.sum_v[l] += add_val * self.size[l]
                self.min_v[l] += add_val
                self.max_v[l] += add_val
            if r:
                self.add[r] += add_val
                self.val[r] += add_val
                self.sum_v[r] += add_val * self.size[r]
                self.min_v[r] += add_val
                self.max_v[r] += add_val
            self.add[u] = 0

    def _split(self, u: int, k: int):
        if u == 0:
            return 0, 0
        self._push_down(u)
        implicit_key = self.size[self.left[u]] + 1
        if k < implicit_key:
            l1, r1 = self._split(self.left[u], k)
            self.left[u] = r1
            self._push_up(u)
            return l1, u
        else:
            l2, r2 = self._split(self.right[u], k - implicit_key)
            self.right[u] = l2
            self._push_up(u)
            return u, r2

    def _merge(self, l: int, r: int) -> int:
        if l == 0 or r == 0:
            return l if l != 0 else r
        self._push_down(l)
        self._push_down(r)
        if self.pri[l] > self.pri[r]:
            self.right[l] = self._merge(self.right[l], r)
            self._push_up(l)
            return l
        else:
            self.left[r] = self._merge(l, self.left[r])
            self._push_up(r)
            return r

    def build(self, arr: list):
        """配列から木を構築"""
        if not arr:
            return
        if self.root == 0:
            stack = []
            for value in arr:
                u = self._create_node(value)
                last = 0
                while stack and self.pri[stack[-1]] < self.pri[u]:
                    last = stack.pop()
                if stack:
                    self.right[stack[-1]] = u
                self.left[u] = last
                stack.append(u)
            self.root = stack[0]

            order = []
            todo = [self.root]
            while todo:
                u = todo.pop()
                order.append(u)
                if self.left[u]:
                    todo.append(self.left[u])
                if self.right[u]:
                    todo.append(self.right[u])
            for u in reversed(order):
                self._push_up(u)
            return
        for val in arr:
            self.insert(self.size[self.root], val)

    def insert(self, index: int, value: int):
        u = self._create_node(value)
        l, r = self._split(self.root, index)
        self.root = self._merge(self._merge(l, u), r)

    def erase(self, index: int):
        l, r = self._split(self.root, index)
        m, r = self._split(r, 1)
        self.root = self._merge(l, r)

    def pop(self, index: int = -1) -> int:
        """指定位置（デフォルトは末尾）の要素を削除して返す"""
        if index < 0:
            index += self.size[self.root]
        l, r = self._split(self.root, index)
        m, r = self._split(r, 1)
        res = self.val[m]
        self.root = self._merge(l, r)
        return res

    def _find_max_index(self, u: int) -> int:
        """部分木uから最大値を持つインデックスを探索"""
        if u == 0:
            return -1
        self._push_down(u)
        # 左の子に最大値があるか
        if self.left[u] and self.max_v[self.left[u]] == self.max_v[u]:
            return self._find_max_index(self.left[u])
        # 現在のノードが最大値か
        if self.val[u] == self.max_v[u]:
            return self.size[self.left[u]]
        # 右の子に最大値がある
        return self.size[self.left[u]] + 1 + self._find_max_index(self.right[u])

    def pop_max(self) -> int:
        """木全体の最大値を削除して返す"""
        if self.root == 0:
            raise IndexError("pop_max from empty tree")
        idx = self._find_max_index(self.root)
        return self.pop(idx)

    def bisect_left(self, value: int) -> int:
        """配列が昇順のとき、value以上の値が現れる最初のインデックスを返す"""
        u = self.root
        idx = 0
        while u != 0:
            self._push_down(u)
            if self.val[u] >= value:
                # 自身を含め左側に候補がある
                u = self.left[u]
            else:
                # 左側と自身は条件を満たさないのでスキップ
                idx += self.size[self.left[u]] + 1
                u = self.right[u]
        return idx

    def update(self, index: int, value: int):
        l, r = self._split(self.root, index)
        m, r = self._split(r, 1)
        self.val[m] = value
        self._push_up(m)
        self.root = self._merge(self._merge(l, m), r)

    def add_val(self, left: int, right: int, value: int):
        """区間加算"""
        if left >= right:
            return
        l, r = self._split(self.root, left)
        m, r = self._split(r, right - left)
        
        self.add[m] += value
        self.val[m] += value
        self.sum_v[m] += value * self.size[m]
        self.min_v[m] += value
        self.max_v[m] += value
        
        self.root = self._merge(self._merge(l, m), r)

    def get(self, index: int) -> int:
        l, r = self._split(self.root, index)
        m, r = self._split(r, 1)
        res = self.val[m]
        self.root = self._merge(self._merge(l, m), r)
        return res

    def query(self, left: int, right: int):
        """(区間和, 最小値, 最大値) を返す"""
        if left >= right:
            return 0, self.default_min, self.default_max
        l, r = self._split(self.root, left)
        m, r = self._split(r, right - left)
        res = (self.sum_v[m], self.min_v[m], self.max_v[m])
        self.root = self._merge(self._merge(l, m), r)
        return res

    def reverse(self, left: int, right: int):
        if left >= right:
            return
        l, r = self._split(self.root, left)
        m, r = self._split(r, right - left)
        
        self.rev[m] ^= 1
        self.left[m], self.right[m] = self.right[m], self.left[m]
        
        self.root = self._merge(self._merge(l, m), r)

    def rotate(self, left: int, right: int, k: int):
        """区間を右にk個分巡回シフトさせる"""
        if left >= right:
            return
        length = right - left
        k %= length
        if k == 0:
            return
        
        l, r = self._split(self.root, left)
        m, r = self._split(r, length)
        
        # m を [0, length-k) と [length-k, length) に分割
        m1, m2 = self._split(m, length - k)
        # m2を前に持ってきてマージ
        m_rotated = self._merge(m2, m1)
        
        self.root = self._merge(self._merge(l, m_rotated), r)

    def to_list(self) -> list:
        res = []
        def dfs(u):
            if u == 0:
                return
            self._push_down(u)
            dfs(self.left[u])
            res.append(self.val[u])
            dfs(self.right[u])
        dfs(self.root)
        return res

    def __len__(self):
        return self.size[self.root]

class BitSet:
    """概要:
        Python int を利用した任意長の非負ビット集合を扱う。
    入力:
        BitSet(x) の x は整数ビットマスクまたはビット位置の iterable。
    出力:
        add/remove/count、論理演算、shift などの集合操作を提供する。
    計算量:
        各操作は保持するビット長に比例する。
    補足:
        ビット位置は 0 以上。元の集合を変更しない演算は新しい BitSet を返す。
    使用例:
        s = BitSet([1, 3]); s.add(5); print(3 in s)
    """
    def __init__(self,x=0): self.bits=x if isinstance(x,int) else sum(1<<i for i in x)
    def add(self,i): self.bits|=1<<i
    def remove(self,i): self.bits&=~(1<<i)
    def __contains__(self,i): return bool(self.bits>>i&1)
    def count(self): return self.bits.bit_count()
    def __and__(self,o): return BitSet(self.bits&o.bits)
    def __or__(self,o): return BitSet(self.bits|o.bits)
    def __xor__(self,o): return BitSet(self.bits^o.bits)
    def shift(self,k): return BitSet(self.bits<<k if k>=0 else self.bits>>-k)

class SegTreeBeats:
    """概要:
        区間 chmin、chmax、加算と区間和を扱う Segment Tree Beats。
    入力:
        SegTreeBeats(a) の a は初期配列。操作区間は全て [l,r)。
    出力:
        range_sum(l,r) が区間和を返す。
    計算量:
        構築 O(n)、各更新は償却 O(log n)、空間 O(n)。
    補足:
        負数、同値、空配列にも対応する。
    """
    def __init__(self,a):
        self.n=len(a); z=4*max(1,self.n); I=10**30
        self.sm=[0]*z; self.mx=[-I]*z; self.mx2=[-I]*z; self.mxc=[0]*z
        self.mn=[I]*z; self.mn2=[I]*z; self.mnc=[0]*z; self.lz=[0]*z
        def build(k,l,r):
            if r-l==1:
                if l<self.n: self.sm[k]=self.mx[k]=self.mn[k]=a[l]
                self.mx2[k]=-I; self.mn2[k]=I; self.mxc[k]=self.mnc[k]=1; return
            q=(l+r)//2; build(k*2,l,q); build(k*2+1,q,r); self._pull(k)
        if self.n: build(1,0,self.n)
    def _pull(self,k):
        x,y=k*2,k*2+1; self.sm[k]=self.sm[x]+self.sm[y]
        self.mx[k]=max(self.mx[x],self.mx[y]); self.mxc[k]=(self.mxc[x] if self.mx[x]==self.mx[k] else 0)+(self.mxc[y] if self.mx[y]==self.mx[k] else 0)
        self.mx2[k]=max(self.mx2[x] if self.mx[x]==self.mx[k] else self.mx[x],self.mx2[y] if self.mx[y]==self.mx[k] else self.mx[y])
        self.mn[k]=min(self.mn[x],self.mn[y]); self.mnc[k]=(self.mnc[x] if self.mn[x]==self.mn[k] else 0)+(self.mnc[y] if self.mn[y]==self.mn[k] else 0)
        self.mn2[k]=min(self.mn2[x] if self.mn[x]==self.mn[k] else self.mn[x],self.mn2[y] if self.mn[y]==self.mn[k] else self.mn[y])
    def _add(self,k,x,n):
        self.sm[k]+=x*n; self.mx[k]+=x; self.mn[k]+=x
        if self.mx2[k]>-10**29: self.mx2[k]+=x
        if self.mn2[k]<10**29: self.mn2[k]+=x
        self.lz[k]+=x
    def _cmax(self,k,x):
        if self.mx[k]<=x: return
        self.sm[k]+=(x-self.mx[k])*self.mxc[k]
        if self.mn[k]==self.mx[k]: self.mn[k]=x
        elif self.mn2[k]==self.mx[k]: self.mn2[k]=x
        self.mx[k]=x
    def _cmin(self,k,x):
        if self.mn[k]>=x: return
        self.sm[k]+=(x-self.mn[k])*self.mnc[k]
        if self.mx[k]==self.mn[k]: self.mx[k]=x
        elif self.mx2[k]==self.mn[k]: self.mx2[k]=x
        self.mn[k]=x
    def _push(self,k,l,r):
        if r-l==1: self.lz[k]=0; return
        q=(l+r)//2; x,y=k*2,k*2+1
        if self.lz[k]: self._add(x,self.lz[k],q-l); self._add(y,self.lz[k],r-q); self.lz[k]=0
        if self.mx[x]>self.mx[k]: self._cmax(x,self.mx[k])
        if self.mx[y]>self.mx[k]: self._cmax(y,self.mx[k])
        if self.mn[x]<self.mn[k]: self._cmin(x,self.mn[k])
        if self.mn[y]<self.mn[k]: self._cmin(y,self.mn[k])
    def _run(self,k,l,r,a,b,typ,x=0):
        if b<=l or r<=a: return 0
        if typ==0 and a<=l and r<=b: self._add(k,x,r-l); return 0
        if typ==1 and (b<=l or r<=a or self.mx[k]<=x): return 0
        if typ==1 and a<=l and r<=b and self.mx2[k]<x: self._cmax(k,x); return 0
        if typ==2 and (b<=l or r<=a or self.mn[k]>=x): return 0
        if typ==2 and a<=l and r<=b and self.mn2[k]>x: self._cmin(k,x); return 0
        q=(l+r)//2; self._push(k,l,r)
        self._run(k*2,l,q,a,b,typ,x); self._run(k*2+1,q,r,a,b,typ,x); self._pull(k)
    def range_add(self,l,r,x): self._run(1,0,self.n,l,r,0,x) if l<r and self.n else None
    def range_chmin(self,l,r,x): self._run(1,0,self.n,l,r,1,x) if l<r and self.n else None
    def range_chmax(self,l,r,x): self._run(1,0,self.n,l,r,2,x) if l<r and self.n else None
    def range_sum(self,l,r):
        if not self.n or l>=r: return 0
        def qsum(k,L,R):
            if r<=L or R<=l: return 0
            if l<=L and R<=r: return self.sm[k]
            self._push(k,L,R); q=(L+R)//2
            return qsum(k*2,L,q)+qsum(k*2+1,q,R)
        return qsum(1,0,self.n)

class LinkCutTree:
    """概要:
        splay 木で森林を動的に管理する Link-Cut Tree。
    入力:
        LinkCutTree(values) の values は各頂点の初期値（0-indexed）。
    出力:
        link/cut は成功時 True、connected は連結判定、path_sum は頂点値の和を返す。
        set_value/get_value で頂点値を更新・取得できる。
    計算量:
        構築 O(n)、各操作は償却 O(log n)、空間 O(n)。
    補足:
        link は異なる連結成分間、cut は存在する辺に対して呼ぶ。
        path_sum は非連結なら None。link(x,y) は x-y に辺を追加し、
        cut(x,y) はその直接辺だけを削除する。
    使用例:
        lct = LinkCutTree([1, 2, 3]); lct.link(0, 1)
        assert lct.path_sum(0, 1) == 3
    """
    class _Node:
        __slots__ = ("l", "r", "p", "value", "total", "rev")
        def __init__(self, value):
            self.l = self.r = self.p = None
            self.value = self.total = value
            self.rev = False

    def __init__(self, values):
        self.nodes = [self._Node(x) for x in values]

    @staticmethod
    def _is_root(x):
        return x.p is None or (x.p.l is not x and x.p.r is not x)

    @staticmethod
    def _pull(x):
        x.total = x.value
        if x.l is not None:
            x.total += x.l.total
        if x.r is not None:
            x.total += x.r.total

    @staticmethod
    def _push(x):
        if x.rev:
            x.l, x.r = x.r, x.l
            if x.l is not None:
                x.l.rev = not x.l.rev
            if x.r is not None:
                x.r.rev = not x.r.rev
            x.rev = False

    def _rotate(self, x):
        p = x.p
        g = p.p
        was_root = self._is_root(p)
        if p.l is x:
            p.l = x.r
            if x.r is not None:
                x.r.p = p
            x.r = p
        else:
            p.r = x.l
            if x.l is not None:
                x.l.p = p
            x.l = p
        p.p = x
        x.p = g
        if g is not None and not was_root:
            if g.l is p:
                g.l = x
            elif g.r is p:
                g.r = x
        self._pull(p)
        self._pull(x)

    def _splay(self, x):
        path = [x]
        y = x
        while not self._is_root(y):
            y = y.p
            path.append(y)
        for y in reversed(path):
            self._push(y)
        while not self._is_root(x):
            p = x.p
            g = p.p
            if not self._is_root(p):
                if (p.l is x) == (g.l is p):
                    self._rotate(p)
                else:
                    self._rotate(x)
            self._rotate(x)

    def _access(self, x):
        last = None
        y = x
        while y is not None:
            self._splay(y)
            y.r = last
            self._pull(y)
            last = y
            y = y.p
        self._splay(x)

    def _make_root(self, x):
        self._access(x)
        x.rev = not x.rev

    def _find_root(self, x):
        self._access(x)
        while True:
            self._push(x)
            if x.l is None:
                break
            x = x.l
        self._splay(x)
        return x

    def _node(self, i):
        if not 0 <= i < len(self.nodes):
            raise IndexError("vertex index")
        return self.nodes[i]

    def link(self, x, y):
        x, y = self._node(x), self._node(y)
        self._make_root(x)
        if self._find_root(y) is x:
            return False
        x.p = y
        return True

    def cut(self, x, y):
        x, y = self._node(x), self._node(y)
        self._make_root(x)
        self._access(y)
        if y.l is not x or x.r is not None:
            return False
        y.l.p = None
        y.l = None
        self._pull(y)
        return True

    def connected(self, x, y):
        x, y = self._node(x), self._node(y)
        if x is y:
            return True
        self._make_root(x)
        return self._find_root(y) is x

    def path_sum(self, x, y):
        x, y = self._node(x), self._node(y)
        if x is not y:
            self._make_root(x)
            if self._find_root(y) is not x:
                return None
        self._make_root(x)
        self._access(y)
        return y.total

    def set_value(self, x, value):
        node = self._node(x)
        self._access(node)
        node.value = value
        self._pull(node)

    def get_value(self, x):
        node = self._node(x)
        self._access(node)
        return node.value

# ============================================================
# 文字列アルゴリズム
# ============================================================

class RollingHash:
    """概要:
        文字列の部分文字列比較を高速化するダブルローリングハッシュ。

    メソッド:
        get(l, r): 部分文字列 s[l:r] のハッシュ値ペアを返す。
        lcp(i, j): 位置 i, j からの最長共通接頭辞長を返す。

    計算量:
        初期化は O(n)、get は O(1)、lcp は O(logN)。

    補足:
        2つの法を使って衝突確率を低減している。

    使用例:
        rh = RollingHash("abcabc")
        print(rh.get(0, 3) == rh.get(3, 6))  # True ("abc" == "abc")
    """
    MOD1, MOD2 = 10**9 + 7, 10**9 + 9
    BASE1, BASE2 = 1007, 2009

    def __init__(self, s: str):
        self.n = len(s)
        self.hash1 = [0] * (self.n + 1)
        self.hash2 = [0] * (self.n + 1)
        self.pow1 = [1] * (self.n + 1)
        self.pow2 = [1] * (self.n + 1)
        for i in range(self.n):
            self.hash1[i + 1] = (self.hash1[i] * self.BASE1 + ord(s[i])) % self.MOD1
            self.hash2[i + 1] = (self.hash2[i] * self.BASE2 + ord(s[i])) % self.MOD2
            self.pow1[i + 1] = self.pow1[i] * self.BASE1 % self.MOD1
            self.pow2[i + 1] = self.pow2[i] * self.BASE2 % self.MOD2

    def get(self, l: int, r: int) -> tuple[int, int]:
        """[l, r) のハッシュ"""
        h1 = (self.hash1[r] - self.hash1[l] * self.pow1[r - l]) % self.MOD1
        h2 = (self.hash2[r] - self.hash2[l] * self.pow2[r - l]) % self.MOD2
        return (h1, h2)

    def lcp(self, i: int, j: int) -> int:
        """位置i, jから始まる最長共通接頭辞の長さ"""
        ok, ng = 0, min(self.n - i, self.n - j) + 1
        while ng - ok > 1:
            mid = (ok + ng) // 2
            if self.get(i, i + mid) == self.get(j, j + mid):
                ok = mid
            else:
                ng = mid
        return ok


def z_algorithm(s: str) -> list[int]:
    """概要:
        文字列 s の Z 配列を構築する。
    入力:
        s (str): 対象文字列。
    出力:
        list[int]: z[i] = s と s[i:] の最長共通接頭辞長。
    補足:
        文字列照合やパターン探索の前処理として O(|s|) で有効。
    """
    n = len(s)
    if n == 0:
        return []
    z = [0] * n
    z[0] = n
    i, j = 1, 0
    while i < n:
        while i + j < n and s[j] == s[i + j]:
            j += 1
        z[i] = j
        if j == 0:
            i += 1
            continue
        k = 1
        while k < j and k + z[k] < j:
            z[i + k] = z[k]
            k += 1
        i += k
        j -= k
    return z


def run_length_encode(s: str | list) -> list[tuple]:
    """概要:
        連続要素を (値, 連続数) に圧縮する。
    入力:
        s (str | list): 圧縮対象シーケンス。
    出力:
        list[tuple]: [(値, 連続数), ...]。
    補足:
        空入力は空配列を返す。計算量は O(n)。
    """
    if not s: return []
    result = []
    current, count = s[0], 1
    for i in range(1, len(s)):
        if s[i] == current:
            count += 1
        else:
            result.append((current, count))
            current, count = s[i], 1
    result.append((current, count))
    return result


class Trie:
    """概要:
        文字列集合を前方一致ベースで管理する Trie 木。

    内部クラス:
        Node: Trie の1ノードを表す。

    メソッド:
        insert(s): 文字列 s を登録する。
        search(s): 文字列 s が完全一致で登録済みか判定する。
        starts_with(prefix): 接頭辞 prefix を持つ語が存在するか判定する。
        count_prefix(prefix): 接頭辞 prefix を持つ登録語数を返す。

    計算量:
        insert/search/starts_with/count_prefix は文字列長を L として O(L)。
    """
    class Node:
        """概要:
            Trie の1ノードを表す内部クラス。

        属性:
            next (dict[str, Trie.Node]): 文字 -> 次ノードの辞書。
            end (int): このノードで終端となる単語数。
            cnt (int): このノードを通過する単語数。
        """
        __slots__ = ("next", "end", "cnt")

        def __init__(self):
            self.next: dict[str, "Trie.Node"] = {}
            self.end: int = 0
            self.cnt: int = 0

    def __init__(self):
        self.root = Trie.Node()

    def insert(self, s: str) -> None:
        node = self.root
        node.cnt += 1
        for ch in s:
            if ch not in node.next:
                node.next[ch] = Trie.Node()
            node = node.next[ch]
            node.cnt += 1
        node.end += 1

    def search(self, s: str) -> bool:
        node = self.root
        for ch in s:
            if ch not in node.next:
                return False
            node = node.next[ch]
        return node.end > 0

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.next:
                return False
            node = node.next[ch]
        return True

    def count_prefix(self, prefix: str) -> int:
        """prefixで始まる登録文字列数"""
        node = self.root
        for ch in prefix:
            if ch not in node.next:
                return 0
            node = node.next[ch]
        return node.cnt


def kmp_table(pattern: str) -> list[int]:
    """概要:
        KMP 法で使う prefix function（部分一致テーブル）を構築する。
    入力:
        pattern (str): パターン文字列。
    出力:
        list[int]: pi[i] = pattern[:i+1] の最長 proper prefix/suffix 長。
    補足:
        `kmp_search` の前処理として利用する。計算量は O(|pattern|)。
    """
    n = len(pattern)
    pi = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            pi[i] = j
    return pi


def kmp_search(text: str, pattern: str) -> list[int]:
    """概要:
        KMP 法で text 内の pattern 出現開始位置を列挙する。
    入力:
        text (str): 検索対象文字列。
        pattern (str): 検索パターン。
    出力:
        list[int]: 出現開始インデックス一覧。
    補足:
        計算量は O(|text| + |pattern|)。空パターンは全位置一致として扱う。
    """
    if not pattern:
        return list(range(len(text) + 1))
    pi = kmp_table(pattern)
    res = []
    j = 0
    for i, ch in enumerate(text):
        while j > 0 and ch != pattern[j]:
            j = pi[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            res.append(i - len(pattern) + 1)
            j = pi[j - 1]
    return res


def levenshtein_distance(s: str, t: str) -> int:
    """概要:
        文字列 s と t の編集距離（レーベンシュタイン距離）を求める。
    入力:
        s (str): 文字列1。
        t (str): 文字列2。
    出力:
        int: 挿入・削除・置換（各コスト1）で s を t に変換する最小操作回数。
    補足:
        計算量は O(|s|*|t|)、メモリは O(min(|s|,|t|))。
    """
    if len(s) < len(t):
        s, t = t, s
    n, m = len(s), len(t)
    if m == 0:
        return n

    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        si = s[i - 1]
        for j in range(1, m + 1):
            cost = 0 if si == t[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + cost,
            )
        prev = curr
    return prev[m]

class AhoCorasick:
    """概要:
        Aho-Corasick 法で複数パターンを検索する。
    入力:
        add(pattern) で登録し、全登録後に build()、find(text) を呼ぶ。
    出力:
        find は (開始位置, パターン番号) のリストを返す。
    計算量:
        構築 O(パターン総長)、検索 O(本文長+出力数)。
    補足:
        文字は dict で扱い、重複パターンと空パターン（無視）に対応する。
    使用例:
        ac = AhoCorasick(); ac.add("aba"); ac.build(); ac.find("ababa")
    """
    def __init__(self): self.next=[{}]; self.fail=[0]; self.out=[[]]; self.terminal=[[]]; self.patterns=[]
    def add(self,s):
        v=0
        for c in s:
            if c not in self.next[v]:
                self.next[v][c]=len(self.next); self.next.append({}); self.fail.append(0); self.out.append([]); self.terminal.append([])
            v=self.next[v][c]
        k=len(self.patterns); self.patterns.append(s); self.terminal[v].append(k); return k
    def build(self):
        self.fail=[0]*len(self.next)
        # build() may be called repeatedly; do not duplicate inherited outputs.
        terminal=[list(x) for x in self.terminal]
        self.out=[x[:] for x in terminal]
        q=deque()
        for to in self.next[0].values(): q.append(to)
        while q:
            v=q.popleft()
            for c,to in self.next[v].items():
                q.append(to); f=self.fail[v]
                while f and c not in self.next[f]: f=self.fail[f]
                self.fail[to]=self.next[f].get(c,0);                 self.out[to]=terminal[to]+self.out[self.fail[to]]
    def find(self,text):
        v=0; ans=[]
        for i,c in enumerate(text):
            while v and c not in self.next[v]: v=self.fail[v]
            v=self.next[v].get(c,0)
            ans.extend((i-len(self.patterns[k])+1,k) for k in self.out[v])
        return ans

def suffix_array(s):
    """概要:
        文字列または整数列の suffix array を doubling 法で構築する。
    入力:
        s (str | Sequence[int]): 対象列。
    出力:
        list[int]: 接尾辞の開始位置を辞書順に並べた配列。
    計算量:
        時間 O(n log n)、空間 O(n)。
    補足:
        空列、負の整数、文字列を扱う。
    """
    n=len(s)
    if not n: return []
    sa=list(range(n)); r=list(s); rank={x:i for i,x in enumerate(sorted(set(r)))}; r=[rank[x] for x in r]; k=1
    while k<n:
        sa.sort(key=lambda i:(r[i],r[i+k] if i+k<n else -1))
        nr=[0]*n
        for j in range(1,n): nr[sa[j]]=nr[sa[j-1]]+((r[sa[j-1]],r[sa[j-1]+k] if sa[j-1]+k<n else -1)!=(r[sa[j]],r[sa[j]+k] if sa[j]+k<n else -1))
        r=nr
        if r[sa[-1]]==n-1: break
        k*=2
    return sa

def lcp_array(s, sa=None):
    """概要:
        suffix array の隣接 suffix 間の最長共通接頭辞長を求める。
    入力:
        s (str | Sequence[int]): 対象列。sa は suffix_array(s)（省略可）。
    出力:
        list[int]: sa[i], sa[i+1] 間の LCP（末尾は 0）。
    計算量:
        時間 O(n)、空間 O(n)。
    補足:
        Kasai 法を用いる。
    """
    if sa is None: sa=suffix_array(s)
    n=len(s); rank=[0]*n
    for i,v in enumerate(sa): rank[v]=i
    h=0; out=[0]*max(0,n-1)
    for i in range(n):
        r=rank[i]
        if r==n-1: h=0; continue
        j=sa[r+1]
        while i+h<n and j+h<n and s[i+h]==s[j+h]: h+=1
        out[r]=h
        if h: h-=1
    return out

# ============================================================
# 回文・進数変換
# ============================================================

def to_base(n: int, base: int) -> str:
    """概要:
        非負整数 n を base 進法表記の文字列に変換する。
    入力:
        n (int): 変換対象の非負整数。
        base (int): 基数（2以上）。
    出力:
        str: base 進法表記の文字列（0 なら "0"）。
    補足:
        計算量は O(log_base(n))。
    使用例:
        to_base(414, 8)  # "636"
        to_base(10, 2)   # "1010"
    """
    if n < 0 or base < 2 or base > 36:
        raise ValueError("requires n >= 0 and 2 <= base <= 36")
    if n == 0:
        return "0"
    symbols = string.digits + string.ascii_uppercase
    digits = []
    while n > 0:
        digits.append(symbols[n % base])
        n //= base
    return ''.join(reversed(digits))


def gen_palindromes_d_digits(d: int):
    """概要:
        d 桁の十進法回文数を昇順に生成するジェネレータ。
    入力:
        d (int): 桁数（1以上）。
    出力:
        Iterator[int]: d 桁の回文数を昇順に yield する。
    補足:
        前半部（⌈d/2⌉桁）を走査して回文を構成する。生成個数は Θ(10^(d/2))、
        全生成の時間計算量は O(d * 10^(d/2))、追加メモリは O(d)。
        d=1: 1〜9、d=2: 11,22,...,99、d=3: 101,111,...,999 など。
    使用例:
        for p in gen_palindromes_d_digits(3):
            print(p)  # 101, 111, 121, ..., 999
    """
    if d < 1:
        raise ValueError("d must be at least 1")
    half = (d + 1) // 2
    start = 10 ** (half - 1)
    end   = 10 ** half
    for front in range(start, end):
        s = str(front)
        if d % 2 == 0:
            palindrome_str = s + s[::-1]
        else:
            palindrome_str = s + s[-2::-1]
        yield int(palindrome_str)


# ============================================================
# 二分探索
# ============================================================

from collections.abc import Callable
def binary_search_min(ng: int, ok: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最小 x を整数二分探索で求める。
    入力:
        ng (int): 条件を満たさない側の初期値。
        ok (int): 条件を満たす側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最小の値。
    補足:
        境界の妥当性（ng 側False, ok 側True）を事前に満たすこと。
        計算量は O(log|ok-ng|) 回の判定関数呼び出し。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

from collections.abc import Callable
def binary_search_max(ok: int, ng: int, check: Callable[[int], bool]) -> int:
    """概要:
        単調性を利用して `check(x)=True` となる最大 x を整数二分探索で求める。
    入力:
        ok (int): 条件を満たす側の初期値。
        ng (int): 条件を満たさない側の初期値。
        check (Callable[[int], bool]): 判定関数（単調）。
    出力:
        int: 条件を満たす最大の値。
    補足:
        境界の妥当性（ok 側True, ng 側False）を事前に満たすこと。
        計算量は O(log|ok-ng|) 回の判定関数呼び出し。
    """
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok

from collections.abc import Callable
def binary_search_float(ok: float, ng: float, check: Callable[[float], bool], iterations: int = 100) -> float:
    """概要:
        実数領域で二分探索を反復回数固定で行う。
    入力:
        ok (float): 条件を満たす側の初期値。
        ng (float): 条件を満たさない側の初期値。
        check (Callable[[float], bool]): 判定関数（単調）。
        iterations (int): 反復回数。
    出力:
        float: 探索結果（近似解）。
    補足:
        精度は反復回数で調整する。計算量は O(iterations)。
    """
    for _ in range(iterations):
        mid = (ok + ng) / 2
        if check(mid):
            ok = mid
        else:
            ng = mid
    return ok


def lis(arr: list[int], strict: bool = True) -> int:
    """概要:
        配列の最長増加部分列（LIS）の長さを求める。
    入力:
        arr (list[int]): 対象配列。
        strict (bool): True なら狭義増加、False なら広義増加。
    出力:
        int: LIS の長さ。
    補足:
        計算量は O(n log n)。復元は行わず長さのみ返す。
    """
    dp = []
    for x in arr:
        i = bisect_left(dp, x) if strict else bisect_right(dp, x)
        if i == len(dp):
            dp.append(x)
        else:
            dp[i] = x
    return len(dp)

# ============================================================
# 三分探索・黄金分割探索・フィボナッチ探索
# ============================================================

def ternary_search_int_max(f, lo: int, hi: int) -> tuple[int, int]:
    """概要:
        整数域の単峰関数（上に凸）に対して三分探索で最大値を求める。
    入力:
        f   : 探索対象の関数（int -> 比較可能な値）。
        lo  (int): 探索区間の左端（inclusive）。
        hi  (int): 探索区間の右端（inclusive）。
    出力:
        tuple[int, int]: (最大値を取るx, f(x)の最大値)。
    制約:
        f が lo..hi 上で単峰（上に凸）であること。
        区間が潰れる（hi - lo <= 2）まで繰り返す。
    計算量:
        O(log(hi - lo)) 回の関数評価。
    使用例:
        # f(x) = -(x-3)^2 + 9  (x=3 で最大値 9)
        x, v = ternary_search_int_max(lambda x: -(x-3)**2+9, 0, 10)
        print(x, v)  # 3 9
    """
    while hi - lo > 2:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    # 残った区間を全探索（最大3点）
    best_x = lo
    best_v = f(lo)
    for x in range(lo + 1, hi + 1):
        v = f(x)
        if v > best_v:
            best_v = v
            best_x = x
    return best_x, best_v


def ternary_search_int_min(f, lo: int, hi: int) -> tuple[int, int]:
    """概要:
        整数域の単峰関数（下に凸）に対して三分探索で最小値を求める。
    入力:
        f   : 探索対象の関数（int -> 比較可能な値）。
        lo  (int): 探索区間の左端（inclusive）。
        hi  (int): 探索区間の右端（inclusive）。
    出力:
        tuple[int, int]: (最小値を取るx, f(x)の最小値)。
    制約:
        f が lo..hi 上で単峰（下に凸）であること。
    計算量:
        O(log(hi - lo)) 回の関数評価。
    使用例:
        # f(x) = (x-3)^2  (x=3 で最小値 0)
        x, v = ternary_search_int_min(lambda x: (x-3)**2, 0, 10)
        print(x, v)  # 3 0
    """
    while hi - lo > 2:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if f(m1) > f(m2):
            lo = m1
        else:
            hi = m2
    best_x = lo
    best_v = f(lo)
    for x in range(lo + 1, hi + 1):
        v = f(x)
        if v < best_v:
            best_v = v
            best_x = x
    return best_x, best_v


def ternary_search_float_max(f, lo: float, hi: float, eps: float = 1e-9) -> tuple[float, float]:
    """概要:
        実数域の単峰関数（上に凸）に対して三分探索で最大値を求める。
    入力:
        f   : 探索対象の関数（float -> float）。
        lo  (float): 探索区間の左端。
        hi  (float): 探索区間の右端。
        eps (float): 収束判定の許容誤差（デフォルト 1e-9）。
    出力:
        tuple[float, float]: (最大値を取るx（近似）, f(x)の最大値（近似））。
    制約:
        f が [lo, hi] 上で単峰（上に凸）であること。
    補足:
        区間幅が eps 以下になるまで繰り返す。収束ステップ数は
        ceil(log_{3/2}((hi-lo)/eps)) 程度。
    計算量:
        O(log((hi-lo)/eps)) 回の関数評価。
    使用例:
        # f(x) = -(x-2.5)^2 + 5
        x, v = ternary_search_float_max(lambda x: -(x-2.5)**2+5, 0.0, 5.0)
        print(x, v)  # 約 2.5, 5.0
    """
    while hi - lo > eps:
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    x = (lo + hi) / 2
    return x, f(x)


def ternary_search_float_min(f, lo: float, hi: float, eps: float = 1e-9) -> tuple[float, float]:
    """概要:
        実数域の単峰関数（下に凸）に対して三分探索で最小値を求める。
    入力:
        f   : 探索対象の関数（float -> float）。
        lo  (float): 探索区間の左端。
        hi  (float): 探索区間の右端。
        eps (float): 収束判定の許容誤差（デフォルト 1e-9）。
    出力:
        tuple[float, float]: (最小値を取るx（近似）, f(x)の最小値（近似））。
    制約:
        f が [lo, hi] 上で単峰（下に凸）であること。
    計算量:
        O(log((hi-lo)/eps)) 回の関数評価。
    使用例:
        # f(x) = (x-2.5)^2
        x, v = ternary_search_float_min(lambda x: (x-2.5)**2, 0.0, 5.0)
        print(x, v)  # 約 2.5, 0.0
    """
    while hi - lo > eps:
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if f(m1) > f(m2):
            lo = m1
        else:
            hi = m2
    x = (lo + hi) / 2
    return x, f(x)


def golden_section_search_max(f, lo: float, hi: float, eps: float = 1e-9) -> tuple[float, float]:
    """概要:
        黄金分割探索で実数域の単峰関数（上に凸）の最大値を求める。
        三分探索より1ステップあたりの関数評価回数が少ない（初回2回、以後1回）。
    入力:
        f   : 探索対象の関数（float -> float）。
        lo  (float): 探索区間の左端。
        hi  (float): 探索区間の右端。
        eps (float): 収束判定の許容誤差（デフォルト 1e-9）。
    出力:
        tuple[float, float]: (最大値を取るx（近似）, f(x)の最大値（近似））。
    制約:
        f が [lo, hi] 上で単峰（上に凸）であること。
    補足:
        各反復で区間が 1/φ ≈ 0.618 倍に縮小する。
        三分探索は 2/3 ≈ 0.667 倍なので黄金分割探索の方が収束が速い。
    計算量:
        O(log_{φ}((hi-lo)/eps)) 回の関数評価。
    使用例:
        x, v = golden_section_search_max(lambda x: -(x-3)**2+9, 0.0, 10.0)
        print(x, v)  # 約 3.0, 9.0
    """
    _GOLDEN_RATIO = (1 + 5 ** 0.5) / 2  # ≈ 1.6180339887
    m1 = hi - (hi - lo) / _GOLDEN_RATIO
    m2 = lo + (hi - lo) / _GOLDEN_RATIO
    f1, f2 = f(m1), f(m2)
    while hi - lo > eps:
        if f1 < f2:
            lo = m1
            m1, f1 = m2, f2
            m2 = lo + (hi - lo) / _GOLDEN_RATIO
            f2 = f(m2)
        else:
            hi = m2
            m2, f2 = m1, f1
            m1 = hi - (hi - lo) / _GOLDEN_RATIO
            f1 = f(m1)
    x = (lo + hi) / 2
    return x, f(x)


def golden_section_search_min(f, lo: float, hi: float, eps: float = 1e-9) -> tuple[float, float]:
    """概要:
        黄金分割探索で実数域の単峰関数（下に凸）の最小値を求める。
    入力:
        f   : 探索対象の関数（float -> float）。
        lo  (float): 探索区間の左端。
        hi  (float): 探索区間の右端。
        eps (float): 収束判定の許容誤差（デフォルト 1e-9）。
    出力:
        tuple[float, float]: (最小値を取るx（近似）, f(x)の最小値（近似））。
    制約:
        f が [lo, hi] 上で単峰（下に凸）であること。
    補足:
        黄金分割探索は前ステップの評価値を再利用するため
        三分探索より収束が速い（区間縮小率 ≈ 0.618 vs 0.667）。
    計算量:
        O(log_{φ}((hi-lo)/eps)) 回の関数評価。
    使用例:
        x, v = golden_section_search_min(lambda x: (x-3)**2, 0.0, 10.0)
        print(x, v)  # 約 3.0, 0.0
    """
    _GOLDEN_RATIO = (1 + 5 ** 0.5) / 2  # ≈ 1.6180339887
    m1 = hi - (hi - lo) / _GOLDEN_RATIO
    m2 = lo + (hi - lo) / _GOLDEN_RATIO
    f1, f2 = f(m1), f(m2)
    while hi - lo > eps:
        if f1 > f2:
            lo = m1
            m1, f1 = m2, f2
            m2 = lo + (hi - lo) / _GOLDEN_RATIO
            f2 = f(m2)
        else:
            hi = m2
            m2, f2 = m1, f1
            m1 = hi - (hi - lo) / _GOLDEN_RATIO
            f1 = f(m1)
    x = (lo + hi) / 2
    return x, f(x)

def fibonacci_search_int_max(f, lo: int, hi: int) -> tuple[int, int]:
    """概要:
        整数域の単峰関数（上に凸）に対してフィボナッチ探索で最大値を求める。
        黄金分割探索の離散（整数）版であり、前ステップの関数評価値を再利用する
        ことで、通常の三分探索に比べて関数評価回数を大幅に削減する。
    入力:
        f   : 探索対象の関数（int -> 比較可能な値）。
        lo  (int): 探索区間の左端（inclusive）。
        hi  (int): 探索区間の右端（inclusive）。
    出力:
        tuple[int, int]: (最大値を取るx, f(x)の最大値)。
    制約:
        f が lo..hi 上で単峰（上に凸）であること。
    補足:
        初回の2点評価以降は各ステップ1回の関数評価で区間を約 0.618 倍に縮小する。
        三分探索（毎回2回評価、縮小率 0.667）に比べ、評価回数は半分以下になる。
    計算量:
        O(log_{φ}(hi - lo)) 回の関数評価（φ ≈ 1.618）。
    使用例:
        # f(x) = -(x-3)^2 + 9  (x=3 で最大値 9)
        x, v = fibonacci_search_int_max(lambda x: -(x-3)**2 + 9, 0, 10)
        print(x, v)  # 3 9
    """
    if lo >= hi:
        return lo, f(lo)

    # 仮想境界値: 区間外 (x > hi) の評価要求に対しては -inf を返す番兵
    _INF = float("inf")

    def eval_f(x: int):
        return -_INF if x > hi else f(x)

    # fib[k] >= hi - lo を満たす最小のフィボナッチ数を生成
    fib = [0, 1]
    while fib[-1] < hi - lo:
        fib.append(fib[-1] + fib[-2])
    while len(fib) < 5:
        fib.append(fib[-1] + fib[-2])

    k = len(fib) - 1
    offset = lo

    # 初期の2つの内分点とその評価
    m1 = offset + fib[k - 2]
    m2 = offset + fib[k - 1]
    f1 = eval_f(m1)
    f2 = eval_f(m2)

    # フィボナッチ数の自己相似性を利用した区間縮小
    while k > 2:
        if f1 < f2:
            # 最大値は [m1, offset + fib[k]] に存在
            offset = m1
            m1, f1 = m2, f2
            k -= 1
            m2 = offset + fib[k - 1]
            f2 = eval_f(m2)
        else:
            # 最大値は [offset, m2] に存在
            m2, f2 = m1, f1
            k -= 1
            m1 = offset + fib[k - 2]
            f1 = eval_f(m1)

    # 残った候補点から真の最大値を特定
    candidates = [lo, hi, offset, m1, m2]
    best_x = lo
    best_v = f(lo)
    for x in set(candidates):
        if lo <= x <= hi:
            v = f(x)
            if v > best_v:
                best_v = v
                best_x = x

    return best_x, best_v


def fibonacci_search_int_min(f, lo: int, hi: int) -> tuple[int, int]:
    """概要:
        整数域の単峰関数（下に凸）に対してフィボナッチ探索で最小値を求める。
        黄金分割探索の離散（整数）版であり、前ステップの関数評価値を再利用する
        ことで、通常の三分探索に比べて関数評価回数を大幅に削減する。
    入力:
        f   : 探索対象の関数（int -> 比較可能な値）。
        lo  (int): 探索区間の左端（inclusive）。
        hi  (int): 探索区間の右端（inclusive）。
    出力:
        tuple[int, int]: (最小値を取るx, f(x)の最小値)。
    制約:
        f が lo..hi 上で単峰（下に凸）であること。
    補足:
        初回の2点評価以降は各ステップ1回の関数評価で区間を約 0.618 倍に縮小する。
        三分探索（毎回2回評価、縮小率 0.667）に比べ、評価回数は半分以下になる。
    計算量:
        O(log_{φ}(hi - lo)) 回の関数評価（φ ≈ 1.618）。
    使用例:
        # f(x) = (x-3)^2  (x=3 で最小値 0)
        x, v = fibonacci_search_int_min(lambda x: (x-3)**2, 0, 10)
        print(x, v)  # 3 0
    """
    if lo >= hi:
        return lo, f(lo)

    # 仮想境界値: 区間外 (x > hi) の評価要求に対しては +inf を返す番兵
    _INF = float("inf")

    def eval_f(x: int):
        return _INF if x > hi else f(x)

    # fib[k] >= hi - lo を満たす最小のフィボナッチ数を生成
    fib = [0, 1]
    while fib[-1] < hi - lo:
        fib.append(fib[-1] + fib[-2])
    while len(fib) < 5:
        fib.append(fib[-1] + fib[-2])

    k = len(fib) - 1
    offset = lo

    # 初期の2つの内分点とその評価
    m1 = offset + fib[k - 2]
    m2 = offset + fib[k - 1]
    f1 = eval_f(m1)
    f2 = eval_f(m2)

    # フィボナッチ数の自己相似性を利用した区間縮小
    while k > 2:
        if f1 > f2:
            # 最小値は [m1, offset + fib[k]] に存在
            offset = m1
            m1, f1 = m2, f2
            k -= 1
            m2 = offset + fib[k - 1]
            f2 = eval_f(m2)
        else:
            # 最小値は [offset, m2] に存在
            m2, f2 = m1, f1
            k -= 1
            m1 = offset + fib[k - 2]
            f1 = eval_f(m1)

    # 残った候補点から真の最小値を特定
    candidates = [lo, hi, offset, m1, m2]
    best_x = lo
    best_v = f(lo)
    for x in set(candidates):
        if lo <= x <= hi:
            v = f(x)
            if v < best_v:
                best_v = v
                best_x = x

    return best_x, best_v

# ============================================================
# 区間マージ
# ============================================================

def merge_intervals(intervals: list[tuple[int, int]], half_open: bool = True) -> list[tuple[int, int]]:
    """概要:
        区間のリストをマージして最小個数の区間リストを返す。
    入力:
        intervals (list[tuple[int, int]]): 区間 (L, R) のリスト。
        half_open (bool): True なら右半開区間 [L,R)、False なら閉区間 [L,R]。
    出力:
        list[tuple[int, int]]: マージ済みの区間リスト（Lで昇順ソート済み）。
    補足:
        右半開区間では [1,3) と [3,5) はマージされて [1,5) になる（L<=curR でマージ）。
        閉区間では [1,3] と [4,5] はマージされない（L<=curR+1 でマージ）。
        計算量は O(N log N)（ソートが支配的）。
    使用例:
        ivs = [(1,3),(2,5),(7,9)]
        print(merge_intervals(ivs))  # [(1,5),(7,9)]
    """
    if not intervals:
        return []
    intervals = sorted(intervals)
    curL, curR = intervals[0]
    result = []
    threshold = 0 if half_open else 1
    for L, R in intervals[1:]:
        if L <= curR + threshold:
            curR = max(curR, R)
        else:
            result.append((curL, curR))
            curL, curR = L, R
    result.append((curL, curR))
    return result

# ============================================================
# 座標圧縮
# ============================================================

def compress(arr: list[int]) -> tuple[dict[int, int], list[int]]:
    """概要:
        配列値を連番インデックスへ写像する座標圧縮を行う。
    入力:
        arr (list[int]): 圧縮対象配列。
    出力:
        tuple[dict[int, int], list[int]]: (値→index辞書, 昇順ユニーク値リスト)。
    補足:
        元値への逆引きは第2戻り値を使う。計算量は O(nlogn)。
    """
    xs = sorted(set(arr))
    mp = {x: i for i, x in enumerate(xs)}
    return mp, xs

def compress_list(arr: list[int]) -> list[int]:
    """概要:
        配列を座標圧縮した後のインデックス配列を返す。
    入力:
        arr (list[int]): 圧縮対象配列。
    出力:
        list[int]: arr の各要素を圧縮インデックスへ変換した配列。
    補足:
        `compress` を内部利用する。計算量は O(nlogn)。
    """
    mp, _ = compress(arr)
    return [mp[x] for x in arr]


def inversion_count(arr: list[int]) -> int:
    """概要:
        配列の転倒数（i<j かつ arr[i]>arr[j] の組数）を求める。
    入力:
        arr (list[int]): 対象配列。
    出力:
        int: 転倒数。
    補足:
        座標圧縮 + BIT で O(n log n)。重複値にも対応。
    """
    if not arr:
        return 0
    c = compress_list(arr)
    n = len(c)
    bit = BIT(max(c) + 1)
    inv = 0
    for i, x in enumerate(c):
        leq = bit.sum(x)
        inv += i - leq
        bit.add(x, 1)
    return inv

# ============================================================
# ダブリング
# ============================================================

def build_doubling(
    n: int,
    nxt: list[int],
    log: int = 30,
    weight: list[int] | None = None,
    op = None,
    e = None,
) -> tuple[list[list[int]], list[list[int]] | None]:
    """概要:
        関数的グラフに対してダブリングテーブルを構築する。
        オプションで「各ステップに付随する値（重み）」の累積テーブルも同時構築できる。

    入力:
        n      (int)            : 頂点数（0-indexed）。
        nxt    (list[int])      : nxt[v] = v から 1 ステップ先（0-indexed）。
        log    (int)            : テーブル段数。2^log >= クエリ最大ステップ数 を満たすこと。
        weight (list[int]|None) : weight[v] = v を出発した際に加算される値。None なら無効。
        op     (callable|None)  : 重みの結合演算（例: operator.add, max）。None なら加算。
        e      (any|None)       : 重みの単位元（例: 0, -INF）。None なら 0。

    出力:
        tuple:
            [0] doubling[k][v]     : v から 2^k ステップ後の頂点。
            [1] acc[k][v]          : v から 2^k ステップで累積した重み。weight=None なら None。

    計算量:
        O(N * log)

    使用例（頂点のみ）:
        nxt = [A[i] - 1 for i in range(N)]
        db, _ = build_doubling(N, nxt)
        v = doubling_query(db, X-1, Y)

    使用例（頂点 + 累積コスト）:
        nxt = [to_list[v] for v in range(N)]
        w   = [cost_list[v] for v in range(N)]
        db, ac = build_doubling(N, nxt, weight=w, op=operator.add, e=0)
        v, total_cost = doubling_query_with_weight(db, ac, operator.add, 0, X-1, Y)
    """
    if op is None:
        import operator
        op = operator.add
    if e is None:
        e = 0

    doubling = [[0] * n for _ in range(log)]
    doubling[0] = list(nxt)

    if weight is not None:
        acc = [[e] * n for _ in range(log)]
        acc[0] = list(weight)
    else:
        acc = None

    for k in range(1, log):
        for v in range(n):
            mid = doubling[k-1][v]
            doubling[k][v] = doubling[k-1][mid]
            if acc is not None:
                acc[k][v] = op(acc[k-1][v], acc[k-1][mid])

    return doubling, acc


def doubling_query(
    doubling: list[list[int]],
    v: int,
    y: int,
) -> int:
    """概要:
        ダブリングテーブルを用いて v から y ステップ後の頂点を返す。

    入力:
        doubling : build_doubling の戻り値 [0]。
        v        : 始点（0-indexed）。
        y        : ステップ数（0 以上）。

    出力:
        int: y ステップ後の頂点（0-indexed）。

    計算量:
        L = len(doubling) とすると O(L)。y のビット数ではなく、
        テーブルの全段数を走査する。
    """
    log = len(doubling)
    for k in range(log):
        if (y >> k) & 1:
            v = doubling[k][v]
    return v


def doubling_query_with_weight(
    doubling: list[list[int]],
    acc: list[list[int]],
    op,
    e,
    v: int,
    y: int,
) -> tuple[int, ...]:
    """概要:
        ダブリングテーブルを用いて v から y ステップ後の頂点と累積重みを返す。

    入力:
        doubling : build_doubling の戻り値 [0]。
        acc      : build_doubling の戻り値 [1]（weight 指定時のみ有効）。
        op       : 重みの結合演算（build_doubling と同一のものを渡す）。
        e        : 重みの単位元（build_doubling と同一のものを渡す）。
        v        : 始点（0-indexed）。
        y        : ステップ数（0 以上）。

    出力:
        tuple[int, any]: (y ステップ後の頂点, 累積重み)。

    計算量:
        L = len(doubling) とすると O(L)（op のコストを O(1) と仮定）。
        y のビット数ではなく、テーブルの全段数を走査する。
    """
    log = len(doubling)
    total = e
    for k in range(log):
        if (y >> k) & 1:
            total = op(total, acc[k][v])
            v = doubling[k][v]
    return v, total

# ============================================================
# Kadane's Algorithm（最大・最小・循環最大部分配列和）
# ============================================================

def kadane_max(arr: list[int]) -> tuple[int, int, int]:
    """概要:
        最大部分配列和（Kadane's Algorithm）。
        空でない連続部分配列 arr[l:r+1] の和の最大値を O(N) で求める。
    入力:
        arr (list[int]): 対象配列。空でないこと。
    出力:
        tuple[int, int, int]: (最大和, 開始インデックス l, 終了インデックス r)。
                               arr[l:r+1] が最大部分配列（複数あれば最左を返す）。
    補足:
        全要素が負の場合は最大の単一要素を返す。
        部分配列のインデックスが不要なら戻り値の [0] だけ使えばよい。
    使用例:
        A = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        val, l, r = kadane_max(A)
        print(val, l, r)  # 6, 3, 6  (A[3:7] = [4,-1,2,1])
    """
    best      = arr[0]
    cur       = arr[0]
    best_l    = 0
    best_r    = 0
    cur_l     = 0

    for i in range(1, len(arr)):
        if cur + arr[i] < arr[i]:
            # ここから新たに始めるほうが良い
            cur   = arr[i]
            cur_l = i
        else:
            cur += arr[i]

        if cur > best:
            best   = cur
            best_l = cur_l
            best_r = i

    return best, best_l, best_r


def kadane_min(arr: list[int]) -> tuple[int, int, int]:
    """概要:
        最小部分配列和（Kadane's Algorithm の最小版）。
        空でない連続部分配列 arr[l:r+1] の和の最小値を O(N) で求める。
    入力:
        arr (list[int]): 対象配列。空でないこと。
    出力:
        tuple[int, int, int]: (最小和, 開始インデックス l, 終了インデックス r)。
    補足:
        最大版と符号を反転させた実装。全要素が正の場合は最小の単一要素を返す。
    使用例:
        A = [2, -1, 3, -4, 2, -1, 2, 1, -5]
        val, l, r = kadane_min(A)
        print(val, l, r)  # -5, 8, 8
    """
    best   = arr[0]
    cur    = arr[0]
    best_l = 0
    best_r = 0
    cur_l  = 0

    for i in range(1, len(arr)):
        if cur + arr[i] > arr[i]:
            cur   = arr[i]
            cur_l = i
        else:
            cur += arr[i]

        if cur < best:
            best   = cur
            best_l = cur_l
            best_r = i

    return best, best_l, best_r


def kadane_circular_max(arr: list[int]) -> int:
    """概要:
        循環配列における最大部分配列和。
        arr を円環とみなしたとき、連続部分配列の和の最大値を O(N) で求める。
    入力:
        arr (list[int]): 対象配列。空でないこと。
    出力:
        int: 最大部分配列和。
    補足:
        考え方:
            ケース1: 最大部分配列が「折り返しを含まない」→ 通常の kadane_max と同じ。
            ケース2: 最大部分配列が「折り返しを含む」
                    → 残り（除外）部分が最小部分配列 = total - kadane_min の値が答え。
        全要素が負の場合は折り返しを使わない通常の最大値を返す（ケース2は空になるため）。
    使用例:
        A = [8, -1, 3, -2]
        print(kadane_circular_max(A))  # 12  (8 + 3 + (-2) + (-1) の折り返し = 12 ではなく 8+3+fold)
        # A = [5, -3, 5]
        print(kadane_circular_max([5, -3, 5]))  # 10  ([5,-3,5] 折り返して 5+5=10)
    """
    total    = sum(arr)
    max_val  = kadane_max(arr)[0]
    min_val  = kadane_min(arr)[0]

    # 全部が負のケースでは total - min_val が 0（空配列）になるので除外
    if max_val < 0:
        return max_val

    return max(max_val, total - min_val)

# ============================================================
# 単調スタック
# ============================================================

def prev_greater(A: list[int]) -> list[int]:
    """概要:
        各要素に対して「直近の自分より大きい要素のインデックス」を返す。
    入力:
        A (list[int]): 対象配列（0-indexed）。
    出力:
        list[int]: res[i] = A[i] より大きい直近左側の要素のインデックス。
        存在しない場合は -1。
    補足:
        単調減少スタックを使い O(N)。
        「d日目の起算日」「Next Greater Element の左版」などに利用できる。
    使用例:
        A = [3, 1, 4, 1, 5]
        print(prev_greater(A))  # [-1, 0, -1, 2, -1]
    """
    n = len(A)
    res = [-1] * n
    stack = []
    for i in range(n):
        while stack and A[stack[-1]] <= A[i]:
            stack.pop()
        if stack:
            res[i] = stack[-1]
        stack.append(i)
    return res

def next_greater(A: list[int]) -> list[int]:
    """概要:
        各要素に対して「直近の自分より大きい要素のインデックス」を右側から返す。
    入力:
        A (list[int]): 対象配列（0-indexed）。
    出力:
        list[int]: res[i] = A[i] より大きい直近右側の要素のインデックス。
        存在しない場合は -1。
    補足:
        単調減少スタックを右から走査して O(N)。
    使用例:
        A = [3, 1, 4, 1, 5]
        print(next_greater(A))  # [2, 2, 4, 4, -1]
    """
    n = len(A)
    res = [-1] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and A[stack[-1]] <= A[i]:
            stack.pop()
        if stack:
            res[i] = stack[-1]
        stack.append(i)
    return res

def prev_smaller(A: list[int]) -> list[int]:
    """概要:
        各要素に対して「直近の自分より小さい要素のインデックス」を返す。
    入力:
        A (list[int]): 対象配列（0-indexed）。
    出力:
        list[int]: res[i] = A[i] より小さい直近左側の要素のインデックス。
        存在しない場合は -1。
    補足:
        単調増加スタックを使い O(N)。
        「ヒストグラム最大長方形」などの前処理に利用できる。
    """
    n = len(A)
    res = [-1] * n
    stack = []
    for i in range(n):
        while stack and A[stack[-1]] >= A[i]:
            stack.pop()
        if stack:
            res[i] = stack[-1]
        stack.append(i)
    return res

def next_smaller(A: list[int]) -> list[int]:
    """概要:
        各要素に対して「直近の自分より小さい要素のインデックス」を右側から返す。
    入力:
        A (list[int]): 対象配列（0-indexed）。
    出力:
        list[int]: res[i] = A[i] より小さい直近右側の要素のインデックス。
        存在しない場合は -1。
    補足:
        単調増加スタックを右から走査して O(N)。
    """
    n = len(A)
    res = [-1] * n
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and A[stack[-1]] >= A[i]:
            stack.pop()
        if stack:
            res[i] = stack[-1]
        stack.append(i)
    return res

# ============================================================
# スライドウィンドウ最大・最小（単調デック）
# ============================================================

def sliding_window_max(arr: list[int], k: int) -> list[int]:
    """概要:
        長さ k のスライディングウィンドウ内の最大値を全て求める。
    入力:
        arr (list[int]): 対象配列（0-indexed）。
        k (int): ウィンドウサイズ。
    出力:
        list[int]: 長さ len(arr)-k+1 の最大値列。
    補足:
        単調減少デックを使用し計算量は O(N)。
    使用例:
        arr = [1, 3, 0, 2, 4]
        print(sliding_window_max(arr, 3))  # [3, 3, 4]
    """
    n = len(arr)
    if k <= 0 or k > n:
        raise ValueError("requires 1 <= k <= len(arr)")
    dq = deque()
    result = []
    for i in range(n):
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            while dq[0] < i - k + 1:
                dq.popleft()
            result.append(arr[dq[0]])
    return result

def sliding_window_min(arr: list[int], k: int) -> list[int]:
    """概要:
        長さ k のスライディングウィンドウ内の最小値を全て求める。
    入力:
        arr (list[int]): 対象配列（0-indexed）。
        k (int): ウィンドウサイズ。
    出力:
        list[int]: 長さ len(arr)-k+1 の最小値列。
    補足:
        単調増加デックを使用し計算量は O(N)。
    使用例:
        arr = [1, 3, 0, 2, 4]
        print(sliding_window_min(arr, 3))  # [0, 0, 0]
    """
    n = len(arr)
    if k <= 0 or k > n:
        raise ValueError("requires 1 <= k <= len(arr)")
    dq = deque()
    result = []
    for i in range(n):
        while dq and arr[dq[-1]] >= arr[i]:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            while dq[0] < i - k + 1:
                dq.popleft()
            result.append(arr[dq[0]])
    return result

def count_subarrays_range_le(arr: list[int], limit: int) -> int:
    """概要:
        変動幅（max - min）が limit 以下の部分配列の個数を返す。
    入力:
        arr (list[int]): 対象配列（0-indexed）。
        limit (int): 変動幅の上限。負の場合は 0 を返す。
    出力:
        int: max(arr[l:r+1]) - min(arr[l:r+1]) <= limit を満たす (l, r) の個数。
    補足:
        単調デックを2本使ったスライディングウィンドウで O(N)。
        「変動幅がちょうど K の区間数」は
        count_subarrays_range_le(arr, K) - count_subarrays_range_le(arr, K-1) で求まる。
    使用例:
        A = [1, 3, 2, 4]
        print(count_subarrays_range_le(A, 2))  # 8
        print(count_subarrays_range_le(A, 2) - count_subarrays_range_le(A, 1))  # 変動幅ちょうど2の個数
    """
    if limit < 0:
        return 0
    n = len(arr)
    max_dq = deque()  # 単調減少（最大値管理）
    min_dq = deque()  # 単調増加（最小値管理）
    l = 0
    ans = 0
    for r in range(n):
        while max_dq and arr[max_dq[-1]] <= arr[r]:
            max_dq.pop()
        max_dq.append(r)
        while min_dq and arr[min_dq[-1]] >= arr[r]:
            min_dq.pop()
        min_dq.append(r)
        while arr[max_dq[0]] - arr[min_dq[0]] > limit:
            l += 1
            if max_dq[0] < l:
                max_dq.popleft()
            if min_dq[0] < l:
                min_dq.popleft()
        ans += r - l + 1
    return ans

# ============================================================
# ユーティリティ
# ============================================================

def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    """概要:
        2点間のマンハッタン距離を返す。
    入力:
        x1, y1, x2, y2 (int): 2点座標。
    出力:
        int: |x1-x2| + |y1-y2|。
    """
    return abs(x1 - x2) + abs(y1 - y2)

def chebyshev(x1: int, y1: int, x2: int, y2: int) -> int:
    """概要:
        2点間のチェビシェフ距離を返す。
    入力:
        x1, y1, x2, y2 (int): 2点座標。
    出力:
        int: max(|x1-x2|, |y1-y2|)。
    """
    return max(abs(x1 - x2), abs(y1 - y2))

def rank_data(arr: list, reverse: bool = False, competition: bool = True) -> list[int]:
    """概要:
        配列の各要素の順位を返す。
    入力:
        arr (list): 順位付けする配列。
        reverse (bool): True なら大きい順、False なら小さい順。
        competition (bool): True なら重複時に同順位（1, 2, 2, 4）、False なら（1, 2, 2, 3）。
    出力:
        list[int]: 各要素の順位（1-indexed）。
    補足:
        デフォルトは小さい順・重複同順位（競技順位）。計算量は O(nlogn)。
    """
    n = len(arr)
    if n == 0: return []
    
    # 元のインデックスと値を保持してソート
    indexed_arr = sorted(enumerate(arr), key=lambda x: x[1], reverse=reverse)
    
    ranks = [0] * n
    curr_rank = 1
    for i in range(n):
        if i > 0:
            if indexed_arr[i][1] == indexed_arr[i-1][1]:
                # 同値の場合
                if competition:
                    # 競技順位（1, 2, 2, 4）: そのまま
                    pass
                else:
                    # 密な順位（1, 2, 2, 3）: 前の順位を維持（更新しない）
                    pass
            else:
                # 異なる値の場合
                if competition:
                    curr_rank = i + 1
                else:
                    curr_rank += 1
        
        ranks[indexed_arr[i][0]] = curr_rank
        
    return ranks

def ceil_div(a: int, b: int) -> int:
    """概要:
        正整数同士の切り上げ除算を返す。
    入力:
        a (int): 被除数。
        b (int): 除数（正）。
    出力:
        int: ceil(a / b)。
    補足:
        想定は a, b > 0。計算量は O(1)。
    """
    return (a + b - 1) // b

def floor_sum(n: int, m: int, a: int, b: int) -> int:
    """概要:
        Σ_{i=0}^{n-1} floor((a*i + b) / m) を高速に計算する。
    入力:
        n, m, a, b (int): 式のパラメータ。
    出力:
        int: 総和値。
    補足:
        ACL由来の再帰的変形を使い O(log m) 程度で処理する（整数演算を O(1) と仮定）。
    """
    if n < 0 or m <= 0:
        raise ValueError("requires n >= 0 and m > 0")
    ans = 0
    if a < 0:
        a_mod = a % m
        ans -= n * (n - 1) // 2 * ((a_mod - a) // m)
        a = a_mod
    if b < 0:
        b_mod = b % m
        ans -= n * ((b_mod - b) // m)
        b = b_mod
    while True:
        if a >= m:
            ans += n * (n - 1) // 2 * (a // m)
            a %= m
        if b >= m:
            ans += n * (b // m)
            b %= m
        y_max = a * n + b
        if y_max < m:
            return ans
        n, b, m, a = y_max // m, y_max % m, a, m

def rotate_90(grid: list[list]) -> list[list]:
    """概要:
        2次元配列を時計回りに90度回転して返す。
    入力:
        grid (list[list]): 元グリッド。
    出力:
        list[list]: 回転後グリッド。
    補足:
        計算量は O(HW)。
    """
    H, W = len(grid), len(grid[0])
    return [[grid[H - 1 - j][i] for j in range(H)] for i in range(W)]

def transpose(grid: list[list]) -> list[list]:
    """概要:
        2次元配列の転置を返す。
    入力:
        grid (list[list]): 元グリッド。
    出力:
        list[list]: 転置後グリッド。
    補足:
        計算量は O(HW)。
    """
    return [list(row) for row in zip(*grid)]


def bit_full_search(n: int):
    """概要:
        n 要素集合の部分集合をビットマスクで全列挙するジェネレータ。
    入力:
        n (int): 要素数。
    出力:
        Iterator[int]: 0 から (1<<n)-1 のビットマスク。
    補足:
        `for bit in bit_full_search(n):` で利用する。全列挙の計算量は O(2^n)。
    """
    for bit in range(1 << n):
        yield bit


def bit_indices(bit: int, n: int) -> list[int]:
    """概要:
        ビットマスクで立っているビット位置を列挙する。
    入力:
        bit (int): ビットマスク。
        n (int): 判定するビット長。
    出力:
        list[int]: 立っている位置（0-indexed）の配列。
    補足:
        計算量は O(n)。
    """
    return [i for i in range(n) if (bit >> i) & 1]


def submasks(mask: int):
    """概要:
        与えたマスクの全部分マスクを降順で列挙するジェネレータ。
    入力:
        mask (int): 元マスク。
    出力:
        Iterator[int]: mask, ..., 0 の順で全部分マスク。
    補足:
        `s = (s - 1) & mask` の定番テクニックを使用する。計算量は O(2^k)（k は立っているビット数）。
    """
    s = mask
    while True:
        yield s
        if s == 0:
            break
        s = (s - 1) & mask

def ternary_full_search(n: int):
    """概要:
        n 要素集合の各要素を 3 択（0/1/2）で全列挙するジェネレータ。
        例: 集合Aに属す / 集合Bに属す / どちらでもない、など。
    入力:
        n (int): 要素数。
    出力:
        Iterator[list[int]]: 各要素の選択（0,1,2）を表すリスト。
    補足:
        生成個数は 3^n、各結果の構築に O(n) かかるため、全生成の時間計算量は
        O(n * 3^n)、追加メモリは O(n)。n <= 15 程度が実用範囲。
    使用例:
        for choices in ternary_full_search(n):
            group = [[], [], []]
            for i, c in enumerate(choices):
                group[c].append(i)
            # group[0]: 択0の要素, group[1]: 択1の要素, group[2]: 択2の要素
    """
    for bit in range(3 ** n):
        choices = [(bit // (3 ** i)) % 3 for i in range(n)]
        yield choices

def digit_sum(x: int) -> int:
    """概要:
        整数 x の十進数各桁の和を返す。
    入力:
        x (int): 非負整数。
    出力:
        int: 各桁の数字の和。
    補足:
        計算量は O(桁数)。
    """
    s = 0
    while x:
        s += x % 10
        x //= 10
    return s

def euclidean_dist2(x1: int, y1: int, x2: int, y2: int) -> int:
    """概要:
        2点間のユークリッド距離の二乗を返す（整数計算、誤差なし）。
    入力:
        x1, y1, x2, y2 (int): 2点座標。
    出力:
        int: (x1-x2)^2 + (y1-y2)^2。
    補足:
        sqrt を使わないため浮動小数点誤差がない。
        距離比較は dist2 <= D*D の形で使う。計算量は O(1)。
    使用例:
        if euclidean_dist2(x1, y1, x2, y2) <= D * D:
            # 距離D以内の処理
    """
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

# ============================================================
# 記録して出力
# ============================================================

class Output:
    """概要:
        !! 高速 print が存在する為非推奨 !!
        出力文字列をバッファリングして最後にまとめて出力する補助クラス。

    メソッド:
        add(*args, sep=' '): 1行分を追加する。
        extend(iterable): 要素列を複数行として追加する。
        grid(grid, sep=' '): 2次元配列を行単位で追加する。
        yes(cond, yes='Yes', no='No'): 条件に応じた文字列を追加する。
        flush(...): まとめて出力しバッファをクリアする。
        get(sep='\n'): 現在バッファを文字列として取得する。

    計算量:
        add/extend/grid は生成する総文字数を S として O(S)、yes は O(1)、
        flush/get はバッファ総文字数を S として O(S)、__len__ は O(1)。

    補足:
        大量出力時の `print` 連打を避けたいときに有効。
    """
    def __init__(self):
        self.buffer = []

    def add(self, *args, sep: str = ' ') -> None:
        """引数を一つの行(文字列)として結合して記録"""
        self.buffer.append(sep.join(map(str, args)))

    def extend(self, iterable) -> None:
        """イテラブルの各要素をそれぞれ一行として記録"""
        for item in iterable:
            if isinstance(item, (list, tuple, range)):
                self.add(*item)
            else:
                self.add(item)

    def grid(self, grid: list[list], sep: str = ' ') -> None:
        """2次元配列を各行を空白区切りなどで記録"""
        for row in grid:
            self.add(*row, sep=sep)

    def yes(self, cond: bool, yes: str = "Yes", no: str = "No") -> None:
        """条件に応じてYes/Noを記録"""
        self.add(yes if cond else no)

    def flush(self, sep: str = '\n', end: str = '\n', file=sys.stdout) -> None:
        """記録した内容を結合して出力し、バッファを空にする"""
        if self.buffer:
            file.write(sep.join(self.buffer) + end)
            self.buffer = []

    def get(self, sep: str = '\n') -> str:
        """記録した内容を結合した文字列を返す"""
        return sep.join(self.buffer)

    def __len__(self) -> int:
        return len(self.buffer)

# ============================================================
# デバッグ
# ============================================================
# AtCoder提出時は自動で無力化
if "ATCODER" not in os.environ and "ONLINE_JUDGE" not in os.environ:
    def debug(*args, sep=' ', end='\n', flush=False) -> None:
        """デバッグ出力（標準エラー）"""
        print("[DEBUG]", *args, sep=sep, end=end, file=sys.stderr, flush=flush)
else:
    def debug(*args, **kwargs) -> None:
        pass

# ============================================================
# main
# ============================================================

def main() -> None:
    # ここに解答を書く
    N = INT()
    print(ans)


if __name__ == "__main__":
    main()
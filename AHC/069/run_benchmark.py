import os
import re
import sys
import glob
import random
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# 設定項目
# ==========================================
NUM_TEST_CASES = 15             # 評価に使用するケース数
TIME_LIMIT = 100.0                # 実行時間制限（秒）
NUM_WORKERS = 3                 # 並列実行数 (CPUコア数に合わせて調整)

TOOLS_DIR = Path("tools_x86_64-pc-windows-gnu")
IN_DIR = TOOLS_DIR / "in"
TESTER_EXE = TOOLS_DIR / "tester.exe"

# 検索対象のCPPファイルパターン (.py は除外)
SOLVER_PATTERN = "solve*.cpp"
# コンパイルコマンド
COMPILER_CMD = "g++ -O2 {src} -o {exe}"

# ==========================================

def compile_solvers():
    """solve*.cpp を探して必要に応じてコンパイルする"""
    cpp_files = sorted(glob.glob(SOLVER_PATTERN))
    solvers = []

    for cpp in cpp_files:
        exe_name = Path(cpp).stem + ".exe"
        exe_path = Path(exe_name)

        # .exe が無い、または .cpp の更新日時が新しい場合は再コンパイル
        if not exe_path.exists() or exe_path.stat().st_mtime < Path(cpp).stat().st_mtime:
            print(f"[Compile] Compiling {cpp} -> {exe_name}...")
            cmd = COMPILER_CMD.format(src=cpp, exe=exe_name)
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"[Error] Failed to compile {cpp}:\n{res.stderr}")
                continue

        solvers.append(exe_path)

    return solvers

def run_single_test(args):
    """1ケースに対する実行処理"""
    solver_exe, in_file = args
    abs_solver_path = str(solver_exe.resolve())
    cmd = [str(TESTER_EXE), abs_solver_path]

    try:
        with open(in_file, "r") as infile:
            res = subprocess.run(
                cmd,
                stdin=infile,
                stdout=subprocess.DEVNULL, # 出力ファイル生成をスキップ
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                # tester.exe起動オーバーヘッドを考慮し、0.5秒のバッファを追加
                timeout=TIME_LIMIT + 0.5
            )
        
        # tester.exe や solver がエラー終了した場合 (RE / WA など)
        if res.returncode != 0:
            err_line = res.stderr.strip().splitlines()[0] if res.stderr else "Unknown error"
            print(f"\n[WA/RE] {solver_exe.name} failed on {in_file.name}: {err_line}")
            return 0

        # tester.exe の stderr から Score を抽出
        match = re.search(r"Score\s*=\s*(\d+)", res.stderr)
        if match:
            return int(match.group(1))
        
        numbers = re.findall(r"\d+", res.stderr)
        if numbers:
            return int(numbers[-1])
            
        return 0

    except subprocess.TimeoutExpired:
        print(f"\n[TLE] {solver_exe.name} timed out on {in_file.name} (>{TIME_LIMIT}s)")
        return 0
    except Exception as e:
        print(f"\n[Error] System error running {solver_exe.name} on {in_file.name}: {e}")
        return 0

def main():
    if not TESTER_EXE.exists():
        print(f"[Error] {TESTER_EXE} が見つかりません。")
        sys.exit(1)

    # 1. コンパイルとソルバーの抽出
    solvers = compile_solvers()
    if not solvers:
        print("[Error] 実行可能なソルバーが見つかりませんでした。")
        sys.exit(1)

    # 2. テストケースの選定 (in/*.txt から指定数ランダム選択)
    all_in_files = sorted(list(IN_DIR.glob("*.txt")))
    if len(all_in_files) < NUM_TEST_CASES:
        selected_cases = all_in_files
    else:
        selected_cases = sorted(random.sample(all_in_files, NUM_TEST_CASES))

    print(f"==================================================")
    print(f" Solvers ({len(solvers)}): {[s.name for s in solvers]}")
    print(f" Test Cases ({len(selected_cases)}): {[c.name for c in selected_cases]}")
    print(f" Time Limit: {TIME_LIMIT} sec")
    print(f"==================================================\n")

    results = {}

    # 3. テストの全ソルバー並列実行
    for solver in solvers:
        print(f"Running {solver.name}...", end="", flush=True)
        tasks = [(solver, case_file) for case_file in selected_cases]
        
        scores = []
        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            scores = list(executor.map(run_single_test, tasks))

        avg_score = sum(scores) / len(scores) if scores else 0
        results[solver.name] = {
            "avg": avg_score,
            "max": max(scores) if scores else 0,
            "min": min(scores) if scores else 0,
            "sum": sum(scores),
            "scores": scores
        }
        print(" Done!")

    # 4. 平均スコア順にランキング付け (降順)
    sorted_ranking = sorted(results.items(), key=lambda x: x[1]["avg"], reverse=True)

    # 5. 結果テーブル表示
    print("\n" + "=" * 68)
    print(f"{'Rank':<5} | {'Solver':<15} | {'Average':<12} | {'Max':<10} | {'Min':<10}")
    print("-" * 68)
    
    for rank, (name, stats) in enumerate(sorted_ranking, start=1):
        print(f"{rank:<5} | {name:<15} | {stats['avg']:<12.1f} | {stats['max']:<10} | {stats['min']:<10}")
    
    print("=" * 68 + "\n")

if __name__ == "__main__":
    main()
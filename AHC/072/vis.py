import argparse
import glob
import os
import random
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# Windowsの文字化け対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, total=None, desc=""):
        return iterable

DEFAULT_VIS_PATH = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\vis.exe"
DEFAULT_IN_DIR = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\in"

# Windowsでバックグラウンド実行するためのフラグ（GUI起動を抑止）
NO_WINDOW_FLAG = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def sanitize_cmd(cmd_str: str) -> list[str]:
    """コマンド文字列を安全なリストに変換し、python抜け等を自動補完する"""
    parts = shlex.split(cmd_str, posix=False)
    if not parts:
        raise ValueError("実行コマンドが空です。")
    
    first = parts[0]
    # .py を直接指定された場合は python を補完
    if first.endswith(".py"):
        return [sys.executable] + parts
    
    return parts


def parse_score(output_str: str) -> int:
    match = re.search(r"Score\s*=\s*(\d+)", output_str, re.IGNORECASE)
    if match:
        return int(match.group(1))

    for line in output_str.strip().splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)

    numbers = re.findall(r"\d+", output_str)
    if numbers:
        return int(numbers[-1])

    raise ValueError(f"スコアをパースできませんでした:\n{output_str}")


def run_single_testcase(args_tuple):
    file_id, in_path, cmd_list, vis_path, timeout = args_tuple
    result = {
        "id": file_id,
        "score": 0,
        "elapsed": 0.0,
        "status": "OK",
        "error_msg": ""
    }

    start_time = time.time()
    try:
        # 1. 解答プログラムの実行 (shell=False, CREATE_NO_WINDOW で安全に起動)
        with open(in_path, "r", encoding="utf-8") as f_in:
            proc = subprocess.run(
                cmd_list,
                stdin=f_in,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=NO_WINDOW_FLAG,
                timeout=timeout
            )

        elapsed = time.time() - start_time
        result["elapsed"] = elapsed

        if proc.returncode != 0:
            result["status"] = "RE"
            result["error_msg"] = proc.stderr[:200]
            return result

        user_output = proc.stdout

        # 2. 一時ファイルに出力を書き出して vis.exe を呼び出す
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as tmp_out:
            tmp_out_path = tmp_out.name
            tmp_out.write(user_output)

        try:
            vis_cmd = [vis_path, in_path, tmp_out_path, "--no-vis"]
            vis_proc = subprocess.run(
                vis_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=NO_WINDOW_FLAG,
                timeout=10
            )

            if vis_proc.returncode != 0:
                result["status"] = "WA (Vis Error)"
                result["error_msg"] = (vis_proc.stderr or vis_proc.stdout)[:200]
                return result

            score = parse_score(vis_proc.stdout)
            result["score"] = score

        finally:
            if os.path.exists(tmp_out_path):
                try:
                    os.remove(tmp_out_path)
                except OSError:
                    pass

    except subprocess.TimeoutExpired:
        result["status"] = "TLE"
        result["elapsed"] = timeout
    except Exception as e:
        result["status"] = "Error"
        result["error_msg"] = str(e)

    return result


def print_summary(results):
    total_cases = len(results)
    valid_results = [r for r in results if r["status"] == "OK"]
    errors = [r for r in results if r["status"] != "OK"]

    print("\n" + "=" * 60)
    print("                    Execution Summary")
    print("=" * 60)
    print(f"Total Cases : {total_cases}")
    print(f"Success     : {len(valid_results)}")
    print(f"Failed      : {len(errors)}")

    if errors:
        print("\n--- Failed Cases ---")
        for err in errors[:10]:
            print(f"[{err['status']}] Case: {err['id']:04d} | Msg: {err['error_msg'].strip()}")
        if len(errors) > 10:
            print(f"... and {len(errors) - 10} more errors")

    if not valid_results:
        print("\n有効なスコアが得られませんでした。")
        return

    scores = [r["score"] for r in valid_results]
    times = [r["elapsed"] for r in valid_results]

    total_score = sum(scores)
    avg_score = statistics.mean(scores)
    med_score = statistics.median(scores)
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
    min_score = min(scores)
    max_score = max(scores)

    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    fastest_case = min(valid_results, key=lambda x: x["elapsed"])
    slowest_case = max(valid_results, key=lambda x: x["elapsed"])

    print("\n--- Score Statistics ---")
    print(f"Total Score : {total_score:,}")
    print(f"Average     : {avg_score:,.2f}")
    print(f"Median      : {med_score:,.2f}")
    print(f"Std Dev     : {std_score:,.2f}")
    print(f"Min Score   : {min_score:,} (Case: {min(valid_results, key=lambda x: x['score'])['id']:04d})")
    print(f"Max Score   : {max_score:,} (Case: {max(valid_results, key=lambda x: x['score'])['id']:04d})")

    print("\n--- Execution Time ---")
    print(f"Average Time: {avg_time:.3f} s")
    print(f"Min Time    : {min_time:.3f} s (Case: {fastest_case['id']:04d})")
    print(f"Max Time    : {max_time:.3f} s (Case: {slowest_case['id']:04d})")

    print("\n--- Score Distribution ---")
    bins = 10
    if min_score == max_score:
        print(f"All scores are {min_score}")
    else:
        step = (max_score - min_score) / bins
        hist = [0] * bins
        for s in scores:
            idx = min(int((s - min_score) / step), bins - 1)
            hist[idx] += 1

        max_bar_width = 30
        max_count = max(hist) if max(hist) > 0 else 1
        for i in range(bins):
            low = min_score + i * step
            high = min_score + (i + 1) * step
            bar = "#" * int((hist[i] / max_count) * max_bar_width)
            print(f"[{low:10.0f} - {high:10.0f}] : {hist[i]:3d} | {bar}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AHC072 高速並列テスター＆スコア集計スクリプト")
    
    parser.add_argument("-c", "--cmd", required=True, 
                        help="解答プログラムの実行コマンド (例: 'python main.py' や './a.exe')")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--range", nargs=2, type=int, metavar=("START", "END"),
                       help="テストケース番号の範囲 [START, END] (例: -r 0 49)")
    group.add_argument("-s", "--sample", type=int, metavar="N",
                       help="存在する入力ファイルからランダムにN個選んで実行")

    parser.add_argument("--vis", default=DEFAULT_VIS_PATH,
                        help=f"vis.exeのパス (デフォルト: {DEFAULT_VIS_PATH})")
    parser.add_argument("--in-dir", default=DEFAULT_IN_DIR,
                        help=f"入力ファイルディレクトリ (デフォルト: {DEFAULT_IN_DIR})")
    
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count(),
                        help="並列実行プロセス数 (デフォルト: CPUコア数)")
    parser.add_argument("-t", "--timeout", type=float, default=3.0,
                        help="各ケースのタイムアウト時間(秒) (デフォルト: 3.0)")

    args = parser.parse_args()

    # コマンドのサニタイズ（安全化・自動補完）
    try:
        cmd_list = sanitize_cmd(args.cmd)
    except Exception as e:
        print(f"コマンドエラー: {e}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.vis):
        print(f"エラー: vis.exe が見つかりません: {args.vis}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.in_dir):
        print(f"エラー: 入力ディレクトリが見つかりません: {args.in_dir}", file=sys.stderr)
        sys.exit(1)

    all_files = sorted(glob.glob(os.path.join(args.in_dir, "*.txt")))
    file_map = {}
    for f in all_files:
        basename = os.path.splitext(os.path.basename(f))[0]
        if basename.isdigit():
            file_map[int(basename)] = f

    if not file_map:
        print(f"エラー: {args.in_dir} 内に数値名の .txt ファイルが見つかりません。", file=sys.stderr)
        sys.exit(1)

    target_tasks = []
    if args.range:
        start, end = args.range
        for i in range(start, end + 1):
            if i in file_map:
                target_tasks.append((i, file_map[i], cmd_list, args.vis, args.timeout))
            else:
                print(f"警告: seed={i} のファイルが見つかりません。スキップします。", file=sys.stderr)
    elif args.sample:
        available_ids = list(file_map.keys())
        sample_size = min(args.sample, len(available_ids))
        chosen_ids = sorted(random.sample(available_ids, sample_size))
        for i in chosen_ids:
            target_tasks.append((i, file_map[i], cmd_list, args.vis, args.timeout))
    else:
        for i in sorted(file_map.keys()):
            target_tasks.append((i, file_map[i], cmd_list, args.vis, args.timeout))

    if not target_tasks:
        print("実行対象のテストケースがありません。", file=sys.stderr)
        sys.exit(1)

    print(f"実行開始: {len(target_tasks)} ケース | 並列プロセス数: {args.jobs}")
    print(f"Command : {' '.join(cmd_list)}")

    results = []
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(run_single_testcase, task) for task in target_tasks]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Evaluating"):
            results.append(f.result())

    results.sort(key=lambda x: x["id"])
    print_summary(results)


if __name__ == "__main__":
    main()
import os
import glob
import re
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================================================================
# [設定パス]
# =========================================================================
IN_DIR = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\in"
VIS_EXE = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\vis.exe"
SOLVER_EXE = r"C:\Rino-program\AtCoder\AHC\072\solve1.exe"

# 並列スレッド数
MAX_WORKERS = 3

# 「失敗（ダメ）」と判定する閾値スコア
# 未帰巣スライム1匹につき 100,000 ペナルティなので、10万以上は全員帰巣できていない
FAIL_SCORE_THRESHOLD = 100_000

# =========================================================================
# [検証したいパラメータ（Trial 94のベスト値、または事故が起きた時の値）]
# =========================================================================
TEST_PARAMS = {
    "phase2_max_merge_dist": 8,
    "combo_h_min": 5,
    "combo_cost_min": 4,
    "combo_cooldown_steps": 20,
    "height8_pending_steps": 9,
    "recent_history_len": 16,
    "rand_p_h8_second": 20,
    "rand_p_norm_second": 12,
    "rand_p_norm_third": 19,
    "combo_search_radius": 3,
    "partner_saved_ops_default": 4,
    "weight_jump_gain": 2,
}


def evaluate_single_case(in_file):
    filename = os.path.basename(in_file)
    cmd = [
        SOLVER_EXE,
        "--phase2_max_merge_dist", str(TEST_PARAMS["phase2_max_merge_dist"]),
        "--combo_h_min", str(TEST_PARAMS["combo_h_min"]),
        "--combo_cost_min", str(TEST_PARAMS["combo_cost_min"]),
        "--combo_cooldown_steps", str(TEST_PARAMS["combo_cooldown_steps"]),
        "--height8_pending_steps", str(TEST_PARAMS["height8_pending_steps"]),
        "--recent_history_len", str(TEST_PARAMS["recent_history_len"]),
        "--rand_p_h8_second", str(TEST_PARAMS["rand_p_h8_second"]),
        "--rand_p_norm_second", str(TEST_PARAMS["rand_p_norm_second"]),
        "--rand_p_norm_third", str(TEST_PARAMS["rand_p_norm_third"]),
        "--combo_search_radius", str(TEST_PARAMS["combo_search_radius"]),
        "--partner_saved_ops_default", str(TEST_PARAMS["partner_saved_ops_default"]),
        "--weight_jump_gain", str(TEST_PARAMS["weight_jump_gain"]),
    ]

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as tmp_out:
        tmp_out_path = tmp_out.name

    score = 10**9
    reason = "NORMAL"

    try:
        with open(in_file, "r") as f_in, open(tmp_out_path, "w") as f_out:
            res_sol = subprocess.run(
                cmd,
                stdin=f_in,
                stdout=f_out,
                stderr=subprocess.PIPE,
                timeout=5.0
            )

        vis_res = subprocess.run(
            [VIS_EXE, in_file, tmp_out_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5.0
        )

        output_text = vis_res.stdout + "\n" + vis_res.stderr
        match = re.search(r"Score\s*=\s*(\d+)", output_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
        else:
            score = 10**9
            reason = "VIS_PARSE_FAILED"

    except subprocess.TimeoutExpired:
        score = 10**9
        reason = "TIMEOUT (>5.0s)"
    except Exception as e:
        score = 10**9
        reason = f"EXCEPTION ({e})"
    finally:
        if os.path.exists(tmp_out_path):
            try:
                os.remove(tmp_out_path)
            except OSError:
                pass

    return filename, score, reason


def main():
    test_files = sorted(glob.glob(os.path.join(IN_DIR, "*.txt")))
    if not test_files:
        print(f"[ERROR] テストケースが見つかりません: {IN_DIR}")
        return

    total_cases = len(test_files)
    print("==================================================")
    print(f"  ダメケース（詰まり・ペナルティ）検出モード開始")
    print(f"  対象ケース総数 : {total_cases} 件")
    print(f"  しきい値スコア : {FAIL_SCORE_THRESHOLD:,} 以上")
    print(f"  並列スレッド数 : {MAX_WORKERS}")
    print("==================================================\n")

    failed_cases = []
    completed = 0
    t_start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(evaluate_single_case, f) for f in test_files]

        for f in as_completed(futures):
            filename, score, reason = f.result()
            completed += 1

            # 失敗判定（スコアが10万以上、またはエラー）
            if score >= FAIL_SCORE_THRESHOLD:
                failed_cases.append((filename, score, reason))
                # 🚨 発見した瞬間にコンソールに割り込んで出力！
                unreturned_slimes = score // 100_000
                print(
                    f"\n[🚨 失敗検知!] {filename} | スコア: {score:,} "
                    f"(未帰巣: 約 {unreturned_slimes} 匹) | 理由: {reason}"
                )

            # 進捗表示
            percent = int(completed / total_cases * 100)
            bar = "█" * (percent // 5) + "░" * (20 - (percent // 5))
            print(
                f"\r進捗: |{bar}| {percent:3d}% ({completed}/{total_cases}) [NG検知数: {len(failed_cases)}]",
                end="",
                flush=True
            )

    elapsed = time.time() - t_start
    print(f"\n\n==================================================")
    print(f"  検証完了！ (所要時間: {elapsed:.1f}s)")
    print(f"  失敗ケース数: {len(failed_cases)} / {total_cases}")
    print("==================================================")

    if failed_cases:
        print("\n【🚨 失敗ケース一覧】")
        for fn, sc, rs in sorted(failed_cases, key=lambda x: x[1], reverse=True):
            print(f"  ・ {fn:<12} : Score = {sc:,} ({rs})")

        # failed_cases.txt に保存
        out_file = "failed_cases.txt"
        with open(out_file, "w", encoding="utf-8") as out_f:
            out_f.write(f"# 失敗ケース一覧 (合計 {len(failed_cases)} 件)\n")
            out_f.write(f"# MUST_HAVE_NAMES = {[fn for fn, _, _ in failed_cases]}\n\n")
            for fn, sc, rs in sorted(failed_cases, key=lambda x: x[1], reverse=True):
                out_f.write(f"{fn}\t{sc}\t{rs}\n")
        print(f"\n[INFO] 詳細を {out_file} に保存しました。")
        print(f"次回チューニングの MUST_HAVE_NAMES にそのままコピペして使えます！")
    else:
        print("\n🎉 素晴らしい！失敗したケースは 1 つもありませんでした！")


if __name__ == "__main__":
    main()
import os
import glob
import re
import subprocess
import tempfile
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import optuna

# Optuna の標準冗長ログを抑制
optuna.logging.set_verbosity(optuna.logging.WARNING)

# =========================================================================
# [設定パス]
# =========================================================================
IN_DIR = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\in"
VIS_EXE = r"C:\Rino-program\AtCoder\AHC\072\vis_dir\vis.exe"
SOLVER_EXE = r"C:\Rino-program\AtCoder\AHC\072\solve2.exe"

# 1試行あたりの評価ケース数
EVAL_CASE_COUNT = 150

# 探索の試行回数
N_TRIALS = 5000

# 並列実行数（PC負荷・発熱を抑える安全設定）
MAX_WORKERS = 2

# 高頻度で含めたい重点ファイル名
MUST_HAVE_NAMES = ["0005.txt", "0097.txt", "0102.txt", "2718.txt", "2855.txt", "2987.txt"]

# MUST_HAVE の各ファイルが毎回の試行に選ばれる確率（例: 0.8 = 80%の確率で含まれる）
# 普通のケース（1500件中47件 ≒ 3%）に比べて約25倍の高頻度で選ばれます
MUST_HAVE_PROBABILITY = 1.00


# =========================================================================
# [単一ケースの実行と評価]
# =========================================================================
def evaluate_single_case(args):
    in_file, params = args

    cmd = [
        SOLVER_EXE,
        "--combo_h_min", str(params["combo_h_min"]),
        "--combo_cost_min", str(params["combo_cost_min"]),
        "--combo_cooldown_steps", str(params["combo_cooldown_steps"]),
        "--height8_pending_steps", str(params["height8_pending_steps"]),
        "--recent_history_len", str(params["recent_history_len"]),
        "--bonus_catapult_align", str(params["bonus_catapult_align"]),
        "--bonus_pass_through_same", str(params["bonus_pass_through_same"]),
        "--bonus_pass_through_diff", str(params["bonus_pass_through_diff"]),
    ]

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as tmp_out:
        tmp_out_path = tmp_out.name

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
            return int(match.group(1))
        else:
            return 10**9

    except subprocess.TimeoutExpired:
        return 10**9
    except Exception:
        return 10**9
    finally:
        if os.path.exists(tmp_out_path):
            try:
                os.remove(tmp_out_path)
            except OSError:
                pass


# =========================================================================
# [Optuna 目的関数]
# =========================================================================
def create_objective(must_have_files, normal_files):
    best_score_holder = {"val": float("inf")}

    def objective(trial):
        trial_num = trial.number + 1
        t_start = time.time()

        # -------------------------------------------------------------
        # 1. 毎回ランダムに80件をサンプリング（重複なし）
        # -------------------------------------------------------------
        current_cases = []

        # MUST_HAVE_NAMES から確率的にピックアップ
        for mf in must_have_files:
            if random.random() < MUST_HAVE_PROBABILITY:
                current_cases.append(mf)

        # 80件に足りない分を通常ファイル群から重複なく選ぶ
        needed = EVAL_CASE_COUNT - len(current_cases)
        if needed > 0:
            current_cases.extend(random.sample(normal_files, needed))

        # シャッフルして実行順の偏りを解消
        random.shuffle(current_cases)

        # -------------------------------------------------------------
        # 2. パラメータ定義
        # -------------------------------------------------------------
        params = {
            "combo_h_min": trial.suggest_int("combo_h_min", 4, 9),
            "combo_cost_min": trial.suggest_int("combo_cost_min", 1, 5),
            "combo_cooldown_steps": trial.suggest_int("combo_cooldown_steps", 10, 32),
            "height8_pending_steps": trial.suggest_int("height8_pending_steps", 5, 20),
            "recent_history_len": trial.suggest_int("recent_history_len", 50, 100),
            "bonus_catapult_align": trial.suggest_int("bonus_catapult_align", 0, 50),
            "bonus_pass_through_same": trial.suggest_int("bonus_pass_through_same", 0, 40),
            "bonus_pass_through_diff": trial.suggest_int("bonus_pass_through_diff", 0, 20),
        }

        tasks = [(in_f, params) for in_f in current_cases]
        scores = []
        completed = 0
        total_cases = len(tasks)

        # 並列実行しながら進捗バーを表示
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(evaluate_single_case, task) for task in tasks]
            for f in as_completed(futures):
                scores.append(f.result())
                completed += 1
                percent = int(completed / total_cases * 100)
                bar = "█" * (percent // 5) + "░" * (20 - (percent // 5))
                print(
                    f"\r[Trial {trial_num:3d}/{N_TRIALS}] |{bar}| {percent:3d}% ({completed}/{total_cases})",
                    end="",
                    flush=True
                )

        elapsed = time.time() - t_start
        total_score = sum(scores)

        # ベスト更新判定
        is_best = total_score < best_score_holder["val"]
        if is_best:
            best_score_holder["val"] = total_score
            status = f"★ BEST! ({total_score:,})"
        else:
            status = f"Score: {total_score:,} (Best: {best_score_holder['val']:,})"

        print(f"\r[Trial {trial_num:3d}/{N_TRIALS}] 完了 ({elapsed:4.1f}s) -> {status}")
        return total_score

    return objective


# =========================================================================
# [メイン実行]
# =========================================================================
if __name__ == "__main__":
    test_files = sorted(glob.glob(os.path.join(IN_DIR, "*.txt")))
    if not test_files:
        print(f"Error: テストケースが見つかりませんでした: {IN_DIR}")
        exit(1)

    must_have_files = []
    normal_files = []

    for f in test_files:
        if os.path.basename(f) in MUST_HAVE_NAMES:
            must_have_files.append(f)
        else:
            normal_files.append(f)

    print("==================================================")
    print(f"  Optuna 自動パラメータチューニング開始")
    print(f"  利用可能総ケース数: {len(test_files)} 件")
    print(f"  重点テストケース  : {len(must_have_files)} 件 (出現率 {int(MUST_HAVE_PROBABILITY*100)}%)")
    print(f"  毎回の評価件数    : {EVAL_CASE_COUNT} 件 (重複なしランダム)")
    print(f"  試行回数          : {N_TRIALS} 回")
    print(f"  並列スレッド数    : {MAX_WORKERS}")
    print("==================================================\n")

    study = optuna.create_study(direction="minimize")
    study.optimize(create_objective(must_have_files, normal_files), n_trials=N_TRIALS)

    print("\n==================================================")
    print("  ★ 最適化完了！")
    print(f"  最良合計スコア : {study.best_value:,}")
    print("  最良パラメータ :")
    for k, v in study.best_params.items():
        print(f"    {k} = {v}")
    print("==================================================")

    # 結果をテキストファイルに自動保存
    output_filepath = "best_params.txt"
    try:
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("==================================================\n")
            f.write(f"  AHCチューニング結果 (試行回数: {N_TRIALS})\n")
            f.write(f"  最良合計スコア : {study.best_value:,}\n")
            f.write("==================================================\n\n")
            f.write("struct HyperParams {\n")
            for k, v in study.best_params.items():
                f.write(f"    int {k} = {v};\n")
            f.write("};\n")
        print(f"\n[INFO] 最適化結果を {output_filepath} に自動保存しました！")
    except Exception as e:
        print(f"\n[ERROR] ファイル保存中にエラーが発生しました: {e}")
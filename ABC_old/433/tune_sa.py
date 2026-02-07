import os, subprocess, random, math, json
from pathlib import Path

# Simple simulated annealing to tune parameters for maina.py on in.txt
IN_FILE = 'in.txt'
OUT_CMD = lambda env: f"python maina.py"

# initial params
params = {
    'TAKE_DELAY_FACTOR': 1.0,
    'PLACE_BIAS': 1.0,
    'PLACE_MARGIN': 1.0,
    'MAX_CAND_EVAL': 30,
    'BEAM_DEPTH': 2,
    'BEAM_WIDTH': 6,
}

bounds = {
    'TAKE_DELAY_FACTOR': (0.3, 3.0),
    'PLACE_BIAS': (0.0, 6.0),
    'PLACE_MARGIN': (-3.0, 5.0),
    'MAX_CAND_EVAL': (5, 80),
    'BEAM_DEPTH': (1, 4),
    'BEAM_WIDTH': (1, 12),
}

# helper to run with env and return score
def run_with_params(p):
    env = os.environ.copy()
    for k, v in p.items():
        env[k] = str(int(v) if k in ('MAX_CAND_EVAL','BEAM_DEPTH','BEAM_WIDTH') else float(v))
    # run solver
    with open('in.txt') as infile, open('out.txt','w') as outfile, open('err.txt','w') as errfile:
        proc = subprocess.run(['python','maina.py'], stdin=infile, stdout=outfile, stderr=errfile, env=env)
    # compute score
    proc2 = subprocess.run(['python','compute_score.py'], capture_output=True, text=True)
    out = proc2.stdout.strip()
    parts = out.split()
    if len(parts) >= 8 and parts[0]=='N':
        score = int(parts[-1])
        return score, out
    return -10**9, out

# SA
best = params.copy()
best_score, _ = run_with_params(best)
print('start score=', best_score, 'params=', best)
T0 = 5.0
iters = 100
for it in range(iters):
    T = T0 * (1 - it / iters)
    cand = best.copy()
    # perturb
    key = random.choice(list(params.keys()))
    lo, hi = bounds[key]
    if isinstance(lo, int) and isinstance(hi, int) and key in ('MAX_CAND_EVAL','BEAM_DEPTH','BEAM_WIDTH'):
        newv = int(max(lo, min(hi, cand[key] + random.randint(-5, 5))))
    else:
        # gaussian perturb
        sigma = (hi - lo) * 0.2
        newv = cand[key] + random.gauss(0, sigma)
        newv = max(lo, min(hi, newv))
    cand[key] = newv
    score, out = run_with_params(cand)
    delta = score - best_score
    if delta > 0 or random.random() < math.exp(delta / max(1e-9, T)):
        best = cand
        best_score = score
        print(f'it={it} improved score={best_score} key={key} val={newv}')
        with open('best_params.json','w') as f:
            json.dump({'params':best,'score':best_score}, f, indent=2)
    if it % 10 == 0:
        print('it',it,'best',best_score)

print('done best',best_score,best)

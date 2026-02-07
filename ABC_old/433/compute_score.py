from pathlib import Path
p=Path('in.txt')
s=p.read_text().strip().split()
if not s:
    print('no input')
    raise SystemExit
N=int(s[0])
vals=list(map(int,s[1:]))
A=[vals[i*N:(i+1)*N] for i in range(N)]
# read operations
ops=Path('out.txt').read_text().strip().splitlines()
now=[0,0]
hand=[]
K=0
for op in ops:
    op=op.strip()
    if not op: continue
    if op in ('U','D','L','R'):
        if op=='U': now[0]-=1
        if op=='D': now[0]+=1
        if op=='L': now[1]-=1
        if op=='R': now[1]+=1
        K+=1
    elif op=='Z':
        y,x=now
        if A[y][x]!=-1:
            hand.append(A[y][x])
            A[y][x]=-1
            if len(hand)>=2 and hand[-1]==hand[-2]:
                hand.pop(); hand.pop()
    elif op=='X':
        y,x=now
        if A[y][x]==-1 and hand:
            A[y][x]=hand.pop()
# compute X
remaining_on_board=sum(1 for y in range(N) for x in range(N) if A[y][x]!=-1)
X=len(hand)+remaining_on_board
# score
if X==0:
    score=N*N + 2*(N**3) - K
else:
    score=N*N - X
print('N',N,'K',K,'X',X,'score',score)
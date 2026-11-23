import json,os,sys,urllib.request
PAWN,KNIGHT,BISHOP,ROOK,QUEEN,KING=1,2,3,4,5,6
WHITE,BLACK=8,16
N=110000
PIECE_VALS={PAWN:100,KNIGHT:320,BISHOP:330,ROOK:500,QUEEN:900,KING:20000}
SLIDE={BISHOP:[-17,-15,15,17],ROOK:[-16,-1,1,16],QUEEN:[-17,-15,15,17,-16,-1,1,16]}
def parse_fen(f):
 b=[0]*128
 for i,r in enumerate(f.split()[0].split('/')):
  c=0
  for x in r:
   if x.isdigit():c+=int(x)
   else:
    p={'p':PAWN,'n':KNIGHT,'b':BISHOP,'r':ROOK,'q':QUEEN,'k':KING}[x.lower()]
    b[(7-i)*16+c]=p|(WHITE if x.isupper() else BLACK);c+=1
 return b
def to_uci(m):
 r="abcdefgh"[m[0]%16]+str(m[0]//16+1)+"abcdefgh"[m[1]%16]+str(m[1]//16+1)
 return r+('q' if m[2] else '')
def gen(b,col):
 m,opp=[],(BLACK if col==WHITE else WHITE)
 for i in range(128):
  if not(b[i]&col):continue
  p=b[i]&7
  if p==PAWN:
   d=16 if col==WHITE else -16
   if 0<=(i+d)<128 and not((i+d)&0x88) and not b[i+d]:
    if (col==WHITE and i//16==6) or (col==BLACK and i//16==1):
     for pr in [QUEEN]:m.append((i,i+d,pr))
    else:m.append((i,i+d,0))
    if (col==WHITE and i//16==1) or (col==BLACK and i//16==6):
     if 0<=(i+2*d)<128 and not((i+2*d)&0x88) and not b[i+2*d]:m.append((i,i+2*d,0))
   for t in [i+d-1,i+d+1]:
    if 0<=t<128 and not(t&0x88) and b[t] and (b[t]&opp):
     if (col==WHITE and i//16==6) or (col==BLACK and i//16==1):
      for pr in [QUEEN]:m.append((i,t,pr))
     else:m.append((i,t,0))
  elif p in [KNIGHT,KING]:
   for d in ([-33,-31,-18,-14,14,18,31,33] if p==KNIGHT else [-17,-16,-15,-1,1,15,16,17]):
    t=i+d
    if 0<=t<128 and not(t&0x88) and not(b[t]&col):m.append((i,t,0))
  elif p in SLIDE:
   for d in SLIDE[p]:
    t=i+d
    while 0<=t<128 and not(t&0x88):
     if b[t]:
      if b[t]&opp:m.append((i,t,0))
      break
     m.append((i,t,0));t+=d
 return m
def eval(b,col):
 s=0;opp=BLACK if col==WHITE else WHITE;k=0
 for i in range(128):
  if not(i&0x88) and b[i]:
   p=b[i]&7;v=PIECE_VALS[p]
   if p==KING:k|=1 if b[i]&col else 2
   v+=(8-abs(2*(i%16)-7)-abs(2*(i//16)-7))*(3 if p in(2,3) else 1 if p<5 else 0)+(i//16 if b[i]&WHITE else 7-i//16)*4*(p==1)
   if b[i]&col:s+=v
   elif b[i]&opp:s-=v
 return 99999 if k==1 else -99999 if k==2 else s
def quiescence(b,col,a,b_a,nodes):
 nodes[0]+=1
 s=eval(b,col)
 if s>=b_a:return b_a
 if s>a:a=s
 moves=sorted([m for m in gen(b,col) if b[m[1]]],key=lambda m:PIECE_VALS.get(b[m[1]]&7,0),reverse=True)
 for m in moves:
  if s+PIECE_VALS[b[m[1]]&7]+200<a and not m[2]:continue
  nb=list(b);nb[m[1]]=(m[2] if m[2] else nb[m[0]]&7)|(nb[m[0]]&24);nb[m[0]]=0
  v=-quiescence(nb,BLACK if col==WHITE else WHITE,-b_a,-a,nodes)
  if v>=b_a:return b_a
  if v>a:a=v
 return a
def search(b,col,d,a,b_a,nodes):
 nodes[0]+=1
 if nodes[0]>N:raise OverflowError
 if d==0:return quiescence(b,col,a,b_a,nodes)
 moves=sorted(gen(b,col),key=lambda m:PIECE_VALS.get(b[m[1]]&7,0)*9-PIECE_VALS[b[m[0]]&7]//9-abs(2*(m[1]%16)-7)-abs(2*(m[1]//16)-7),reverse=True)
 if not moves:return eval(b,col)
 for m in moves:
  nb=list(b);nb[m[1]]=(m[2] if m[2] else nb[m[0]]&7)|(nb[m[0]]&24);nb[m[0]]=0
  v=-search(nb,BLACK if col==WHITE else WHITE,d-1,-b_a,-a,nodes)
  if v>=b_a:return b_a
  if v>a:a=v
 return a
def P(p,b):
 E=os.environ.get("MAKEFUN_ENV_URL")
 r=urllib.request.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
 with urllib.request.urlopen(r) as s:return json.load(s)
if __name__ == "__main__":
 E=os.environ.get("MAKEFUN_ENV_URL")
 if not E:sys.exit(1)
 while 1:
  g=P("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   b=parse_fen(g["fen"]);col=WHITE if " w " in g["fen"] else BLACK;o=BLACK if col==WHITE else WHITE
   L=[m for m in gen(b,col) if to_uci(m) in g["legal_moves"]];best=L[0]
   for d in range(1,8):
    try:
     n=[0];a=-10**6;cur=None
     for m in L:
      nb=list(b);nb[m[1]]=(m[2] if m[2] else nb[m[0]]&7)|(nb[m[0]]&24);nb[m[0]]=0
      v=-search(nb,o,d,-10**6,-a,n)
      if v>a:a,cur=v,m
     best=cur;L.remove(cur);L.insert(0,cur)
    except OverflowError:break
   best=to_uci(best)
   g=P("/move",{"game":g["game"],"move":best})

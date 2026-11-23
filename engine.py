
import sys

# 0x88 board constants
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1, 2, 3, 4, 5, 6
WHITE, BLACK = 8, 16
PIECE_VALS = {PAWN: 100, KNIGHT: 320, BISHOP: 330, ROOK: 500, QUEEN: 900, KING: 20000}

# Directions
SLIDE_DIRS = {BISHOP: [-17, -15, 15, 17], ROOK: [-16, -1, 1, 16], QUEEN: [-17, -15, 15, 17, -16, -1, 1, 16]}
KNIGHT_DIRS = [-33, -31, -18, -14, 14, 18, 31, 33]
KING_DIRS = [-17, -16, -15, -1, 1, 15, 16, 17]

def create_board(): return [0] * 128

def parse_fen(fen):
    board = create_board()
    rows = fen.split()[0].split('/')
    for r in range(8):
        c = 0
        for char in rows[r]:
            if char.isdigit(): c += int(char)
            else:
                p = {'p': PAWN, 'n': KNIGHT, 'b': BISHOP, 'r': ROOK, 'q': QUEEN, 'k': KING}[char.lower()]
                board[(7-r)*16 + c] = p | (WHITE if char.isupper() else BLACK)
                c += 1
    return board

def get_pseudo_legal_moves(board, color):
    moves = []
    opp = BLACK if color == WHITE else WHITE
    for i in range(128):
        if not (board[i] & color): continue
        p = board[i] & 7
        if p == PAWN:
            d = 16 if color == WHITE else -16
            if not board[i+d]:
                moves.append((i, i+d))
                if (color==WHITE and i//16==1) or (color==BLACK and i//16==6):
                    if not board[i+2*d]: moves.append((i, i+2*d))
            for c in [i+d-1, i+d+1]:
                if 0 <= c < 128 and not (c&0x88) and board[c] and (board[c]&opp): moves.append((i, c))
        elif p in [KNIGHT, KING]:
            dirs = KNIGHT_DIRS if p == KNIGHT else KING_DIRS
            for d in dirs:
                target = i + d
                if 0 <= target < 128 and not (target&0x88) and not (board[target]&color): moves.append((i, target))
        elif p in SLIDE_DIRS:
            for d in SLIDE_DIRS[p]:
                target = i + d
                while 0 <= target < 128 and not (target&0x88):
                    if board[target]:
                        if board[target]&opp: moves.append((i, target))
                        break
                    moves.append((i, target))
                    target += d
    return moves

def evaluate(board, color):
    score = 0
    opp = BLACK if color == WHITE else WHITE
    for i in range(128):
        if not (i & 0x88):
            p = board[i]
            if not p: continue
            val = PIECE_VALS[p&7]
            if p & color: score += val
            elif p & opp: score -= val
    return score

def make_move(board, move):
    f, t = move
    board[t] = board[f]
    board[f] = EMPTY
    return board

# Negamax with capture quiescence
def search(board, depth, alpha, beta, color):
    # Need to handle nodes limit and quiescence
    return 0

# Test setup
if __name__ == "__main__":
    start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board = parse_fen(start_fen)
    moves = get_pseudo_legal_moves(board, WHITE)
    print(f"Generated {len(moves)} pseudo-legal moves.")
    assert len(moves) == 20

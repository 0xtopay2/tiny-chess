from main import parse_fen, gen, WHITE
start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
b = parse_fen(start_fen)
moves = gen(b, WHITE)
print(f"Generated {len(moves)} pseudo-legal moves.")
assert len(moves) == 20

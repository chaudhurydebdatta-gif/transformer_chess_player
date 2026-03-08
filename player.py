import chess
import random
import time


class TransformerPlayer:

    def __init__(self):

        self.max_depth = 4
        self.time_limit = 1.0

        self.values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        self.tt = {}
        self.history = {}
        self.killer_moves = [[None, None] for _ in range(64)]

        self.opening_book = {
            "start": ["e2e4", "d2d4", "c2c4", "g1f3"]
        }

    # -------------------------
    # Evaluation
    # -------------------------

    def evaluate(self, board):

        if board.is_checkmate():
            return -999999 if board.turn else 999999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0

        for square, piece in board.piece_map().items():

            value = self.values[piece.piece_type]

            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

        # bishop pair bonus
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += 30
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= 30

        # passed pawn / pawn advancement
        for sq in board.pieces(chess.PAWN, chess.WHITE):
            score += chess.square_rank(sq) * 5

        for sq in board.pieces(chess.PAWN, chess.BLACK):
            score -= (7 - chess.square_rank(sq)) * 5

        # king safety
        wk = board.king(chess.WHITE)
        bk = board.king(chess.BLACK)

        if wk is not None:
            score -= len(board.attackers(chess.BLACK, wk)) * 10

        if bk is not None:
            score += len(board.attackers(chess.WHITE, bk)) * 10

        return score

    # -------------------------
    # Move ordering
    # -------------------------

    def order_moves(self, board, moves, depth):

        scored = []

        for move in moves:

            score = 0

            if board.is_capture(move):

                captured = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)

                if captured and attacker:
                    score += 10 * self.values[captured.piece_type]
                    score -= self.values[attacker.piece_type]

            if move.promotion:
                score += 8000

            if board.gives_check(move):
                score += 50

            if move == self.killer_moves[depth][0]:
                score += 9000

            if move == self.killer_moves[depth][1]:
                score += 8000

            score += self.history.get(move, 0)

            scored.append((score, move))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [m for s, m in scored]

    # -------------------------
    # Quiescence search
    # -------------------------

    def quiescence(self, board, alpha, beta):

        stand = self.evaluate(board)

        if stand >= beta:
            return beta

        if alpha < stand:
            alpha = stand

        for move in board.legal_moves:

            if not board.is_capture(move):
                continue

            board.push(move)

            score = -self.quiescence(board, -beta, -alpha)

            board.pop()

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

        return alpha

    # -------------------------
    # Alpha-beta
    # -------------------------

    def alphabeta(self, board, depth, alpha, beta, ply):

        if depth <= 0:
            return self.quiescence(board, alpha, beta)

        key = board.fen()

        if key in self.tt:
            return self.tt[key]

        if board.is_check():
            depth += 1

        # null move pruning
        if depth >= 3 and not board.is_check():

            board.push(chess.Move.null())

            score = -self.alphabeta(board, depth - 3, -beta, -beta + 1, ply + 1)

            board.pop()

            if score >= beta:
                return beta

        best_score = -999999

        moves = self.order_moves(board, list(board.legal_moves), ply)

        if not moves:
            return self.evaluate(board)

        for index, move in enumerate(moves):

            board.push(move)

            reduction = 0

            if index > 3 and depth > 2 and not board.is_capture(move):
                reduction = 1

            score = -self.alphabeta(board, depth - 1 - reduction, -beta, -alpha, ply + 1)

            board.pop()

            if score >= beta:

                if self.killer_moves[ply][0] != move:
                    self.killer_moves[ply][1] = self.killer_moves[ply][0]
                    self.killer_moves[ply][0] = move

                return beta

            if score > best_score:
                best_score = score

            if score > alpha:
                alpha = score
                self.history[move] = self.history.get(move, 0) + depth * depth

        self.tt[key] = best_score

        return best_score

    # -------------------------
    # Root search
    # -------------------------

    def search_root(self, board, depth):

        best_move = None
        best_score = -999999

        moves = self.order_moves(board, list(board.legal_moves), 0)

        for move in moves:

            board.push(move)

            score = -self.alphabeta(board, depth - 1, -999999, 999999, 1)

            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    # -------------------------
    # Main interface
    # -------------------------

    def get_move(self, fen):

        board = chess.Board(fen)

        if board.fullmove_number <= 2 and board.board_fen() == chess.Board().board_fen():
            return random.choice(self.opening_book["start"])

        start = time.time()

        best_move = None

        for depth in range(1, self.max_depth + 1):

            if time.time() - start > self.time_limit:
                break

            score, move = self.search_root(board, depth)

            if move:
                best_move = move

        if best_move is None:
            best_move = random.choice(list(board.legal_moves))

        return best_move.uci()

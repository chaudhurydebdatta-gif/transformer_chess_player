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

        self.pst = {
            chess.PAWN: [
                0,0,0,0,0,0,0,0,
                50,50,50,50,50,50,50,50,
                10,10,20,30,30,20,10,10,
                5,5,10,25,25,10,5,5,
                0,0,0,20,20,0,0,0,
                5,-5,-10,0,0,-10,-5,5,
                5,10,10,-20,-20,10,10,5,
                0,0,0,0,0,0,0,0
            ],
            chess.KNIGHT: [
                -50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,0,0,0,0,-20,-40,
                -30,0,10,15,15,10,0,-30,
                -30,5,15,20,20,15,5,-30,
                -30,0,15,20,20,15,0,-30,
                -30,5,10,15,15,10,5,-30,
                -40,-20,0,5,5,0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50
            ]
        }

    def evaluate(self, board):

        if board.is_checkmate():
            return -999999 if board.turn else 999999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0

        for square, piece in board.piece_map().items():

            value = self.values[piece.piece_type]

            if piece.piece_type in self.pst:
                table = self.pst[piece.piece_type]
                if piece.color == chess.WHITE:
                    value += table[square]
                else:
                    value -= table[chess.square_mirror(square)]

            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

        return score

    def order_moves(self, board, moves, depth):

        ordered = []

        for move in moves:

            score = 0

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += 10 * self.values[captured.piece_type]

            if board.gives_check(move):
                score += 50

            if move == self.killer_moves[depth][0]:
                score += 9000

            if move == self.killer_moves[depth][1]:
                score += 8000

            score += self.history.get(move, 0)

            ordered.append((score, move))

        ordered.sort(reverse=True)

        return [m for s, m in ordered]

    def quiescence(self, board, alpha, beta):

        stand_pat = self.evaluate(board)

        if stand_pat >= beta:
            return beta

        if alpha < stand_pat:
            alpha = stand_pat

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

    def alphabeta(self, board, depth, alpha, beta, ply):

        if depth <= 0:
            return self.quiescence(board, alpha, beta)

        key = board.fen()

        if key in self.tt:
            return self.tt[key]

        if board.is_check():
            depth += 1

        best_score = -999999

        moves = self.order_moves(board, list(board.legal_moves), ply)

        if not moves:
            return self.evaluate(board)

        for move in moves:

            board.push(move)

            score = -self.alphabeta(board, depth - 1, -beta, -alpha, ply + 1)

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

import chess
import random


class TransformerPlayer:

    def __init__(self):

        self.values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }

        self.center = [chess.D4, chess.E4, chess.D5, chess.E5]

        self.tt = {}

    # -------------------------
    # Evaluation
    # -------------------------
    def evaluate_board(self, board):

        score = 0

        for piece in self.values:
            score += len(board.pieces(piece, chess.WHITE)) * self.values[piece]
            score -= len(board.pieces(piece, chess.BLACK)) * self.values[piece]

        for square in self.center:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 20
                else:
                    score -= 20

        mobility = len(list(board.legal_moves))

        if board.turn == chess.WHITE:
            score += mobility * 2
        else:
            score -= mobility * 2

        if board.is_check():
            if board.turn == chess.BLACK:
                score += 30
            else:
                score -= 30

        return score

    # -------------------------
    # Move ordering
    # -------------------------
    def order_moves(self, board, moves):

        scored = []

        for move in moves:

            score = 0

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += 10 * self.values.get(captured.piece_type, 0)

            if move.to_square in self.center:
                score += 50

            board.push(move)

            if board.is_check():
                score += 200

            board.pop()

            scored.append((score, move))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [m for _, m in scored]

    # -------------------------
    # Quiescence
    # -------------------------
    def quiescence(self, board, alpha, beta):

        stand_pat = self.evaluate_board(board)

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

    # -------------------------
    # Alpha-beta
    # -------------------------
    def alphabeta(self, board, depth, alpha, beta, maximizing):

        key = (board.fen(), depth)

        if key in self.tt:
            return self.tt[key]

        if depth == 0:
            value = self.quiescence(board, alpha, beta)
            self.tt[key] = value
            return value

        if board.is_game_over():
            value = self.evaluate_board(board)
            self.tt[key] = value
            return value

        moves = self.order_moves(board, list(board.legal_moves))[:12]

        if maximizing:

            value = -999999

            for move in moves:

                board.push(move)

                value = max(
                    value,
                    self.alphabeta(board, depth - 1, alpha, beta, False)
                )

                board.pop()

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

        else:

            value = 999999

            for move in moves:

                board.push(move)

                value = min(
                    value,
                    self.alphabeta(board, depth - 1, alpha, beta, True)
                )

                board.pop()

                beta = min(beta, value)

                if beta <= alpha:
                    break

        self.tt[key] = value

        return value

    # -------------------------
    # Move function
    # -------------------------
    def get_move(self, fen):

        board = chess.Board(fen)

        moves = list(board.legal_moves)

        if not moves:
            return None

        moves = self.order_moves(board, moves)

        best_move = random.choice(moves)

        max_depth = 3

        for depth in range(1, max_depth + 1):

            if board.turn == chess.WHITE:
                best_score = -999999
            else:
                best_score = 999999

            for move in moves:

                board.push(move)

                if board.is_checkmate():
                    board.pop()
                    return move.uci()

                score = self.alphabeta(
                    board,
                    depth,
                    -999999,
                    999999,
                    board.turn == chess.WHITE
                )

                board.pop()

                if board.turn == chess.WHITE:

                    if score > best_score:
                        best_score = score
                        best_move = move

                else:

                    if score < best_score:
                        best_score = score
                        best_move = move

        return best_move.uci()

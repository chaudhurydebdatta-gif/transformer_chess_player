import chess
import random


class TransformerPlayer:

    def __init__(self):

        self.values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

    # -------------------------
    # Board evaluation
    # -------------------------
    def evaluate_board(self, board):

        score = 0

        # Material
        for piece_type in self.values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.values[piece_type]

        # Mobility
        mobility = len(list(board.legal_moves))
        if board.turn == chess.WHITE:
            score += mobility * 0.05
        else:
            score -= mobility * 0.05

        # Check bonus
        if board.is_check():
            if board.turn == chess.BLACK:
                score += 0.5
            else:
                score -= 0.5

        return score

    # -------------------------
    # Move ordering
    # -------------------------
    def order_moves(self, board, moves):

        ordered = []

        for move in moves:

            score = 0

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += self.values.get(captured.piece_type, 0) + 5

            board.push(move)
            if board.is_check():
                score += 3
            board.pop()

            ordered.append((score, move))

        ordered.sort(reverse=True, key=lambda x: x[0])

        return [m for _, m in ordered]

    # -------------------------
    # Alpha-beta search
    # -------------------------
    def alphabeta(self, board, depth, alpha, beta, maximizing):

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        moves = self.order_moves(board, list(board.legal_moves))[:10]

        if maximizing:

            value = -9999

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

            return value

        else:

            value = 9999

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

            return value

    # -------------------------
    # Main move selection
    # -------------------------
    def get_move(self, fen):

        board = chess.Board(fen)

        legal_moves = self.order_moves(board, list(board.legal_moves))

        if not legal_moves:
            return None

        best_move = None

        if board.turn == chess.WHITE:
            best_score = -9999
        else:
            best_score = 9999

        center = [chess.D4, chess.E4, chess.D5, chess.E5]

        for move in legal_moves:

            board.push(move)

            if board.is_checkmate():
                board.pop()
                return move.uci()

            score = self.alphabeta(board, 2, -9999, 9999, board.turn == chess.WHITE)

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += self.values.get(captured.piece_type, 0) * 0.5

            if move.to_square in center:
                score += 0.3

            board.pop()

            if board.turn == chess.WHITE:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        if best_move is None:
            best_move = random.choice(legal_moves)

        return best_move.uci()

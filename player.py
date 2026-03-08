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

    def evaluate_board(self, board):
        score = 0

        for piece_type in self.values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.values[piece_type]

        return score

    def get_move(self, fen):

        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            return None

        best_move = None
        best_score = -9999 if board.turn == chess.WHITE else 9999

        center = [chess.D4, chess.E4, chess.D5, chess.E5]

        for move in legal_moves:

            board.push(move)

            if board.is_checkmate():
                board.pop()
                return move.uci()

            score = self.evaluate_board(board)

            if move.to_square in center:
                score += 0.3

            if board.is_stalemate():
                score -= 5

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

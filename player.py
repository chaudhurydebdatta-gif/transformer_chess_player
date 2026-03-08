
import chess
import random
from chess_tournament.players import Player


class TransformerPlayer(Player):

    def __init__(self, name="TransformerPlayer"):
        super().__init__(name)

        # piece values for evaluation
        self.values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

    def evaluate_board(self, board):
        """Simple material evaluation"""

        score = 0

        for piece_type in self.values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.values[piece_type]

        return score


   def get_move(self, fen):
       
    import chess
    import random

    board = chess.Board(fen)

    legal_moves = list(board.legal_moves)

    if not legal_moves:
        return None

    best_move = None
    best_score = -9999 if board.turn == chess.WHITE else 9999

    center = [chess.D4, chess.E4, chess.D5, chess.E5]

    for move in legal_moves:

        board.push(move)

        # ---------- Immediate checkmate ----------
        if board.is_checkmate():
            board.pop()
            return move.uci()

        score = self.evaluate_board(board)

        # ---------- Penalize moves that lose material ----------
        if board.is_capture(move):
            captured = board.piece_at(move.to_square)
            if captured:
                score += self.values.get(captured.piece_type, 0)

        # ---------- Prefer center ----------
        if move.to_square in center:
            score += 0.3

        # ---------- Avoid stalemate ----------
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


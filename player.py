
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

    best_move = None
    best_score = -9999 if board.turn == chess.WHITE else 9999

    for move in legal_moves:

        board.push(move)

        # instant win
        if board.is_checkmate():
            board.pop()
            return move.uci()

        # evaluate opponent responses
        opponent_moves = list(board.legal_moves)[:10]  # limit for speed

        if not opponent_moves:
            score = self.evaluate_board(board)
        else:
            scores = []

            for opp_move in opponent_moves:
                board.push(opp_move)
                scores.append(self.evaluate_board(board))
                board.pop()

            # opponent plays best response
            score = min(scores) if board.turn == chess.BLACK else max(scores)

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

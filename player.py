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

        # ----- Material -----
        for piece_type in self.values:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.values[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.values[piece_type]

        # ----- Mobility -----
        mobility = len(list(board.legal_moves))
        if board.turn == chess.WHITE:
            score += mobility * 0.05
        else:
            score -= mobility * 0.05

        # ----- Check bonus -----
        if board.is_check():
            if board.turn == chess.BLACK:
                score += 0.5
            else:
                score -= 0.5

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

            # ----- Instant checkmate -----
            if board.is_checkmate():
                board.pop()
                return move.uci()

            # ----- Opponent responses (limit to keep it fast) -----
            opponent_moves = list(board.legal_moves)[:10]

            if not opponent_moves:
                score = self.evaluate_board(board)

            else:

                scores = []

                for opp_move in opponent_moves:

                    board.push(opp_move)

                    score = self.evaluate_board(board)

                    scores.append(score)

                    board.pop()

                # Opponent chooses best reply
                if board.turn == chess.WHITE:
                    score = min(scores)
                else:
                    score = max(scores)

            # ----- Capture bonus -----
            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score += self.values.get(captured.piece_type, 0) * 0.5

            # ----- Center bonus -----
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

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

        # Transposition table
        self.tt = {}

        # Opening book
        self.opening_book = {
            "start": ["e2e4", "d2d4", "c2c4", "g1f3"],
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": ["c7c5", "e7e5", "e7e6"],
            "rnbqkbnr/pppppppp/8/8/3PP3/8/PPP2PPP/RNBQKBNR": ["d7d5"],
            "rnbqkbnr/pppppppp/8/8/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e5"]
        }

        # Piece-square tables
        self.pawn_table = [
            0,0,0,0,0,0,0,0,
            5,10,10,-20,-20,10,10,5,
            5,-5,-10,0,0,-10,-5,5,
            0,0,0,20,20,0,0,0,
            5,5,10,25,25,10,5,5,
            10,10,20,30,30,20,10,10,
            50,50,50,50,50,50,50,50,
            0,0,0,0,0,0,0,0
        ]

        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,0,5,5,0,-20,-40,
            -30,5,10,15,15,10,5,-30,
            -30,0,15,20,20,15,0,-30,
            -30,5,15,20,20,15,5,-30,
            -30,0,10,15,15,10,0,-30,
            -40,-20,0,0,0,0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        }

    # -------------------------
    # Opening book
    # -------------------------
    def get_book_move(self, board):

        fen_key = board.board_fen()

        if board.fullmove_number == 1:
            return random.choice(self.opening_book["start"])

        if fen_key in self.opening_book:
            return random.choice(self.opening_book[fen_key])

        return None

    # -------------------------
    # Evaluation
    # -------------------------
    def evaluate_board(self, board):

        score = 0

        # Material
        for piece in self.values:
            score += len(board.pieces(piece, chess.WHITE)) * self.values[piece]
            score -= len(board.pieces(piece, chess.BLACK)) * self.values[piece]

        # Piece-square tables
        for square in chess.SQUARES:

            piece = board.piece_at(square)

            if not piece:
                continue

            if piece.piece_type == chess.PAWN:

                if piece.color == chess.WHITE:
                    score += self.pawn_table[square]
                else:
                    score -= self.pawn_table[chess.square_mirror(square)]

            elif piece.piece_type == chess.KNIGHT:

                if piece.color == chess.WHITE:
                    score += self.knight_table[square]
                else:
                    score -= self.knight_table[chess.square_mirror(square)]

        # Center control
        for square in self.center:

            piece = board.piece_at(square)

            if piece:
                if piece.color == chess.WHITE:
                    score += 20
                else:
                    score -= 20

        # Mobility
        mobility = len(list(board.legal_moves))

        if board.turn == chess.WHITE:
            score += mobility * 2
        else:
            score -= mobility * 2

        # Check bonus
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
    # Quiescence search
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
    # Alpha-beta search
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
    # Main move function
    # -------------------------
    def get_move(self, fen):

        board = chess.Board(fen)

        # Opening book
        book_move = self.get_book_move(board)
        if book_move:
            return book_move

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

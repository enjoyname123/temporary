
"""
Handling the AI moves.
"""
import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findBestMove(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


# Add these global variables to track board history and half-move count
board_states = {}
half_move_count = 0

def isInsufficientMaterial(game_state):
    """
    Check for insufficient material.
    """
    white_pieces = []
    black_pieces = []
    for row in game_state.board:
        for square in row:
            if square != "--":
                if square[0] == "w":
                    white_pieces.append(square[1])
                else:
                    black_pieces.append(square[1])
    # Check for King vs King
    if len(white_pieces) == 1 and len(black_pieces) == 1:
        return True
    # Check for King and Bishop vs King
    if (len(white_pieces) == 2 and "B" in white_pieces and len(black_pieces) == 1) or \
       (len(black_pieces) == 2 and "B" in black_pieces and len(white_pieces) == 1):
        return True
    # Check for King and Knight vs King
    if (len(white_pieces) == 2 and "N" in white_pieces and len(black_pieces) == 1) or \
       (len(black_pieces) == 2 and "N" in black_pieces and len(white_pieces) == 1):
        return True
    # Check for King and two Knights vs King
    if (len(white_pieces) == 3 and white_pieces.count("N") == 2 and len(black_pieces) == 1) or \
       (len(black_pieces) == 3 and black_pieces.count("N") == 2 and len(white_pieces) == 1):
        return True
    return False


def isThreefoldRepetition(game_state):
    """
    Check for threefold repetition using a simplified board state.
    """
    global board_states
    board_fen = str(game_state.board) + str(game_state.white_to_move)
    board_states[board_fen] = board_states.get(board_fen, 0) + 1
    if board_states[board_fen] >= 3:
        return True
    return False


def isFiftyMoveRule():
    """
    Check for the 50-move rule.
    """
    global half_move_count
    return half_move_count >= 100


def scoreBoard(game_state):
    """
    Enhanced scoring function to include insufficient material, threefold repetition, and 50-move rule.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    elif game_state.stalemate or isInsufficientMaterial(game_state) or isThreefoldRepetition(game_state) or isFiftyMoveRule():
        return STALEMATE
    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                elif piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score
    return score


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    NegaMax with Alpha-Beta pruning and tracking for the 50-move rule and threefold repetition.
    """
    global next_move, half_move_count

    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    # Move ordering - implement later
    max_score = -CHECKMATE
    for move in valid_moves:
        # Track 50-move rule
        is_capture_or_pawn = game_state.board[move.start_row][move.start_col][1] == "p" or \
                             game_state.board[move.end_row][move.end_col] != "--"
        if is_capture_or_pawn:
            half_move_count = 0
        else:
            half_move_count += 1

        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        game_state.undoMove()

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score

def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)

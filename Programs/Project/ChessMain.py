import pygame as p
import ChessEngine, ChessAI
import sys
import os
import datetime
from multiprocessing import Process, Queue
import tempfile

# Constants
BOARD_WIDTH = BOARD_HEIGHT = 512    
MOVE_LOG_PANEL_WIDTH = 320
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def loadImages():
    """
    Initialize a global dictionary of images. This will be called exactly once in the main.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def main():
    """
    The main driver for the game. This will handle user input and updating the graphics.
    """
    p.init()
    icon = p.image.load('images/chess_icon.png')
    p.display.set_icon(icon)
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    p.display.set_caption("Chess Game!")
    clock = p.time.Clock()
    multiplayer_mode = chooseGameMode(screen)
    player_one = True
    player_two = multiplayer_mode
    screen.fill(p.Color("#FFFFFF"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    loadImages()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            elif e.type == p.KEYDOWN:
                if e.key in (p.K_z, p.K_u):
                    if len(game_state.move_log) >= 2:
                        game_state.undoMove()
                        game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key in (p.K_p, p.K_s):
                    saveScreenshot(screen)
                if e.key in (p.K_e, p.K_q):
                    p.quit()
                    sys.exit()

        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate or game_state.stalemate:
            game_over = True
            if game_state.checkmate:
                if game_state.white_to_move:
                    drawEndGameText(screen, "Black wins by checkmate")
                else:
                    drawEndGameText(screen, "White wins by checkmate")
            elif game_state.stalemate:
                drawEndGameText(screen, "Stalemate")
            saveEndGame(screen, game_state)

        clock.tick(MAX_FPS)
        p.display.flip()

def chooseGameMode(screen):
    """
    Display the game mode selection screen and return the selected mode.
    """
    background = p.image.load('images/background.jpg')
    background = p.transform.scale(background, (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    overlay = p.Surface((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 139, 100))
    background.blit(overlay, (0, 0))
    font_title = p.font.SysFont("Roboto", 48, True, False)
    font_button = p.font.SysFont("Roboto", 36, True, False)
    title_color = p.Color("white")
    button_base_color = p.Color("#1C75D9")
    button_hover_color = p.Color("#3A7CA5")
    title_bg_color = p.Color("#155D8B")
    title_text = font_title.render("Choose Game Mode", True, title_color)
    title_text_width = title_text.get_width()
    title_text_height = title_text.get_height()
    padding = 18.9
    title_x_position = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2 - title_text_width // 2
    title_bg_rect = p.Rect(
        title_x_position - padding,
        100 - padding,
        title_text_width + (2 * padding),
        title_text_height + (2 * padding)
    )
    p.draw.rect(screen, title_bg_color, title_bg_rect, border_radius=20)
    title_rect = p.Rect(title_x_position, 100, title_text_width, title_text_height)
    text_friend = font_button.render("Pass and Play with a Friend", True, p.Color("white"))
    text_computer = font_button.render("Play with the Computer", True, p.Color("white"))
    button_width = max(text_friend.get_width(), text_computer.get_width()) + 20
    button_height = 50
    friend_rect = p.Rect(BOARD_WIDTH // 2 - button_width // 2, 250, button_width, button_height)
    computer_rect = p.Rect(BOARD_WIDTH // 2 - button_width // 2, 350, button_width, button_height)
    friend_hover = False
    computer_hover = False

    while True:
        screen.blit(background, (0, 0))
        p.draw.rect(screen, title_bg_color, title_bg_rect, border_radius=20)
        screen.blit(title_text, title_rect)
        mouse_pos = p.mouse.get_pos()
        friend_hover = friend_rect.collidepoint(mouse_pos)
        computer_hover = computer_rect.collidepoint(mouse_pos)
        p.draw.rect(screen, button_hover_color if friend_hover else button_base_color, friend_rect, border_radius=20)
        p.draw.rect(screen, button_hover_color if computer_hover else button_base_color, computer_rect, border_radius=20)
        screen.blit(text_friend, text_friend.get_rect(center=friend_rect.center))
        screen.blit(text_computer, text_computer.get_rect(center=computer_rect.center))

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if friend_hover:
                    return True
                elif computer_hover:
                    return False

        p.display.flip()

def saveScreenshot(screen):
    """
    Save a screenshot of the current screen.
    """
    save_directory = r"C:\23054-AI-051\Python\Project\Chess Shots"
    os.makedirs(save_directory, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chess_screenshot_{timestamp}.png"
    full_path = os.path.join(save_directory, filename)
    p.image.save(screen, full_path)
    print(f"Screenshot saved at {full_path}")

def saveEndGame(screen, game_state):
    """
    Save the end game screenshot and PGN to a temporary directory and prompt the user to save the files.
    """
    temp_dir = os.path.join(os.getcwd(), "temp_Shots")
    os.makedirs(temp_dir, exist_ok=True)
    screenshot_path = os.path.join(temp_dir, "endgame_screenshot.png")
    p.image.save(screen, screenshot_path)
    pgn_path = os.path.join(temp_dir, "game.pgn")
    with open(pgn_path, "w") as pgn_file:
        pgn_file.write(game_state.getPGN())
    promptSaveFiles(screen, screenshot_path, pgn_path, game_state, temp_dir)

def promptSaveFiles(screen, screenshot_path, pgn_path, game_state, temp_dir):
    """
    Prompt the user to save the game files and handle the save operation.
    """
    p.display.quit()
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen.fill(p.Color("white"))
    
    font = p.font.SysFont("Arial", 18)
    displayText(screen, "Press Enter to view the PGN.", font, (20, 20))
    waitForEnter()
    
    screen.fill(p.Color("white"))
    displayText(screen, "Enter White player's name: ", font, (20, 20))
    white_name = waitForInput().strip()
    displayText(screen, "Enter Black player's name: ", font, (20, 50))
    black_name = waitForInput().strip()
    
    result = "1-0" if game_state.white_to_move else "0-1"
    termination = f"{black_name} wins by checkmate" if not game_state.white_to_move else f"{white_name} wins by checkmate"
    date = datetime.datetime.now().strftime("%d.%m.%Y")
    
    pgn_header = f"""[Date "{date}"]
[White "{white_name}"]
[Black "{black_name}"]
[Result "{result}"]
[Termination "{termination}"]

"""
    pgn_text = game_state.getPGN()
    pgn_content = pgn_header + pgn_text
    
    screen.fill(p.Color("white"))
    y_offset = 20
    for line in pgn_content.split("\n"):
        text_surface = font.render(line, True, p.Color("black"))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 25
    
    p.display.flip()
    
    displayText(screen, "Would you like to save this game? (y/n): ", font, (20, y_offset + 30))
    save_game = waitForInput().strip().lower()
    
    if save_game == 'y':
        save_directory = r"C:\23054-AI-051\Python\Project\Chess Shots"
        os.makedirs(save_directory, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        game_folder = os.path.join(save_directory, f"game_{timestamp}")
        os.makedirs(game_folder, exist_ok=True)
        screenshot_dest = os.path.join(game_folder, "chess_screenshot.png")
        pgn_dest = os.path.join(game_folder, "game.txt")
        
        os.replace(screenshot_path, screenshot_dest)
        with open(pgn_dest, "w") as pgn_file:
            pgn_file.write(pgn_content)
        
        displayText(screen, f"Files saved at {game_folder}", font, (20, y_offset + 60))
    else:
        displayText(screen, "Files not saved.", font, (20, y_offset + 60))
    
    # Clean up temp_Shots directory
    os.remove(screenshot_path)
    os.remove(pgn_path)
    os.rmdir(temp_dir)
    
    displayText(screen, "Press Enter to exit.", font, (20, y_offset + 90))
    waitForEnter()
    
    p.quit()
    sys.exit()

def displayText(screen, text, font, position):
    """
    Display text on the screen at the given position.
    """
    text_surface = font.render(text, True, p.Color("black"))
    screen.blit(text_surface, position)
    p.display.flip()

def waitForEnter():
    """
    Wait for the user to press the Enter key.
    """
    while True:
        for event in p.event.get():
            if event.type == p.KEYDOWN and event.key == p.K_RETURN:
                return

def waitForInput():
    """
    Wait for the user to input text and return the input.
    """
    input_text = ""
    while True:
        for event in p.event.get():
            if event.type == p.KEYDOWN:
                if event.key == p.K_RETURN:
                    return input_text
                elif event.key == p.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        p.time.wait(100)

def drawGameState(screen, game_state, valid_moves, square_selected):
    """
    Draw the current game state on the screen.
    """
    drawBoard(screen)
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)

def drawBoard(screen):
    """
    Draw the chess board on the screen.
    """
    colors = [p.Color("#EEEED2"), p.Color("#769656")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight the selected square and valid moves.
    """
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

def drawPieces(screen, board):
    """
    Draw the chess pieces on the board.
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

class GameState:

    def getPGN(self):
        """
        Generate the PGN (Portable Game Notation) for the game.
        """
        pgn = []
        for i in range(0, len(self.move_log), 2):
            move_str = f"{i // 2 + 1}. {self.move_log[i].getChessNotation()}"
            if i + 1 < len(self.move_log):
                move_str += f" {self.move_log[i + 1].getChessNotation()}"
            if self.checkmate:
                move_str += "#"
            pgn.append(move_str)
        return " ".join(pgn)

def drawMoveLog(screen, game_state, font):
    """
    Draw the move log on the screen.
    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('#FFFFFF'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        white_move = f"{i // 2 + 1}. {str(move_log[i])}"
        black_move = str(move_log[i + 1]) if i + 1 < len(move_log) else ""
        move_texts.append((white_move, black_move))
    padding = 5
    line_spacing = 5
    moves_per_row = 4
    text_x = move_log_rect.x + padding
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        row_moves = move_texts[i:i + moves_per_row]
        row_text = "    ".join(f"{w} {b}" for w, b in row_moves)
        text_object = font.render(row_text, True, p.Color('#000000'))
        screen.blit(text_object, (text_x, text_y))
        text_y += text_object.get_height() + line_spacing

def drawEndGameText(screen, text):
    """
    Draw the end game text on the screen.
    """
    font = p.font.SysFont("Helvetica", 48, True, False)
    text_object = font.render(text, False, p.Color("white"))
    text_width = text_object.get_width()
    text_height = text_object.get_height()
    padding = 18.9
    text_x_position = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH) // 2 - text_width // 2
    text_bg_rect = p.Rect(
        text_x_position - padding,
        BOARD_HEIGHT // 2 - text_height // 2 - padding,
        text_width + (2 * padding),
        text_height + (2 * padding)
    )
    button_base_color = p.Color("#1C75D9")
    p.draw.rect(screen, button_base_color, text_bg_rect, border_radius=20)
    screen.blit(text_object, text_object.get_rect(center=text_bg_rect.center))
    p.display.flip()

def animateMove(move, screen, board, clock):
    """
    Animate a move on the screen.
    """
    colors = [p.Color("white"), p.Color("green")]
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 5  # Reduced frames per square for faster animation
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
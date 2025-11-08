import pygame
import random
import subprocess
import sys
import os

# Lấy đường dẫn tuyệt đối đến thư mục chứa file script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(relative_path):
    """(HÀM BỊ THIẾU) Trả về đường dẫn tuyệt đối an toàn."""
    return os.path.join(BASE_DIR, relative_path)

# KHỞI TẠO 
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 MENU CHỌN GAME")
CLOCK = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (220, 220, 220)
LIGHT_GRAY = (245, 245, 245)
BLUE = (50, 120, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 230, 120)

try:
    FONT = pygame.font.Font(None, 36)
    TITLE_FONT = pygame.font.Font(None, 70)
    SMALL_FONT = pygame.font.Font(None, 28) 
except Exception:
    FONT = pygame.font.SysFont("Arial", 36)
    TITLE_FONT = pygame.font.SysFont("Arial", 70)
    SMALL_FONT = pygame.font.SysFont("Arial", 28)

def load_icon(relative_path, size=(120, 120)):
    path = get_path(relative_path)
    if os.path.exists(path):
        try:
            icon = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(icon, size)
        except Exception as e:
            print(f"Lỗi khi tải icon {path}: {e}")
    
    print(f"Không tìm thấy icon: {path}. Tạo icon thay thế.")
    icon_surface = pygame.Surface(size)
    icon_surface.fill(GRAY)
    return icon_surface

#ẢNH NỀN 
bg_path = get_path("Assets/menu_bg.jpg")
if os.path.exists(bg_path):
    background = pygame.image.load(bg_path)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
else:
    print(f"Không tìm thấy ảnh nền: {bg_path}")
    background = None

#Danh Sách Game
games_config = [
    ("Dino Run", get_path("Dino/main.py"), "Logo/DinoJump.png"),
    ("Snake", get_path("Snake/snake.py"), "Logo/Snake.png"),
    ("Flappy Bird", get_path("Flappy bird/flappy_bird.py"), "Logo/bird.png"),
    ("Space Invaders", get_path("Space Invaders/Space_Invaders.py"), "Logo/Space.png"),
    ("TicTacToe", get_path("Tic-Tac-Toe/tictactoe.py"), "Logo/TicTacToe.png"),
    ("Random Game", None, "Logo/Random.png") # File là None
]

print("Đang tải tài nguyên game...")
loaded_games = [
    (name, file_path, load_icon(icon_path)) 
    for name, file_path, icon_path in games_config
]
print("Tải xong!")

#Hàm Chạy Game
def run_game(file_path):
    """Chạy file game Python trong một tiến trình riêng."""
    if not file_path:
        print("Lỗi: Không có file path để chạy (cho nút Random).")
        return

    if not os.path.exists(file_path):
        print(f"LỖI: Không tìm thấy file game: {file_path}")
        return

    try:
        game_dir = os.path.dirname(file_path)
        game_script = os.path.basename(file_path)
        
        print(f"Đang chạy '{game_script}' trong thư mục '{game_dir}'...")
        
        subprocess.run([sys.executable, game_script], cwd=game_dir, check=True)
        
        print(f"Đã quay trở lại menu từ '{game_script}'.")
        
    except Exception as e:
        print(f"Lỗi không xác định khi chạy game: {e}")

#HÀM VẼ NÚT GAME
def draw_game_button(icon_surface, name, x, y, mouse_pos):
    icon_size = icon_surface.get_width()
    button_w, button_h = 160, 45

    button_x = x + (icon_size // 2) - (button_w // 2)
    button_y = y + icon_size + 15
    button_rect = pygame.Rect(button_x, button_y, button_w, button_h)

    total_h = icon_size + button_h + 25
    hover_rect = pygame.Rect(x - 10, y - 10, icon_size + 20, total_h + 10)

    hover = hover_rect.collidepoint(mouse_pos)
    scale = 1.08 if hover else 1.0
    
    icon_scaled = pygame.transform.smoothscale(icon_surface, (int(icon_size * scale), int(icon_size * scale)))
    offset = (icon_scaled.get_width() - icon_size) // 2
    
    if hover:
        shadow_rect = pygame.Rect(x - offset - 4, y - offset - 4, icon_scaled.get_width() + 8, icon_scaled.get_height() + 8)
        pygame.draw.rect(SCREEN, YELLOW, shadow_rect, border_radius=20)
        
    SCREEN.blit(icon_scaled, (x - offset, y - offset))

    # Vẽ nút text
    color = YELLOW if hover else LIGHT_GRAY
    pygame.draw.rect(SCREEN, color, button_rect, border_radius=12)
    border_color = BLUE if hover else BLACK
    border_width = 3 if hover else 2
    pygame.draw.rect(SCREEN, border_color, button_rect, border_width, border_radius=12)

    text_font = FONT
    label = text_font.render(name, True, BLACK)
    if label.get_width() > button_w - 20:
        text_font = SMALL_FONT
        label = text_font.render(name, True, BLACK)
        
    label_rect = label.get_rect(center=button_rect.center)
    SCREEN.blit(label, label_rect)

    return hover_rect 

#MENU CHÍNH 
def main_menu():
    running = True
    
    buttons_layout = []
    start_x = 140
    start_y_top = 180
    start_y_bottom = 420
    spacing_x = 280 

    for i in range(3):
        name, file, icon_surface = loaded_games[i]
        x_pos = start_x + i * spacing_x
        buttons_layout.append((name, file, icon_surface, x_pos, start_y_top))
    
    for i in range(3, 6):
        name, file, icon_surface = loaded_games[i]
        x_pos = start_x + (i - 3) * spacing_x
        buttons_layout.append((name, file, icon_surface, x_pos, start_y_bottom))
    
    clickable_buttons = []

    while running:
        mouse_pos = pygame.mouse.get_pos()
        clickable_buttons.clear() 

        if background:
            SCREEN.blit(background, (0, 0))
        else:
            SCREEN.fill(WHITE)

        title_surf = TITLE_FONT.render(" MENU  GAME", True, BLUE)
        shadow_surf = TITLE_FONT.render(" MENU  GAME", True, (0,0,0, 100))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 60))
        SCREEN.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
        SCREEN.blit(title_surf, title_rect)

        for name, file, icon_surface, x, y in buttons_layout:
            rect = draw_game_button(icon_surface, name, x, y, mouse_pos)
            clickable_buttons.append((rect, file, name)) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, file, name in clickable_buttons:
                    if rect.collidepoint(mouse_pos):
                        print(f"Clicked: {name}")
                        if "Random" in name:
                            valid_games = [g[1] for g in loaded_games[:-1] if g[1] is not None] 
                            if valid_games:
                                random_file = random.choice(valid_games)
                                run_game(random_file)
                        else:
                            run_game(file)
                        
                        pygame.time.wait(200) 

        pygame.display.flip()
        
        CLOCK.tick(60)

#MAIN
if __name__ == "__main__":
    main_menu()
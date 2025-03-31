import pygame

pygame.init()

# Список музыкальных файлов (добавьте свои файлы сюда)
playlist = [
    "Headlock.mp3",
    "Uide.mp3",
    "Sheker.mp3"
]

# Экран
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Playlist")
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
DARK_BLUE = (20, 20, 50)

# Шрифты
font = pygame.font.SysFont(None, 20)

# Кнопки (прямоугольники для кликов)
play_rect = pygame.Rect(370, 590, 70, 70)
pause_rect = pygame.Rect(370, 590, 70, 70)
next_rect = pygame.Rect(460, 587, 70, 70)
prev_rect = pygame.Rect(273, 585, 75, 75)

index = 0
aplay = False

# Загружаем и воспроизводим первую песню
pygame.mixer.music.load(playlist[index]) 
pygame.mixer.music.play(1)
aplay = True 

run = True
while run:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if aplay:
                    aplay = False
                    pygame.mixer.music.pause()
                else:
                    aplay = True
                    pygame.mixer.music.unpause()
            if event.key == pygame.K_RIGHT:
                index = (index + 1) % len(playlist)
                pygame.mixer.music.load(playlist[index])
                pygame.mixer.music.play()
            if event.key == pygame.K_LEFT:
                index = (index - 1) % len(playlist)
                pygame.mixer.music.load(playlist[index])
                pygame.mixer.music.play()
    
    # Отображение названия текущего трека
    text = font.render(playlist[index], True, DARK_BLUE)
    screen.blit(text, (365, 520))
    
    pygame.display.update()
    clock.tick(24)

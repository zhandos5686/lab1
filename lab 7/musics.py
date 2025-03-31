import pygame

pygame.init()

# Музыканың плейлисті (файлдардың атын тікелей жазыңыз)
playlist = ["Headlock.mp3", "Uide.mp3", "Sheker.mp3"]  # Өз әндеріңіздің атын жазыңыз

# Экран параметрлері
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Playlist")
clock = pygame.time.Clock()

# Артқы фон суреті
background = pygame.image.load("background.png")

# Кнопкаларды жүктеу
playb = pygame.image.load("play.png")
pausb = pygame.image.load("pause.png")
nextb = pygame.image.load("next.png")
prevb = pygame.image.load("back.png")

# Фон для кнопок
bg = pygame.Surface((500, 200))
bg.fill((255, 255, 255))

# Музыканың аты шығатын қаріп
font2 = pygame.font.SysFont(None, 20)

index = 0
aplay = False

pygame.mixer.music.load(playlist[index]) 
pygame.mixer.music.play(1)
aplay = True 

run = True
while run:
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

    # Музыка аты шығатын жер 
    text2 = font2.render(playlist[index], True, (20, 20, 50))
    
    # Кнопкалардың орналасуы
    screen.blit(background, (0, 0))
    screen.blit(bg, (155, 500))
    screen.blit(text2, (365, 520))
    
    playb = pygame.transform.scale(playb, (70, 70))
    pausb = pygame.transform.scale(pausb, (70, 70))
    nextb = pygame.transform.scale(nextb, (70, 70))
    prevb = pygame.transform.scale(prevb, (75, 75))
    
    if aplay:
        screen.blit(pausb, (370, 590))
    else: 
        screen.blit(playb, (370, 590))
    
    screen.blit(nextb, (460, 587))
    screen.blit(prevb, (273, 585))
    
    clock.tick(24)
    pygame.display.update()
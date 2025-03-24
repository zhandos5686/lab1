import pygame

# Initialize pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# Variables
draw_mode = 'line'  # Modes: 'line', 'rect', 'circle', 'eraser'
color = (0, 0, 255)  # Default blue
radius = 10
points = []
drawing = False
start_pos = None

# Main loop
running = True
while running:
    pressed = pygame.key.get_pressed()
    alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
    ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and ctrl_held:
                running = False
            if event.key == pygame.K_F4 and alt_held:
                running = False
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # Color selection
            if event.key == pygame.K_r:
                color = (255, 0, 0)  # Red
            elif event.key == pygame.K_g:
                color = (0, 255, 0)  # Green
            elif event.key == pygame.K_b:
                color = (0, 0, 255)  # Blue
            elif event.key == pygame.K_e:
                draw_mode = 'eraser'
            elif event.key == pygame.K_l:
                draw_mode = 'line'
            elif event.key == pygame.K_c:
                draw_mode = 'circle'
            elif event.key == pygame.K_t:
                draw_mode = 'rect'
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                drawing = True
                start_pos = event.pos
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                end_pos = event.pos
                points.append((start_pos, end_pos, color, draw_mode))
                drawing = False

    screen.fill((0, 0, 0))
    
    for start, end, point_color, mode in points:
        if mode == 'line':
            pygame.draw.line(screen, point_color, start, end, radius)
        elif mode == 'circle':
            center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            radius_circle = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
            pygame.draw.circle(screen, point_color, center, radius_circle, 2)
        elif mode == 'rect':
            rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
            pygame.draw.rect(screen, point_color, rect, 2)
        elif mode == 'eraser':
            pygame.draw.line(screen, (0, 0, 0), start, end, radius * 2)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
from Engine import Engine
import pygame
import pygame_gui


def get_simulation_parameters():
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Ustawienia symulacji")
    manager = pygame_gui.UIManager((600, 500))

    labels = [
        "N_VEHICLES", "DELTA_T", "V_0", "SMALL_DELTA",
        "MINIMAL_DISTANCE", "T", "A", "B"
    ]
    default_values = [
        "10", "0.03", "60", "6", "2", "1.5", "5", "6"
    ]
    input_fields = []

    for i, (label, default) in enumerate(zip(labels, default_values)):
        y = 50 + i * 50
        pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, y), (200, 30)),
                                    text=label, manager=manager)
        input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((250, y), (200, 30)), manager=manager)
        input_box.set_text(default)
        input_fields.append(input_box)

    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((200, 500 - 50), (200, 40)),
        text="Start symulacji", manager=manager)

    clock = pygame.time.Clock()
    running = True
    values = None

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    try:
                        values = [float(field.get_text()) if '.' in field.get_text()
                                  else int(field.get_text()) for field in input_fields]
                        running = False
                    except ValueError:
                        print("Wprowadź poprawne wartości liczbowe.")

            manager.process_events(event)

        manager.update(time_delta)
        screen.fill((255, 255, 255))
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
    return values


if __name__ == '__main__':
    params = get_simulation_parameters()
    engine = Engine(*params)
    engine.run()

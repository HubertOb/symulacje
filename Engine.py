import math
from random import random
import pygame

from Vehicle import Vehicle


class Engine:
    def __init__(self, n_vehicles, delta_t, v_0, small_delta, minimal_distance, T, a, b):
        self.n_vehicles = n_vehicles
        self.vehicles_tab = []
        self.delta_t = delta_t  # używana tylko jako wartość startowa
        self.current_time = 0
        self.running = True
        self.v_0 = v_0
        self.small_delta = small_delta
        self.minimal_distance = minimal_distance
        self.T = T
        self.a = a
        self.b = b
        self.leading_car_acc = 0
        self.paused=False
        self.rectangles_colour=[]
        self.WHITE, self.GRAY, self.BLUE, self.BLACK, self.RED = (255, 255, 255), (150, 150, 150), (0, 100, 255), (0, 0, 0), (255, 0, 0)

    def _initialize(self):
        for i in range(self.n_vehicles):
            xPos = 0 if i == 0 else self.vehicles_tab[-1].getXPos() + self.vehicles_tab[-1].getVehLength() + self.minimal_distance + 2 * random()
            vehLen = 3 + 4 * random()
            veh = Vehicle(xPos=xPos, veh_length=vehLen)
            self.vehicles_tab.append(veh)
            self.rectangles_colour.append(self.BLACK)

    def _desired_distance(self, v_i, v_i_prev):
        return self.minimal_distance + v_i * self.T + ((v_i - v_i_prev) * v_i / (2 * math.sqrt(self.a * self.b)))

    def _accelerate(self, v_i, v_i_prev, x_i, x_i_prev, x_len):
        return self.a * (1 - math.pow(v_i / self.v_0, self.small_delta) -
                         math.pow(self._desired_distance(v_i, v_i_prev) / (x_i - x_i_prev - x_len), 2))

    def _accelerate_leading_car(self, v_i):
        return self.a * (1 - math.pow(v_i / self.v_0, self.small_delta))

    def stop(self):
        self.running = False

    def _update_vehicles_params(self, dt):
        first_veh_speed = self.vehicles_tab[0].getSpeed()
        first_veh_pos = self.vehicles_tab[0].getXPos()

        if self.leading_car_acc == 0:
            acc = self._accelerate_leading_car(first_veh_speed)
            new_speed = max(0, first_veh_speed + acc * dt)
        else:
            new_speed = max(0, first_veh_speed - self.leading_car_acc * dt)

        self.vehicles_tab[0].setSpeed(new_speed)
        self.vehicles_tab[0].setXPos(first_veh_pos - new_speed * dt)

        for i in range(1, len(self.vehicles_tab)):
            curr = self.vehicles_tab[i]
            prev = self.vehicles_tab[i - 1]
            acc = self._accelerate(curr.getSpeed(), prev.getSpeed(), curr.getXPos(), prev.getXPos(), curr.getVehLength())
            new_speed = max(0, curr.getSpeed() + acc * dt)
            curr.setSpeed(new_speed)
            curr.setXPos(curr.getXPos() - new_speed * dt)

    def _check_collisions(self):
        for i in range(len(self.vehicles_tab) - 1):
            rear_car = self.vehicles_tab[i + 1]
            front_car = self.vehicles_tab[i]

            rear_x = rear_car.getXPos()
            front_len = front_car.getVehLength()
            front_x = front_car.getXPos()

            if front_x + front_len > rear_x:
                print(f"Kolizja: pojazd {i + 1} uderzył w pojazd {i}")
                self.rectangles_colour[i+1]=self.RED
                self.paused=True

    def run(self):
        self._initialize()
        pygame.init()
        screen = pygame.display.set_mode((1200, 700))
        pygame.display.set_caption('Symulacja ruchu drogowego')

        slider_x, slider_y, slider_width, slider_height, handle_radius = 100, 100, 400, 10, 10
        min_val, max_val = 0.0, self.b
        dragging = False

        # Tło
        background = pygame.image.load("road_background2.png").convert()
        bg_width = background.get_width()

        clock = pygame.time.Clock()

        def draw_slider(value):
            pygame.draw.rect(screen, self.GRAY, (slider_x, slider_y, slider_width, slider_height))
            rel_x = int(((value - min_val) / (max_val - min_val)) * slider_width)
            handle_x = slider_x + rel_x
            pygame.draw.circle(screen, self.BLUE, (handle_x, slider_y + slider_height // 2), handle_radius)
            font = pygame.font.SysFont(None, 24)
            text = font.render(f'Siła hamowania pierwszego samochodu: {value:.2f}', True, self.BLACK)
            screen.blit(text, (slider_x, slider_y - 30))

        while self.running:
            dt = clock.tick(60) / 1000.0

            screen.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    handle_x = slider_x + int(((self.leading_car_acc - min_val) / (max_val - min_val)) * slider_width)
                    if (mx - handle_x) ** 2 + (my - (slider_y + slider_height // 2)) ** 2 <= handle_radius ** 2:
                        dragging = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    rel_x = max(0, min(event.pos[0] - slider_x, slider_width))
                    self.leading_car_acc = min_val + (rel_x / slider_width) * (max_val - min_val)

            draw_slider(self.leading_car_acc)

            x1 = (0 - self.vehicles_tab[0].getXPos() * 10) % bg_width
            x2 = x1 - bg_width
            screen.blit(background, (x1, 250))
            screen.blit(background, (x2, 250))

            for ind,veh in enumerate(self.vehicles_tab):
                x = veh.getXPos() * 10 - self.vehicles_tab[0].getXPos() * 10 + 10
                rect = pygame.Rect(x, 500, veh.getVehLength() * 10, 50)
                pygame.draw.rect(screen, self.rectangles_colour[ind], rect)


            pygame.display.flip()

            if not self.paused:
                self._check_collisions()
                self._update_vehicles_params(dt)

        # pygame.quit()

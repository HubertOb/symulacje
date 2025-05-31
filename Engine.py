import math
from random import random
# from time import sleep, time
import time
import pygame
import pygame_gui
from torch.distributed import barrier

from Vehicle import Vehicle


class Engine:
    def __init__(self, n_vehicles, delta_t, v_0, small_delta, minimal_distance, T, a, b):
        self.n_vehicles = n_vehicles
        self.vehicles_tab = []
        self.delta_t = delta_t
        self.current_time = 0
        self.running = True
        self.v_0 = v_0
        self.small_delta = small_delta
        self.minimal_distance = minimal_distance  # s0
        self.T = T  # czas odstepu
        self.a = a
        self.b = b
        self.leading_car_acc=0

    def _initialize(self):
        for i in range(self.n_vehicles):
            if i == 0:
                xPos = 0
            else:
                xPos = self.vehicles_tab[-1].getXPos() + self.vehicles_tab[
                    -1].getVehLength() + self.minimal_distance + 2 * random()  # losuję odstęp od poprzedzającego samochodu z przedziału [minimal_distance, 2 + minimal_distance] i ustawiam pozycję pojazdu
            vehLen = 3 + 4 * random()  # długość pojazdu pomiędzy 3 a 7 metrów
            veh = Vehicle(xPos=xPos, veh_length=vehLen)
            self.vehicles_tab.append(veh)

    def _desired_distance(self, v_i, v_i_prev):
        return self.minimal_distance + v_i * self.T + ((v_i - v_i_prev) * v_i / (2 * math.sqrt(self.a * self.b)))

    def _accelerate(self, v_i, v_i_prev, x_i, x_i_prev, x_len):
        return self.a * (1 - math.pow(v_i / self.v_0, self.small_delta) - math.pow(
            self._desired_distance(v_i, v_i_prev) / (x_i - x_i_prev - x_len), 2))

    def _accelerate_leading_car(self, v_i):
        return self.a * (1 - math.pow(v_i / self.v_0, self.small_delta))

    def stop(self):
        self.running = False

    def _update_vehicles_params(self):
        first_veh_speed = self.vehicles_tab[0].getSpeed()
        first_veh_pos = self.vehicles_tab[0].getXPos()
        if self.leading_car_acc == 0:
            self.vehicles_tab[0].setSpeed(
                max(0, first_veh_speed + self._accelerate_leading_car(first_veh_speed) * self.delta_t))
        else:
            self.vehicles_tab[0].setSpeed(
                max(0, first_veh_speed - self.leading_car_acc * self.delta_t))
        self.vehicles_tab[0].setXPos(first_veh_pos - self.vehicles_tab[0].getSpeed() * self.delta_t)

        for i in range(1, len(self.vehicles_tab)):
            curr_speed = self.vehicles_tab[i].getSpeed()
            curr_pos = self.vehicles_tab[i].getXPos()
            prev_speed = self.vehicles_tab[i - 1].getSpeed()
            prev_pos = self.vehicles_tab[i - 1].getXPos()

            self.vehicles_tab[i].setSpeed(max(0,
                                              curr_speed + self._accelerate(curr_speed, prev_speed, curr_pos, prev_pos,
                                                                            self.vehicles_tab[
                                                                                i].getVehLength()) * self.delta_t))
            self.vehicles_tab[i].setXPos(curr_pos - self.vehicles_tab[i].getSpeed() * self.delta_t)

    def run(self):
        self._initialize()
        pygame.init()

        WIDTH, HEIGHT = 1200, 700
        WHITE = (255, 255, 255)
        GRAY = (150, 150, 150)
        BLUE = (0, 100, 255)
        BLACK = (0, 0, 0)
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Symulacja ruchu drogowego')
        # barrierPos = 0

        # Suwak
        slider_x = 100  # pozycja X suwaka
        slider_y = 100  # pozycja Y suwaka
        slider_width = 400
        slider_height = 10
        handle_radius = 10

        # Wartości
        min_val = 0.0
        max_val = self.b
        # value = 0.0  # wartość początkowa
        dragging = False

        background = pygame.image.load("road_background2.png").convert()
        bg_width = background.get_width()

        # Pozycje tła
        x1 = 0
        x2 = -bg_width

        def draw_slider(value):
            # pasek suwaka
            pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_width, slider_height))

            # pozycja uchwytu
            rel_x = int(((value - min_val) / (max_val - min_val)) * slider_width)
            handle_x = slider_x + rel_x
            handle_y = slider_y + slider_height // 2

            # uchwyt
            pygame.draw.circle(screen, BLUE, (handle_x, handle_y), handle_radius)

            # tekst
            font = pygame.font.SysFont(None, 24)
            text = font.render(f'Siła hamowania pierwszego samochodu: {value:.2f}', True, BLACK)
            screen.blit(text, (slider_x, slider_y - 30))

        # last_time = time.time()
        while self.running:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    handle_x = slider_x + int(((self.leading_car_acc - min_val) / (max_val - min_val)) * slider_width)
                    handle_y = slider_y + slider_height // 2
                    if (mouse_x - handle_x) ** 2 + (mouse_y - handle_y) ** 2 <= handle_radius ** 2:
                        dragging = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False

                elif event.type == pygame.MOUSEMOTION and dragging:
                    mouse_x = event.pos[0]
                    rel_x = max(0, min(mouse_x - slider_x, slider_width))
                    self.leading_car_acc = min_val + (rel_x / slider_width) * (max_val - min_val)

            draw_slider(self.leading_car_acc)
            x1 = (0-self.vehicles_tab[0].getXPos() * 10)%bg_width
            x2 = (0-self.vehicles_tab[0].getXPos() * 10)%bg_width-bg_width

            if x1 <= -bg_width:
                x1 = x2 + bg_width
            if x2 <= -bg_width:
                x2 = x1 + bg_width

            screen.blit(background, (x1, 250))
            screen.blit(background, (x2, 250))

            # barrierPos = (0 - self.vehicles_tab[0].getXPos() * 10) % WIDTH
            # barrier = pygame.Rect(barrierPos, 500, 300, 20)
            # pygame.draw.rect(screen, BLACK, barrier)

            print(str(self.vehicles_tab[0].getSpeed()) + "               " + str(self.vehicles_tab[0].getXPos()))

            for veh in self.vehicles_tab:
                rect = pygame.Rect(veh.getXPos() * 10 - self.vehicles_tab[0].getXPos() * 10 + 10, 500,
                                   veh.getVehLength() * 10, 50)
                pygame.draw.rect(screen, BLACK, rect)

            pygame.display.flip()
            pygame.time.Clock().tick(60)
            # self.current_time +=self.delta_t
            # curr_time=time.time()
            self._update_vehicles_params()
            time.sleep(self.delta_t)

        pygame.quit()

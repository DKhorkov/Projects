import sys
import pygame
from time import sleep

from settings import Settings
from ship import Ship
from bullet import Bullets
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


# Для создания пустого окна, в котором будет запускаться игра создадим класс:
class AlienInvasion:
    """Класс для управления ресурсами и поведением игры."""

    def __init__(self):
        """Инициализация игры и ресурсов."""
        pygame.init()  # Команда для запуска в работу библиотеки 'pyGame'.

        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption('Alien Invasion')  # Устанавливает название окна игры.

        self.stats = GameStats(self.settings)  # Создаем экземпляр игровой статистики.
        self.scoreboard = Scoreboard(self.screen, self.settings, self.stats)

        self.ship = Ship(self.screen, 'images/ship3.bmp')  # Передаем атрибуту 'ship' атрибут экрана.

        self.bullets = pygame.sprite.Group()  # Создаем "список", хранящий в себе выпущенные снаряды.

        self.aliens = pygame.sprite.Group()  # Создаем "список", хранящий в себе пришельцев.
        self.__create_fleet()

        self.play_button = Button(self.screen, 'Play')  # Создание кнопки для начала игры.
        self.pause_button = Button(self.screen, 'Pause')  # Создание кнопки для паузы игры.
        self.stop_flag = False  # Флаг для корректной работы игры в режиме паузы.

        self.__create_level_buttons()

    def __create_level_buttons(self):
        """Создание кнопок для выбора сложности"""
        self.easy_level_button = Button(self.screen, 'EASY')
        self.easy_level_button.rect.x -= 300
        self.easy_level_button.rect.y += 100
        self.easy_level_button.text_image_rect.center = self.easy_level_button.rect.center

        self.medium_level_button = Button(self.screen, 'MEDIUM')
        self.medium_level_button.rect.y += 100
        self.medium_level_button.text_image_rect.center = self.medium_level_button.rect.center

        self.hard_level_button = Button(self.screen, 'HARD')
        self.hard_level_button.rect.x += 300
        self.hard_level_button.rect.y += 100
        self.hard_level_button.text_image_rect.center = self.hard_level_button.rect.center
        self.level_selected = False

    def __screen_changes_after_lvl_selection(self):
        """Изменения атрибутов и их прорисовка на экране после выбора уровня сложности пользователем"""
        self.ship.ship_start_position()
        self.scoreboard.draw_ships()  # Рисует кол-во жизней при запуске игры.
        self.scoreboard.draw_level()  # При запуске игры рисует уровень сложности.
        self.scoreboard.draw_score()  # При запуске игры количество очков будет равно нулю.
        self.level_selected = True
        pygame.mouse.set_visible(False)

    def __check_game_level(self, event):
        """Выбор уровня игры"""
        if event.key == pygame.K_h:
            for i in range(self.settings.hard_level):
                self.settings.increase_game()
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.stats.level = self.settings.hard_level
            self.__screen_changes_after_lvl_selection()
        elif event.key == pygame.K_m:
            for i in range(self.settings.medium_level):
                self.settings.increase_game()
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.stats.level = self.settings.medium_level
            self.__screen_changes_after_lvl_selection()
        elif event.key == pygame.K_e:
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.__screen_changes_after_lvl_selection()

    def __check_keydown_events(self, event):
        """Проверяет события при нажатии клавиш."""
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:  # Второй способ для пользователя закрыть программу, нажав 'q'.
            sys.exit()
        elif event.key == pygame.K_SPACE:  # Стреляем снарядами при нажатии пробела.
            self.__fire_bullet()
        elif event.key == pygame.K_p:  # Игра запустится при нажатии кнопки 'p' - play.
            self.settings.initialize_dynamic_settings()  # При начале игры устанавливаются базовые настройки скорости.
            self.__start_game()
        elif not self.stop_flag and event.key == pygame.K_ESCAPE:  # Игра ставится на паузу, если нажать клавишу "esc".
            pygame.mouse.set_visible(True)
            self.stop_flag = True
            self.stats.game_active = False
        elif self.stop_flag and event.key == pygame.K_ESCAPE:  # Продолжить игру после паузы.
            pygame.mouse.set_visible(False)
            self.stop_flag = False
            self.stats.game_active = True
        elif self.stats.game_active and not self.level_selected:  # Выбор сложности, чтобы начать игру.
            self.__check_game_level(event)

    def __check_keyup_events(self, event):
        """Проверяет события при отпускании клавиш."""
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = False
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.ship.moving_down = False

    def __check_play_button(self, mouse_position):
        """Проверяет, не нажата ли кнопка 'play_button'."""
        button_clicked = self.play_button.rect.collidepoint(mouse_position)

        # Если игра активна и не на паузе, то нажатие на невидимую кнопку ее не перезапустит:
        if button_clicked and not self.stop_flag and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()  # При начале игры устанавливаются базовые настройки скорости.
            self.__start_game()

    def __check_lvl_buttons_vs_mouse_collision(self, mouse_position):
        """Проверяет, не нажата ли одна из кнопок сложности мышкой."""
        easy_button_clicked = self.easy_level_button.rect.collidepoint(mouse_position)
        medium_button_clicked = self.medium_level_button.rect.collidepoint(mouse_position)
        hard_button_clicked = self.hard_level_button.rect.collidepoint(mouse_position)
        if easy_button_clicked and self.stats.game_active and not self.level_selected:
            self.__screen_changes_after_lvl_selection()
        elif medium_button_clicked and self.stats.game_active and not self.level_selected:
            for i in range(self.settings.medium_level):
                self.settings.increase_game()
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.stats.level = self.settings.medium_level
            self.__screen_changes_after_lvl_selection()
        elif hard_button_clicked and self.stats.game_active and not self.level_selected:
            for i in range(self.settings.hard_level):
                self.settings.increase_game()
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.stats.level = self.settings.hard_level
            self.__screen_changes_after_lvl_selection()

    def __check_pause_button(self, mouse_position):
        """Проверяет, не нажата ли кнопка 'pause_button'."""
        button_clicked = self.pause_button.rect.collidepoint(mouse_position)

        if button_clicked and self.stop_flag and not self.stats.game_active:
            self.stop_flag = False
            self.stats.game_active = True

    def __start_game(self):
        """Запуск игры."""
        self.stats.game_active = True

        if self.level_selected:
            # Очистка списков пришельцев и снарядов:
            self.aliens.empty()
            self.bullets.empty()

            # Создание нового флота и корабля в изначальной позиции:
            self.__create_fleet()
            pygame.mouse.set_visible(False)  # Скрыть мышь в активной игре.

    def __check_events(self):  # Делаем метод приватным.
        """Проверяет события в программе."""
        for event in pygame.event.get():  # Идентифицирует каждое событие в программе.
            if event.type == pygame.QUIT:  # Если пользователь нажал кнопку закрытия программы, то игра закроется.
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # Если нажать кнопку, корабль начнет движение.
                self.__check_keydown_events(event)
            elif event.type == pygame.KEYUP:  # Если отпустить кнопку, то корабль перестанет двигаться.
                self.__check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.__check_play_button(mouse_pos)
                self.__check_lvl_buttons_vs_mouse_collision(mouse_pos)
                self.__check_pause_button(mouse_pos)

    def __create_alien(self, alien_number, alien_row):
        """Создает одного пришельца."""
        alien = Alien(self.screen, self.settings)
        alien_width, alien_height = alien.rect.size
        alien.x = 0.5 * alien_width + 2 * alien_width * alien_number  # Создает сдвиг каждого нового пришельца вправо.
        alien.y = 1 * alien_height + 1.5 * alien_height * alien_row  # Расстояние между рядами.
        alien.rect.x = alien.x
        alien.rect.y = alien.y
        self.aliens.add(alien)  # Добавляем созданный экземпляр в группу пришельцев.

    def __create_fleet(self):
        """Создает флот пришельцев."""
        alien = Alien(self.screen, self.settings)  # Создаем экземпляр класса пришельца.
        alien_width, alien_height = alien.rect.size  # Множественное присвоение.
        # Ниже представлен отступ с правой стороны экрана. Он нужен для дальнейшего движения ряда вправо.
        available_space_x = self.settings.screen_width - (10 * alien_width)
        # (2 * alien_width) - отступ от пришельца (равный ширине) + создание нового пришельца = 2 ширинам пришельца.
        number_of_aliens_x = available_space_x // (2 * alien_width)

        # Определим, сколько рядов пришельцев можно уместить на экране до корабля.
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (2 * alien_height) - ship_height
        number_of_alien_rows_y = available_space_y // (2 * alien_height)

        # Создадим много рядов (флот) пришельцев:
        for alien_row in range(number_of_alien_rows_y):
            for alien_number in range(number_of_aliens_x):
                self.__create_alien(alien_number, alien_row)

    def __fire_bullet(self):
        """Создание выстрела пулей и включение пули в группу."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullets(self.screen, self.settings, self.ship)
            self.bullets.add(new_bullet)

    def __change_fleet_direction(self):
        """Меняет направление движения флота при достижении края."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed_factor
        self.settings.fleet_direction *= -1

    def __check_fleet_edges(self):
        """Проверяет, не достиг ли флот одного из краев экрана."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.__change_fleet_direction()
                break

    def __ship_hit(self):
        """Обработка столкновения пришельцев с кораблем."""
        if self.stats.ships_left > 1:  # Проверка наличия оставшихся кораблей.
            self.stats.ships_left -= 1  # Уменьшаем количество кораблей при столкновении.
            self.scoreboard.draw_ships()

            # Очистим флот и пули:
            self.bullets.empty()
            self.aliens.empty()

            # Создаем новый флот и перемещаем корабль в изначальную позицию в "midbottom":
            self.__create_fleet()
            self.ship.ship_start_position()

            # Пауза до создания нового флота
            sleep(1)  # 1 sec.
        else:
            self.stats.reset_stats()  # Сброс игровой статистики при нажатии кнопки.
            self.stats.game_active = False
            self.level_selected = False
            pygame.mouse.set_visible(True)  # Снова делает курсор мыши видимым, когда игра неактивна.

    def __check_aliens_and_bottom(self):
        """Проверяется, не достиг ли флот пришельцев нижнего края экрана."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:  # Если пришелец достиг края экрана, мы теряем корабль.
                self.__ship_hit()
                break

    def __update_aliens(self):
        """Обновляет местоположение всех пришельцев."""
        self.__check_fleet_edges()
        self.aliens.update()

        # Проверка столкновения (коллизии) корабля с группой пришельцев:
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.__ship_hit()

        self.__check_aliens_and_bottom()  # Проверка, достигли ли пришельцы низа экрана.

    def __check_aliens_and_bullets_collision(self):
        """Проверяет, столкнулись ли пришельцы с пулями.
        Если да - удаляются и пуля, и пришелец. Если все пришельцы убиты, флот создается заново."""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            # Регистрация очков за попадание снаряда во всех пришельцев, а не только одного.
            for alians in collisions.values():
                self.stats.score += self.settings.alien_points * len(alians)
            self.scoreboard.draw_score()
            self.scoreboard.check_record()
        if not self.aliens:
            sleep(0.5)  # Пауза на пол секунды, чтобы игрок приготовился к новому флоту.
            self.bullets.empty()
            self.__create_fleet()
            self.settings.increase_game()  # Ускоряем игру при уничтожении всего флота.

            # Увеличения значения уровня:
            self.stats.level += 1
            self.scoreboard.draw_level()

    def __update_bullets(self):
        """Обновляет снаряды и удаляет ненужные снаряды."""
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.top <= 0:  # Если верх пули достигает верхней части экрана, пуля удаляется из игры.
                self.bullets.remove(bullet)

        self.__check_aliens_and_bullets_collision()

    def __update_screen(self):  # Делаем метод приватным.
        """Обновляет изображение на экране."""
        self.screen.blit(self.settings.bg_color, self.settings.bg_color.get_rect())  # Космический фон.
        # self.screen.fill(self.settings.bg_color)  # Обновление цвета экрана перед выводом пользователю.

        self.ship.show_ship()  # Выводим корабль на экран.

        for bullet in self.bullets.sprites():  # Перебираем всю группу снарядов и рисуем каждый снаряд.
            bullet.draw_bullet()
        for elien in self.aliens.sprites():  # Перебираем всю группу пришельцев и рисуем каждый снаряд.
            elien.show_alien()

        self.scoreboard.show_score()  # Вывод на экран счет игрока.

        # Если игра неактивна, отображается кнопка 'play'.
        # Кнопка после отображения других объектов, чтобы быть поверх них.
        if not self.stats.game_active and not self.stop_flag:
            self.play_button.draw_button()

        if self.stats.game_active and not self.level_selected:
            self.easy_level_button.draw_button()
            self.medium_level_button.draw_button()
            self.hard_level_button.draw_button()

        if self.stop_flag:
            self.pause_button.draw_button()

        pygame.display.flip()  # Обновляет экран пользователя после установления цвета и вывода корабля с пулями.

    def run_game(self):
        """Запуск основного цикла игры."""
        while True:
            # Отслеживание действий пользователя на клавиатуре или с помощью мыши. Если "выход", то закрыть игру.
            self.__check_events()
            if self.level_selected and self.stats.game_active:
                self.ship.update_ship_position()
                self.__update_bullets()  # Позиция пуль должна меняться после изменения позиции корабля.
                self.__update_aliens()
            self.__update_screen()


if __name__ == '__main__':
    the_game = AlienInvasion()
    the_game.run_game()

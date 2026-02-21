from typing import Optional
from pathlib import Path
from functools import cache
from datetime import timedelta

import pygame

from interactors.interactors import StopGame
from interface.pixel.presenter import RenderModel, PixelVector, ImageAsset, BoxAsset, PixelPresenter
from interface.pixel.controller import DeviceEvent, PixelController


class PygameView:
    def __init__(self, controller: PixelController, presenter: PixelPresenter, fps: int, screen_name: Optional[str] = None) -> None:
        self._fps = fps
        self._presenter = presenter
        self._controller = controller
        self._is_running = True

        pygame.init()
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(presenter.screen_size)
        pygame.display.set_caption(screen_name or "Pygame")

    def run(self) -> None:
        while self._is_running:
            delta_time = timedelta(milliseconds=self._clock.tick(self._fps))
            self._process_input(delta_time)
            self._draw_frame()

    def _draw_frame(self) -> None:
        self._screen.fill("black")
        for model in self._presenter.render_models:
            self._render(model)
        pygame.display.update()

    def _render(self, model: RenderModel) -> None:
        match model.asset:
            case ImageAsset(file, size):
                self._screen.blit(self._get_image(file, size), model.position)
            case BoxAsset(size, color):
                box = pygame.Rect(model.position, size)
                pygame.draw.rect(self._screen, color, box)
            case _:
                raise RuntimeError
        
    @cache # Assume all image assets can be cached with no problem, resize elsewhere?
    def _get_image(self, file: Path, size: PixelVector):
        image = pygame.image.load(file)
        image.convert_alpha()
        return image

    def _process_input(self, delta_time: timedelta) -> None:
        events = pygame.event.get()
        event_types = [event.type for event in events]
        self._is_running = not pygame.QUIT in event_types

        event = DeviceEvent(
            entity_ids=self._get_hovered_ids(),
            delta_time=delta_time,
            left_click=(pygame.MOUSEBUTTONDOWN in event_types),
            space_key=pygame.key.get_pressed()[pygame.K_SPACE],
            right_key=pygame.key.get_pressed()[pygame.K_RIGHT],
            left_key=pygame.key.get_pressed()[pygame.K_LEFT],
            up_key=pygame.key.get_pressed()[pygame.K_UP],
            down_key=pygame.key.get_pressed()[pygame.K_DOWN],
        )
        try:
            self._controller.update(event)
        except StopGame:
            self._is_running = False

    def _get_hovered_ids(self) -> list[int]:
        result = []
        for model in self._presenter.render_models:
            match model.asset:
                case BoxAsset(size, _):
                    box = pygame.Rect(model.position, size)
                    if box.collidepoint(pygame.mouse.get_pos()):
                        result.append(model.id)
        return result

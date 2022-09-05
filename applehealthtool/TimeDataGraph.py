from typing import Union, Dict

import pygame
from pygame_gui.core import IContainerLikeInterface, UIElement, ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from pygame_gui.elements import UIImage


class UIGraph(UIImage):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 title='',
                 data_config=None,
                 data=None
                 ):
        self._title = title
        self.set_data(data_config, data)
        self._surface = pygame.Surface(relative_rect.size)
        super().__init__(relative_rect,
                         self._surface,
                         manager,
                         container=container,
                         parent_element=parent_element,
                         object_id=object_id,
                         anchors=anchors,
                         visible=visible
                         )

    def set_data(self, config, rows):
        '''
        Set the graph data.

        :param config: dict that maps rows to timestamp, and list of column names to graph as data samples.
            Must contain 'timestamp' and at least one column name.
        :param rows: list of dicts with each dict representing a data sample. Every row must contain all of the columns
            described in config
        :return: None
        '''
        if config is not None:
            assert 'timestamp' in config
            assert 'samples' in config

class UITimeDataGraph(UIGraph):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 manager: IUIManagerInterface,
                 container: Union[IContainerLikeInterface, None] = None,
                 parent_element: UIElement = None,
                 object_id: Union[ObjectID, str, None] = None,
                 anchors: Dict[str, str] = None,
                 visible: int = 1,
                 title='',
                 data=None
                 ):
        super().__init__(relative_rect,
                       manager,
                       container=container,
                       parent_element=parent_element,
                       object_id=object_id,
                       anchors=anchors,
                       visible=visible,
                       title=title,
                       data=data
                       )
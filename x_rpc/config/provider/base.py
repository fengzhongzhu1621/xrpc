from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique
from typing import Dict


@unique
class ConfigProviderType(IntEnum):
    ENV = 1
    PATH = 2


class BaseConfigProvider(metaclass=ABCMeta):
    @abstractmethod
    def load(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def set_options(self, options: Dict, *args, **kwargs) -> None:
        raise NotImplementedError

"""
选择枚举，用于对常量进行处理
"""

import collections
from enum import Enum
from typing import Dict, Tuple

__all__ = [
    "ChoicesValue",
    "ChoicesEnum",
]

ChoicesValue = collections.namedtuple("choices_value", ["id", "name"])


class ChoicesEnum(Enum):

    @classmethod
    def _get_members(cls):
        return cls._members.value

    @classmethod
    def get_choices(cls) -> Tuple:
        members = cls._get_members()
        result = [(member.id, member.name) for member in members]
        return tuple(result)

    @classmethod
    def get_dict_choices(cls) -> Dict:
        members = cls._get_members()
        result = {member.id: member.name for member in members}
        return result

    @classmethod
    def get_choices_drop_down_list(cls):
        members = cls._get_members()
        result = [{"id": member.id, "name": member.name} for member in members]
        return result

"""领域枚举：场景类型等跨模块共享的离散值。"""

from enum import StrEnum


class SceneType(StrEnum):
    SALES = "sales"
    NON_SALES = "non_sales"

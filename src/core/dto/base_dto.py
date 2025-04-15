from dataclasses import dataclass, asdict
from collections.abc import Callable, Sequence
from typing import Any, Generic, Optional, TypeVar
from typing import get_type_hints, get_args, get_origin


RootDTO = TypeVar("RootDTO", bound="BaseDTO")
ListDTO = TypeVar("ListDTO", bound="BaseListDTO")


@dataclass
class BaseDTO:
    """Базовый DTO с маппингом полей при парсинге."""

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        field_map: Optional[dict[str, str]] = None,  # noqa: UP007
    ) -> "BaseDTO":
        """
        Создает DTO из словаря с возможностью маппинга полей.

        :param data: Исходный словарь
        :param field_map: Сопоставление {ключ_в_данных: поле_в_DTO}
        """
        filtered_data = {}

        if field_map is not None:
            for source_key, target_field in field_map.items():
                if source_key in data:
                    filtered_data[target_field] = data[source_key]
        else:
            filtered_data = data.copy()

        return cls(**filtered_data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BaseListDTO(Generic[RootDTO]):
    """Базовый DTO для списков с гибким источником данных."""

    items: Sequence[RootDTO]

    @classmethod
    def from_dict(
        cls: type[ListDTO],
        data: dict[str, Any],
        *,
        items_key: Optional[str] = None,  # noqa: UP007
        field_map: Optional[dict[str, str]] = None,  # noqa: UP007
        filter_func: Optional[Callable[[dict], bool]] = None,  # noqa: UP007, E501
    ) -> ListDTO:
        """
        Создает DTO из словаря с гибким выбором источника данных.

        :param items_key: Ключ в data, где находятся элементы
        :param filter_func: Функция для фильтрации элементов
        """  # noqa: E501
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        if items_key is None:
            items_key = "items"
        raw_items = data.get(items_key, [])

        if isinstance(raw_items, dict):
            raw_items = list(raw_items.values())

        if filter_func is not None:
            raw_items = [item for item in raw_items if filter_func(item)]

        item_type = cls._get_item_type()

        converted_items = [
            (
                item
                if isinstance(item, item_type)
                else item_type.from_dict(item, field_map=field_map)
            )
            for item in raw_items
        ]

        return cls(items=converted_items)

    def to_dict(self) -> dict[str, Any]:
        """Конвертирует DTO в словарь, рекурсивно преобразуя вложенные DTO."""
        result = asdict(self)

        result["items"] = [
            item.to_dict() if isinstance(item, BaseDTO) else item for item in self.items
        ]

        return result

    @classmethod
    def _get_item_type(cls) -> type:
        """Получает тип элементов (RootDTO) из Generic BaseListDTO[RootDTO]."""
        for base in getattr(cls, "__orig_bases__", []):
            if get_origin(base) is BaseListDTO and get_args(base):
                item_type = get_args(base)[0]
                if isinstance(item_type, type):
                    return item_type

        type_hints = get_type_hints(cls)
        if "items" in type_hints:
            item_type = type_hints["items"]
            origin = get_origin(item_type)

            if origin is not None and issubclass(origin, Sequence):
                args = get_args(item_type)
                if args:
                    return args[0]

        raise TypeError(f"Cannot determine item type for {cls.__name__}. ")

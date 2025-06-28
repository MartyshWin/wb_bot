from typing import Any, Union
from pydantic import BaseModel
from enum import Enum
from tabulate import tabulate
from rich import print as rprint
from rich.pretty import pretty_repr
from rich.console import Console

# Пример enum и pydantic модели
class ExampleEnum(Enum):
    FIRST = 1
    SECOND = 2

class ExampleModel(BaseModel):
    id: int
    name: str
    status: ExampleEnum

# Основная функция форматированного вывода
# def pretty_dump(
#     data: Any,
#     style: str = "tabulate",
#     title: str = "Data Dump"
# ) -> None:
#     """
#     Форматированный дамп данных: поддержка list, dict, pydantic, enum и др.
#
#     :param data: Данные для вывода
#     :param style: Стиль вывода: 'tabulate', 'rich', 'repr'
#     :param title: Заголовок дампа
#     """
#     if style == "tabulate":
#         if isinstance(data, list):
#             if all(isinstance(i, BaseModel) for i in data):
#                 data = [i.model_dump() for i in data]
#             elif all(isinstance(i, Enum) for i in data):
#                 data = [{"name": i.name, "value": i.value} for i in data]
#             print(tabulate(data, headers="keys", tablefmt="grid"))
#         elif isinstance(data, BaseModel):
#             print(tabulate([data.model_dump()], headers="keys", tablefmt="grid"))
#         elif isinstance(data, dict):
#             print(tabulate([data], headers="keys", tablefmt="grid"))
#         else:
#             print(f"[Unsupported type for tabulate] {repr(data)}")
#
#     elif style == "rich":
#         console = Console()
#         table = Table(title=title)
#         if isinstance(data, list):
#             if all(isinstance(i, BaseModel) for i in data):
#                 rows = [i.model_dump() for i in data]
#                 if rows:
#                     for key in rows[0].keys():
#                         table.add_column(str(key))
#                     for row in rows:
#                         table.add_row(*[str(v) for v in row.values()])
#             elif all(isinstance(i, Enum) for i in data):
#                 table.add_column("Enum Name")
#                 table.add_column("Enum Value")
#                 for i in data:
#                     table.add_row(i.name, str(i.value))
#         elif isinstance(data, BaseModel):
#             for k, v in data.model_dump().items():
#                 table.add_row(str(k), str(v))
#         elif isinstance(data, dict):
#             for k, v in data.items():
#                 table.add_row(str(k), str(v))
#         else:
#             console.print(f"[Unsupported type for rich] {repr(data)}")
#             return
#         console.print(table)
#
#     elif style == "repr":
#         print(inspect.cleandoc(repr(data)))
#
#     else:
#         print("[Unsupported style]")

class DebugTools:
    console = Console()

    @staticmethod
    def pretty_dump(
        data: Any,
        style: str = "rich",  # rich | tabulate | repr
        title: str = None,
    ) -> None:
        """Универсальный дамп данных в консоль в читаемом виде."""
        if title:
            print(f"\n{title}\n{'=' * len(title)}")

        if style == "tabulate":
            if isinstance(data, list):
                if all(isinstance(d, BaseModel) for d in data):
                    rows = [d.model_dump() for d in data]
                elif all(isinstance(d, dict) for d in data):
                    rows = data
                else:
                    rows = [{"value": str(d)} for d in data]

                print(tabulate(rows, headers="keys", tablefmt="grid", showindex=True))
            elif isinstance(data, BaseModel):
                print(tabulate([data.model_dump()], headers="keys", tablefmt="grid"))
            else:
                print(tabulate([{"value": str(data)}], headers="keys"))

        elif style == "rich":
            DebugTools.console.print(pretty_repr(data))

        else:  # fallback to repr
            print(repr(data))

# # Пример использования
# example = [ExampleModel(id=1, name="Alice", status=ExampleEnum.FIRST),
#            ExampleModel(id=2, name="Bob", status=ExampleEnum.SECOND)]
# example2 = [{'id': 507, 'alarm': 1}, {'id': 686, 'alarm': 1}, {'id': 1733, 'alarm': 1}, {'id': 6144, 'alarm': 1}, {'id': 6145, 'alarm': 1}, {'id': 106476, 'alarm': 1}, {'id': 117501, 'alarm': 1}, {'id': 117986, 'alarm': 1}, {'id': 130744, 'alarm': 1}, {'id': 158751, 'alarm': 1}, {'id': 169872, 'alarm': 1}, {'id': 172430, 'alarm': 1}, {'id': 172940, 'alarm': 1}, {'id': 204939, 'alarm': 1}, {'id': 206236, 'alarm': 1}, {'id': 206298, 'alarm': 1}, {'id': 208277, 'alarm': 1}, {'id': 208941, 'alarm': 1}, {'id': 209207, 'alarm': 1}, {'id': 210127, 'alarm': 1}, {'id': 210515, 'alarm': 1}, {'id': 211622, 'alarm': 1}, {'id': 215020, 'alarm': 1}, {'id': 216476, 'alarm': 1}, {'id': 218210, 'alarm': 1}, {'id': 218623, 'alarm': 1}, {'id': 218987, 'alarm': 1}, {'id': 300169, 'alarm': 1}, {'id': 300219, 'alarm': 1}, {'id': 300461, 'alarm': 1}, {'id': 300571, 'alarm': 1}, {'id': 301229, 'alarm': 1}, {'id': 301760, 'alarm': 1}, {'id': 301805, 'alarm': 1}, {'id': 301809, 'alarm': 1}, {'id': 301981, 'alarm': 1}, {'id': 301983, 'alarm': 1}, {'id': 312617, 'alarm': 1}, {'id': 316879, 'alarm': 1}, {'id': 317470, 'alarm': 1}, {'id': 324108, 'alarm': 1}]
#
# DebugTools.pretty_dump(example, style="tabulate", title="📦 Product Dump")
# DebugTools.pretty_dump(example, style="rich", title="📦 Product Dump")
# DebugTools.pretty_dump(example2, style="repr", title="📦 Product Dump")
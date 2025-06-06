import importlib
import pkgutil
from aiogram import Router
from pathlib import Path

main_router = Router()

# Путь к папке handlers
package_path = Path(__file__).parent
package_name = __name__  # "app.handlers"

# Автоматический импорт всех модулей в handlers
for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
    if is_pkg or module_name.startswith("_"):
        continue

    module = importlib.import_module(f"{package_name}.{module_name}")

    # Проверяем наличие router
    if hasattr(module, "router"):
        router = getattr(module, "router")
        if isinstance(router, Router):
            main_router.include_router(router)
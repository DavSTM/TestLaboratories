import os
import importlib
from flask import Blueprint


def register_blueprints(app):
    base_dir = os.path.dirname(__file__)
    package_name = __name__  # 'handlers'

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                module_path = rel_path.replace(os.sep, ".")[:-3]  # remove '.py'

                full_module = f"{package_name}.{module_path}"
                try:
                    module = importlib.import_module(full_module)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, Blueprint):
                            app.register_blueprint(attr)
                except Exception as e:
                    print(f"[⚠️] Не удалось загрузить модуль {full_module}: {e}")

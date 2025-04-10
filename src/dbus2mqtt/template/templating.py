
from datetime import datetime
from typing import Any

import yaml

from jinja2 import (
    BaseLoader,
    Environment,
    StrictUndefined,
)
from yaml import SafeDumper, SafeLoader


def _represent_template_str(dumper: SafeDumper, data: str):
    data = data.replace("{{", "template:{{", 1)
    data = data.replace("}}", "}}:template", 1)
    # return dumper.represent_str(f"template:{data}:template")
    return dumper.represent_str(data)

class _CustomSafeLoader(SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)

        # Disable parsing ISO date strings
        self.add_constructor('tag:yaml.org,2002:timestamp', lambda _l, n: n.value)

class _CustomSafeDumper(SafeDumper):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.add_representer(_TemplatedStr, _represent_template_str)

class _TemplatedStr(str):
    """A marker class to force template string formatting in YAML."""
    pass

def _mark_templates(obj):
    if isinstance(obj, dict):
        return {k: _mark_templates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_mark_templates(v) for v in obj]
    elif isinstance(obj, str):
        s = obj.strip()
        if s.startswith("{{") and s.endswith("}}"):
            return _TemplatedStr(obj)
    return obj

class TemplateEngine:
    def __init__(self):

        engine_globals = {}
        engine_globals['now'] = datetime.now

        self.jinja2_env = Environment(
            loader=BaseLoader(),
            extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'],
            undefined=StrictUndefined,
            keep_trailing_newline=False
        )

        self.jinja2_async_env = Environment(
            loader=BaseLoader(),
            extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'],
            undefined=StrictUndefined,
            enable_async=True
        )

        self.app_context: dict[str, Any] = {}
        # self.dbus_context: dict[str, Any] = {}

        self.jinja2_env.globals.update(engine_globals)
        self.jinja2_async_env.globals.update(engine_globals)

    def add_functions(self, custom_functions: dict[str, Any]):
        self.jinja2_env.globals.update(custom_functions)
        self.jinja2_async_env.globals.update(custom_functions)

    def update_app_context(self, context: dict[str, Any]):
        self.app_context.update(context)

    def _dict_to_templatable_str(self, value: dict[str, Any]) -> str:
        template_str = _mark_templates(value)
        template_str = yaml.dump(template_str, Dumper=_CustomSafeDumper)
        # value= yaml.safe_dump(value, default_style=None)
        # print(f"_dict_to_templatable_str: {value}")
        template_str = template_str.replace("template:{{", "{{").replace("}}:template", "}}")
        # print(value)
        return template_str

    def _render_result_to_dict(self, value: str) -> dict[str, Any]:
        return yaml.load(value, _CustomSafeLoader)

    def render_template(self, template: str | dict | None, res_type: type, context: dict[str, Any] = {}) -> Any:

        if not template:
            return None

        if res_type not in [dict, str]:
            raise ValueError(f"Unsupported result type: {res_type}")

        dict_template = isinstance(template, dict)
        if dict_template:
            template = self._dict_to_templatable_str(template)

        res = self.jinja2_env.from_string(template).render(**context)

        if res_type is dict:
            res = self._render_result_to_dict(res)

        return res

    async def async_render_template(self, template: str | dict | None, res_type: type, context: dict[str, Any] = {}) -> Any:

        if not template:
            return None

        if res_type not in [dict, str]:
            raise ValueError(f"Unsupported result type: {res_type}")

        dict_template = isinstance(template, dict)
        if dict_template:
            template = self._dict_to_templatable_str(template)

        res = await self.jinja2_async_env.from_string(template).render_async(**context)

        if res_type is dict:
            res = self._render_result_to_dict(res)

        return res

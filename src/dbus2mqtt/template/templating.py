
from typing import Any
from datetime import datetime
import yaml

from jinja2 import (
    BaseLoader,
    Environment,
    StrictUndefined,
)

# class AnsibleCoreFiltersExtension(Extension):

#     def __init__(self, environment):
#         super().__init__(environment)
#         filters = FilterModule().filters()
#         for x in filters:
#             if x in environment.filters:
#                 warnings.warn("Filter name collision detected changing "
#                               "filter name to ans_{0} "
#                               "to avoid clobbering".format(x),
#                               RuntimeWarning)
#                 filters["ans_" + x] = filters[x]
#                 del filters[x]

#         # Register provided filters
#         environment.filters.update(filters)
# def _now():
#     return datetime.now()

class TemplateEngine:
    def __init__(self):

        engine_globals = {}
        engine_globals['now'] = datetime.now


        self.jinja2_env = Environment(
            loader=BaseLoader(),
            extensions=['jinja2_ansible_filters.AnsibleCoreFiltersExtension'],
            undefined=StrictUndefined
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

    def render_template(self, template, context: dict[str, Any] = {}) -> Any:

        if not template:
            return None

        dict_template = isinstance(template, dict)
        if dict_template:
            template = yaml.safe_dump(template, indent=2)

        res = self.jinja2_env.from_string(template).render(**context)

        print(f"res={res}")
        if dict_template:
            res = yaml.safe_load(res)

        return res

    async def async_render_template(self, template, context: dict[str, Any] = {}) -> Any:

        if not template:
            return None

        dict_template = isinstance(template, dict)
        print(f"original template: {template}")
        if dict_template:
            template = yaml.safe_dump(template)
            print(f"safe_dump template: {template}")

        res = await self.jinja2_async_env.from_string(template).render_async(**context)

        if dict_template:
            print(f"res: {res}")
            res = yaml.safe_load(res)

        return res

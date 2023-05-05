from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from apps.settings.local import settings

env = Environment(loader=FileSystemLoader("apps/modules/jinja/templates/"))


def find_template(app_name: str, template_name: str) -> str:
    template = env.get_template(app_name + "/" + template_name + ".html")
    return template


def get_template(
    app_name: str,
    template_name: str,
    template_data,
) -> str:
    template = env.get_template(app_name + "/" + template_name + ".html")
    content = template.render(HOST_URL=settings.URL, **template_data)
    return content

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("apps/modules/jinja/templates/"))

templates = Jinja2Templates(directory="apps/modules/jinja/templates/")


def find_template(
    request: Request, app_name: str, template_name: str, template_data: dict
) -> str:
    # template = env.get_template(app_name + "/" + template_name + ".html")
    # body = template.render(**template_data)
    # return body
    template = templates.get_template(app_name + "/" + template_name + ".html")
    content = template.render(request=request, **template_data)
    return content

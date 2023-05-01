from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("apps/modules/jinja/templates/"))


def find_template(app_name: str, template_name: str, template_data: dict) -> str:
    template = env.get_template(app_name + "/" + template_name + ".html")
    body = template.render(**template_data)
    return body

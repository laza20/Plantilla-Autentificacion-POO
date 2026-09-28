from jinja2 import Environment, FileSystemLoader

class TemplateRenderer:
    def __init__(self, template_dir: str):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, nombre_template: str, **contexto) -> str:
        return self.env.get_template(nombre_template).render(**contexto)


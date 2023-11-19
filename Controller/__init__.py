import os

def create_blueprint(app):
    api_folder = os.path.dirname(__file__)
    for filename in os.listdir(api_folder):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module = __import__(f'Controller.{module_name}', fromlist=[module_name])
            blueprint = getattr(module, f'{module_name}')
            app.register_blueprint(blueprint,url_prefix=f'/{module_name}')
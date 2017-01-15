"""
Main module for managing image scrapper web application
"""
import logging
from scrapper import create_app
from flask_script import Manager, Shell

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create application and bind application manager as well as shell
app = create_app('default')
manager = Manager(app)


def make_shell_context():
    """
    Make context for Shell.
    :return: Application models, database and application object.
    """
    return dict(app=app)

manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()

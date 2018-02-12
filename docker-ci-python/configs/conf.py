import sys

sys.path.append('/project')

project = '{project_name}'
copyright = '{author}'
author = '{author}'

version = '{version}'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinxcontrib.plantuml',
    'sphinx.ext.githubpages'
]

plantuml = 'java -jar /usr/share/plantuml.jar'
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
todo_include_todos = True

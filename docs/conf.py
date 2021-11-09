# -*- coding: utf-8 -*-
#
# NES documentation

# -- General configuration ------------------------------------------------

extensions = [
    'sphinx.ext.autodoc'
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'NES'
copyright = u'NeuroMat, 2021'
author = u'NeuroMat'

version = u'1.72.6'
release = u'1.72.6'

language = 'en'

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_theme_options = {
    "collapse_navigation" : False
}

html_sidebars = { '**': ['globaltoc.html', 'relations.html', 'sourcelink.html', 'searchbox.html'] }

latex_elements = {
}

latex_documents = [
    (master_doc, 'NES.tex', u'NES Documentation',
     u'NeuroMat', 'manual'),
]

# latex_logo = None

# -- Options for manual page output ---------------------------------------

man_pages = [
    (master_doc, 'nes', u'NES Documentation',
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------
texinfo_documents = [
    (master_doc, 'NES', u'NES Documentation',
     author, 'NES', 'One line description of project.',
     'Miscellaneous'),
]

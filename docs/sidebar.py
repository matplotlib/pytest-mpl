"""
Move the top navbar to the sidebar because matplotlib/matplotlib
reserves the top navbar.

Prepend to the sidebar a link to the pytest-mpl documentation homepage.
"""
from bs4 import BeautifulSoup as bs

HOME_LINK = (
    '<li class="toctree-l1{li_active}">'
    '   <a class="{a_active}reference internal" href="{href}">'
    '       Home'
    '   </a>'
    '</li>'
)
HOME_LINK_ACTIVE = HOME_LINK.format(li_active=" current active", a_active="current ", href="#")
HOME_LINK_INACTIVE = HOME_LINK.format(li_active="", a_active="", href="index.html")


def add_toctree_functions(app, pagename, templatename, context, doctree):
    """
    Monkeypatch the pydata-sphinx-theme Jinja function which generates the sidebar.
    """
    f = context["generate_nav_html"]
    home_link = HOME_LINK_INACTIVE if pagename != context["root_doc"] else HOME_LINK_ACTIVE

    def generate_nav_html(kind, startdepth=None, show_nav_level=1, **kwargs):
        if startdepth is None:
            startdepth = 0
        ret = f(kind, startdepth=startdepth, show_nav_level=1, **kwargs)
        if startdepth == 0:
            soup = bs(ret, "html.parser")
            li = bs(home_link, "html.parser")
            soup.ul.insert(0, li)
            ret = soup.prettify(formatter="minimal")
        return ret

    context["generate_nav_html"] = generate_nav_html


def setup(app):
    # Reduce the priority of this hook so it runs after the pydata theme hook
    app.connect("html-page-context", add_toctree_functions, 999)
    return {"parallel_read_safe": True, "parallel_write_safe": True}

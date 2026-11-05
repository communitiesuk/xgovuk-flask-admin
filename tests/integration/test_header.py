"""Integration tests for the header bar text and service navigation name."""

import pytest
from flask import Flask
from flask_admin import Admin
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader

from xgovuk_flask_admin import XGovukFlaskAdmin
from xgovuk_flask_admin.theme import XGovukFrontendTheme


def _make_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    app.jinja_options = {
        "loader": ChoiceLoader(
            [
                PrefixLoader(
                    {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
                ),
                PrefixLoader(
                    {"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}
                ),
                PackageLoader("xgovuk_flask_admin"),
            ]
        )
    }
    Admin(app, theme=XGovukFrontendTheme())
    return app


def _header_html(html):
    start = html.index('class="govuk-generic-header"')
    return html[start : html.index("</header>", start)]


@pytest.mark.integration
class TestHeader:
    def test_header_text_and_service_name_shown_separately(self):
        app = _make_app()
        XGovukFlaskAdmin(app, service_name="Manage widgets", header_text="Widget Dept")

        html = app.test_client().get("/admin/").data.decode("utf-8")
        header = _header_html(html)

        assert "Widget Dept" in header
        assert 'href="/admin/"' in header
        assert "govuk-service-navigation__service-name" in html
        assert "Manage widgets" in html

    def test_header_text_defaults_to_service_name(self) -> None:
        app = _make_app()
        XGovukFlaskAdmin(app, service_name="Manage widgets")

        html = app.test_client().get("/admin/").data.decode("utf-8")

        assert "Manage widgets" in _header_html(html)

    def test_init_app_sets_names(self):
        app = _make_app()
        ext = XGovukFlaskAdmin(None)
        ext.init_app(app, service_name="Manage widgets", header_text="Widget Dept")

        html = app.test_client().get("/admin/").data.decode("utf-8")

        assert "Widget Dept" in _header_html(html)
        assert "Manage widgets" in html

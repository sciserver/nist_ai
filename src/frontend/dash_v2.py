# MIT License

# Copyright (c) 2023 sciserver

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module contains the base UI"""

import os
from typing import List

import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx

import src.backend.repository as repo

DEFAULT_MAP = dl.Map(
    dl.TileLayer(),
    center=[39.135107, -77.218065],
    zoom=14,
    style={"width": "100%", "aspectRatio": "1/1"},
)


def build_app(
    dash_cls: type,
    name: str,
    repo: repo.Repository,
    scripts: List[str] = [],
    stylesheets: List[str] = ["assets/css/bootstrap.min.css"],
) -> dash.Dash:
    """Builds a dash app.

    Note, the class passed in for `dash_cls` could be a JupyterDash class or
    a Dash class. However due to versioning I only include the Dash class as
    a type hint.

    Args:
        dash_cls (dash.Dash): Dash class.
        name (str): Name of the app.
        repo (repo.Repository): Repository object.
        scripts (List[str], optional): List of scripts to include.
        stylesheets (List[str], optional): List of stylesheets to include.

    Returns:
        dash.Dash: Dash app.

    """
    needed_js = [
        "./assets/js/chroma-js/chroma.min.js",
        "./assets/js/dashLeafletHelper.js",
    ]


    global REPO_SINGLETON
    REPO_SINGLETON = repo

    app = dash_cls(
        __name__,
        assets_folder=os.path.join(os.getcwd(), "assets"),
        external_scripts=needed_js + scripts,
        external_stylesheets=stylesheets,
        prevent_initial_callbacks=True,
    )

    app.layout = dbc.Col([
        dbc.Row([
            dbc.Col([], width=2),
            dbc.Col([
                dash.html.Img(src="https://www.nist.gov/libraries/nist-component-library/dist/img/logo/NIST-Logo-Brand-White.svg"),
            ], width=8),
            dbc.Col([], width=2),
        ]),
        dbc.Row([build_search()]),
        dbc.Row([
            dbc.Col([], width=2),
            dbc.Col([
                build_search_results()
            ], width=5),
            dbc.Col([
                build_map()
            ], width=3),
            dbc.Col([], width=2),
        ]),
    ])

    return app


def build_search() -> dbc.Form:
    return dbc.Form([
        dbc.Row([
            dbc.Col([], width=2),
            dbc.Col([
                dbc.Input(id="query", type="text", placeholder="Search")
            ], width=5),
            dbc.Col([
                dbc.Button("Search")
            ], width=3),
            dbc.Col([], width=2),
        ])
    ], id="search-form")

def build_search_results():
    return dash.dash_table.DataTable(
        id="search-results",
        filter_action="native",
        sort_action="native",
    )

def build_map():
    return DEFAULT_MAP

@dash.callback(
    [
        dash.Output("search-results", "data"),
        dash.Output('search-results', 'columns')
    ],
    dash.Input("search-form", "n_submit"),
    dash.State("query", "value"),
    prevent_initial_call=True,
)
def search_form_submitted(n_submit:int, query:str):
    """Callback for when the search form is submitted.

    Args:
        n_submit (int): Number of times the form has been submitted.
        q (str): The query string.

    Returns:
        List[dbc.ListGroupItem]: A list of search results.
    """
    global REPO_SINGLETON

    segments = REPO_SINGLETON.query_text_segments(query)

    return (
        segments.to_dict('records'),
        [{"name": i, "id": i} for i in segments.columns],
    )
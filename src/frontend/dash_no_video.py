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

"""This module contains the function for building a dash based UI."""

import base64
import datetime
import functools
import re
from typing import List, Union

import dash
import dash_bootstrap_components as dbc
import dash_extensions.javascript as dash_js
import dash_leaflet as dl
import dash_leaflet.express as dlx
import numpy as np
import pandas as pd

import src.backend.repository as repo
import src.backend.video_processing as vp

DEFAULT_MAP = dl.Map(
    dl.TileLayer(),
    center=[39.135107, -77.218065],
    zoom=14,
    style={"width": "100%", "aspectRatio": "1/1"},
)

REPO_SINGLETON: repo.Repository = None

POINT_TO_LAYER = dash_js.assign(
    """function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);
    circleOptions.fillColor = csc(feature.properties[colorProp]);
    return L.circleMarker(latlng, circleOptions);
}"""
)


def build_app(
    dash_cls: dash.Dash,
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

    import os

    app = dash_cls(
        __name__,
        assets_folder=os.path.join(os.getcwd(), "assets"),
        external_scripts=needed_js + scripts,
        external_stylesheets=stylesheets,
        prevent_initial_callbacks=True,
    )

    app.layout = dbc.Row(
        [
            # Search and search results
            dbc.Col(
                [
                    build_search_form(),
                    # The spinner component is wrapper that will display a spinner
                    # between changes to the underlying component.
                    dbc.Spinner(dbc.ListGroup(id="search-results")),
                ]
            ),
            # video, thumbnails, map
            dbc.Col(
                [
                    dbc.Spinner(
                        dbc.Carousel(
                            items=[
                                dict(
                                    key="1", src="assets/img/carousel_placeholder.svg"
                                ),
                            ],
                            controls=True,
                            indicators=True,
                            id="video-thumbnails",
                        )
                    ),
                    dbc.Spinner(
                        dbc.Container(
                            children=[
                                DEFAULT_MAP,
                            ],
                            id="map-container",
                        )
                    ),
                ]
            ),
        ]
    )

    return app


def build_search_form(
    text_box_hint: str = "Search Video Text",
    button_text: str = "Search",
) -> dbc.Form:
    """Builds a search form.

    Args:
        text_box_hint (str, optional): Text box hint. Defaults to "Search Video Text".
        button_text (str, optional): Button text. Defaults to "Search".

    Returns:
        dbc.Form: Search form with id="search-form"
    """
    return dbc.Form(
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.FormFloating(
                            [
                                dbc.Input(
                                    type="text", placeholder="type query", id="query"
                                ),
                                dbc.Label(text_box_hint),
                            ]
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Button(button_text, color="primary"),
                    ],
                    width="auto",
                ),
            ],
            align="center",
        ),
        id="search-form",
    )


def convert_search_result_to_button(
    q: str,
    row: pd.DataFrame,
) -> dbc.Card:
    """Converts a row from the search results dataframe to a button.

    Args:
        q (str): The query string.
        row (pd.DataFrame): A row from the search results dataframe.

    Returns:
        dbc.Card: A card with the thumbnail, segment text, and timestamp.
    """
    if row["thumbnail"] and len(row["thumbnail"]):
        img_src = "data:image/png;base64," + base64.b64encode(row["thumbnail"]).decode(
            "ASCII"
        )
    else:
        img_src = "assets/img/thumbnail_missing.svg"

    # We don't want to display the microseconds so subtract them off
    if row["time_start"]:
        td = datetime.timedelta(seconds=row["time_start"])
        td -= datetime.timedelta(microseconds=td.microseconds)
    else:
        td = datetime.timedelta(seconds=0)

    card = dbc.Card(
        [
            dbc.CardLink(
                dbc.Row(
                    [
                        # left side thumbnail
                        dbc.Col(
                            [
                                dbc.CardImg(
                                    src=img_src,
                                ),
                            ]
                        ),
                        # center segment text
                        dbc.Col(
                            dbc.CardBody(
                                highlight(
                                    row["segment"],
                                    q,
                                ),
                            )
                        ),
                        # right side timestamp
                        dbc.Col(
                            [
                                dash.html.Span(
                                    str(td),
                                    className="card-text",
                                ),
                            ]
                        ),
                    ],
                    align="center",
                    justify="center",
                ),
                # id and atrributes for loading search results
                # this is a hack that lets you use improper python attr notation "-" in
                # a property, perhaps change this.
                id={
                    "type": "search-result",
                    "video_id": row["video_id"],
                    "offset": td.seconds,
                },
            )
        ]
    )

    return card


@dash.callback(
    dash.Output("search-results", "children"),
    dash.Input("search-form", "n_submit"),
    dash.State("query", "value"),
    prevent_initial_call=True,
)
def search_form_submitted(n_submit: int, q: str) -> List[dbc.ListGroupItem]:
    """Callback for when the search form is submitted.

    Args:
        n_submit (int): Number of times the form has been submitted.
        q (str): The query string.

    Returns:
        List[dbc.ListGroupItem]: A list of search results.
    """
    global REPO_SINGLETON
    # `segments` a dataframe with the following columns:
    # id - segment id
    # transcription_id - id for the transcription run
    # segment - the text for the segment
    # temperature - a setting from the model
    # time_start - time the segment starts in seconds from the beginning of the video
    # time_end - time the segment ends in seconds from the beginning of the video
    # thumbnail - the thumbnail in a byte string
    # video_id - the video id in the data base
    segments = REPO_SINGLETON.query_text_segments(q)
    # IF the query doesn't return any results show some default text defined at the tops
    if len(segments) > 0:
        convert_f = functools.partial(convert_search_result_to_button, q)
        segment_rows = list(segments.apply(convert_f, axis=1))
    else:
        segment_rows = [dbc.ListGroupItem("No text found matching input.")]

    return segment_rows


@dash.callback(
    [
        dash.Output("video-thumbnails", "items"),
        dash.Output("video-thumbnails", "active_index"),
    ],
    dash.Input(
        {"type": "search-result", "video_id": dash.ALL, "offset": dash.ALL},
        "n_clicks_timestamp",
    ),
    dash.State(
        {"type": "search-result", "video_id": dash.ALL, "offset": dash.ALL}, "id"
    ),
    prevent_initial_call=True,
)
def search_result_clicked_update_thumbnails(
    n_clicks_timestamps: List[Union[None, int]],
    ids: List[dict],
) -> List[dbc.ListGroupItem]:
    """Callback for when a search result is clicked, updates thumbnails.

    Args:
        n_clicks_timestamps (List[Union[None, int]]): List of timestamps for when
                                                      each search result was clicked.
        ids (List[dict]): List of ids for each search result.

    Returns:
        List[dbc.ListGroupItem]: A list of thumbnails.
    """
    # convert None to 0
    n_clicks_timestamps = list(map(lambda idx: idx if idx else 0, n_clicks_timestamps))

    if not any(n_clicks_timestamps):
        return (
            [{"key": "1", "src": "assets/img/carousel_placeholder-click_result.svg"}],
            0,
        )

    # the most recently clicked index will have the largest timestamp
    index = n_clicks_timestamps.index(max(n_clicks_timestamps))
    selected_segment = ids[index]
    video_id = selected_segment["video_id"]

    global REPO_SINGLETON
    video_path = REPO_SINGLETON.query_video_path_by_id(video_id)
    offset = ids[index]["offset"]

    # this needs to be checked properly
    length = vp.get_video_length(video_path)

    start_time = max(offset - 5, 0)
    end_time = min(offset + 5, length)

    # TODO: check for max time
    frame_seconds = np.linspace(start_time, end_time, 11)
    thmb_f = functools.partial(vp.get_thumbnail, video_path, 0)

    import time

    start = time.time()
    thumbnails = list(
        map(
            lambda buffer: "data:image/png;base64,"
            + base64.b64encode(buffer).decode("ASCII"),
            map(thmb_f, frame_seconds),
        )
    )
    print(f"Time to get thumbnails: {time.time() - start}")

    idxs = list(range(1, len(thumbnails) + 1))
    items = [{"key": str(i), "src": t} for i, t in zip(idxs, thumbnails)]

    center_idx = 6
    return items, center_idx


@dash.callback(
    dash.Output("map-container", "children"),
    dash.Input(
        {"type": "search-result", "video_id": dash.ALL, "offset": dash.ALL},
        "n_clicks_timestamp",
    ),
    dash.State(
        {"type": "search-result", "video_id": dash.ALL, "offset": dash.ALL}, "id"
    ),
    prevent_initial_call=True,
)
def search_result_clicked_update_map(
    n_clicks_timestamps: List[Union[None, int]],
    ids: List[dict],
) -> List[dl.Map]:
    """Callback for when a search result is clicked, updates map.

    Args:
        n_clicks_timestamps (List[Union[None, int]]): List of timestamps for when
                                                      each search result was clicked.
        ids (List[dict]): List of ids for each search result.

    Returns:
        List[dl.Map]: A list containing a map.
    """
    # convert None to 0
    n_clicks_timestamps = list(map(lambda idx: idx if idx else 0, n_clicks_timestamps))

    if not any(n_clicks_timestamps):
        return DEFAULT_MAP

    # the most recently clicked index will have the largest timestamp
    index = n_clicks_timestamps.index(max(n_clicks_timestamps))
    selected_segment = ids[index]
    video_id = selected_segment["video_id"]

    # gps_coords a dataframe with the following columns:
    # lat - latitude coord
    # lon - longitude coord
    # time - time in seconds of GPS location in video
    global REPO_SINGLETON
    gps_coords = REPO_SINGLETON.query_gps_coords(
        video_id, selected_segment["offset"] - 5, selected_segment["offset"] + 5
    )

    if len(gps_coords) > 0:
        # adapted: https://www.dash-leaflet.com/docs/geojson_tutorial#a-scatter-plot

        gps_coords["tooltip"] = gps_coords["time"].apply(lambda t: f"{t:+} secs")

        geojson = dlx.dicts_to_geojson(
            gps_coords.to_dict("records"), lon="longitude", lat="latitude"
        )
        geobuf = dlx.geojson_to_geobuf(geojson)

        colorscale = ["red", "yellow", "green", "blue", "purple"]  # rainbow
        color_prop = "time"
        colorbar = dl.Colorbar(
            colorscale=colorscale,
            width=20,
            height=150,
            min=gps_coords["time"].min(),
            max=gps_coords["time"].max(),
            unit="sec",
        )

        geojson = dl.GeoJSON(
            data=geobuf,
            id="geojson",
            format="geobuf",
            zoomToBounds=True,  # when true, zooms to bounds when data changes
            pointToLayer=POINT_TO_LAYER,  # how to draw points
            # superClusterOptions=dict(radius=50),   # adjust cluster size
            hideout=dict(
                colorProp=color_prop,
                circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                min=gps_coords["time"].min(),
                max=gps_coords["time"].max(),
                colorscale=colorscale,
            ),
        )

        return [
            dl.Map(
                children=[dl.TileLayer(), geojson, colorbar],
                style={"width": "100%", "aspectRatio": "1 / 1"},
            )
        ]
    else:
        return [
            dbc.Card(
                [
                    dbc.CardImg(
                        src="./assets/img/map_question.jpeg",
                        top=True,
                    ),
                    dbc.CardImgOverlay(
                        dbc.CardBody(
                            [
                                dash.html.H4("GPS Missing", className="card-title"),
                            ],
                        ),
                    ),
                ]
            ),
        ]


def highlight(text: str, search: str) -> str:
    """Highlights `search` in `text` with a badge.

    Args:
        text (str): Text to highlight.
        search (str): Text to search for.

    Returns:
        str: Text with `search` highlighted.
    """
    els = re.split(f"(\\b{search})", text, flags=re.IGNORECASE)

    styled_elements = []
    for e in els:
        if e.lower() == search.lower():
            styled_elements.append(dbc.Badge(e, color="primary"))
        else:
            styled_elements.append(dash.html.Span(e, style={"color": "black"}))
            # styled_elements.append(r'<span style="color: black">{}</span>'.format(e))

    return styled_elements


#     print(els)
#     for i in range(1, len(els), 2):
#         els[i] = dbc.Badge(els[i], color="primary")

#     return els

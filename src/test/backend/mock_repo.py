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

"""Mock Repository class for saving and retreiving data from the database."""


from typing import Any, Optional, Union

import pandas as pd


class MockRepositoryForUI:
    """This class provides an interface to the database."""

    def __init__(
        self,
        video_dataframe: pd.DataFrame = None,
        text_dataframe: pd.DataFrame = None,
        gps_dataframe: pd.DataFrame = None,
    ) -> "MockRepositoryForUI":
        """Creates a Repository object.

        Args:
            db_auth_path (Optional[str], optional): Path to a json file
                                                    containing database
                                                    authentication info.
                                                    Defaults to None.
            db_auth (Optional[Dict[str, Union[str, int]]], optional): auth JSON
            DROP_AND_CREATE_DANGER (Optional[bool], optional): Whether to drop
                                                               and recreate the
                                                               database.

        Raises:
            ValueError: If both `db_auth_path` and `db_auth` are given or if
                        neither are given.

        Returns:
            Repository: The Repository object.
        """
        self.vid_df = video_dataframe if video_dataframe else self.default_video_df()
        self.txt_df = text_dataframe if text_dataframe else self.default_text_df()
        self.gps_df = gps_dataframe if gps_dataframe else self.default_gps_df()

    def get_video(
        self,
        video_id: Optional[int] = None,
        checksum: Optional[str] = None,
    ) -> Union[Any, None]:
        """Gets a video row from the database.

        Args:
            video_id (Optional[int], optional): The video id.
            checksum (Optional[str], optional): The video checksum.

        Raises:
            ValueError: If both `video_id` and `checksum` are given or if
                        neither are given.

        Returns:
            Union[Any, None]: The video row or None if it doesn't exist.
        """
        return self.df.loc[self.df["video_id"] == video_id, :].iloc[0]

    def query_text_segments(self, query: str) -> pd.DataFrame:
        """Queries the text segments table.

        Args:
            query (str): The query to execute.

        Returns:
            pd.DataFrame: The results of the query.
        """
        mask = self.txt_df["text"].str.contains(query, case=False)
        return self.txt_df.loc[mask, :]

    def query_video_path_by_id(self, video_id: int) -> str:
        """Queries the video path by id.

        Args:
            video_id (int): The video id.

        Returns:
            str: The video path if found, otherwise an empty string
        """
        return self.vid_df.loc[self.vid_df["id"] == video_id, "filename"].iloc[0]

    def query_gps_coords(
        self, video_id: int, time_start: float, time_end: float
    ) -> pd.DataFrame:
        """Queries the gps coords table.

        Args:
            video_id (int): The video id.
            time_start (float): The start time.
            time_end (float): The end time.

        Returns:
            pd.DataFrame: The results of the query.
        """
        mask = (
            (self.gps_df["video_id"] == video_id)
            & (self.gps_df["time"] >= time_start)
            & (self.gps_df["time"] <= time_end)
        )

        return self.gps_df.loc[mask, :]

    def default_video_df(self) -> pd.DataFrame:
        """Returns a default video dataframe."""
        url1 = "https://archive.org/download/MakingBo1947/MakingBo1947.mp4"
        url2 = "https://archive.org/download/DuckandC1951/DuckandC1951.ia.mp4"
        return pd.DataFrame(
            [
                dict(
                    id=1,
                    filename=url1,
                    checksum="1234",
                ),
                dict(
                    id=2,
                    filename=url2,
                    checksum="5678",
                ),
            ]
        )

    def default_text_df(self) -> pd.DataFrame:
        """Returns a default text dataframe."""
        return pd.DataFrame(
            [
                dict(
                    id=1,
                    video_id=1,
                    time_start=100,
                    time_end=110,
                    thumbnail="",
                    text="This video is about books.",
                ),
                dict(
                    id=2,
                    video_id=1,
                    time_start=200,
                    time_end=210,
                    thumbnail="",
                    text="This part is also about books.",
                ),
                dict(
                    id=3,
                    video_id=2,
                    time_start=100,
                    time_end=110,
                    thumbnail="",
                    text="This video is about bombs.",
                ),
                dict(
                    id=4,
                    video_id=2,
                    time_start=200,
                    time_end=210,
                    thumbnail="",
                    text="This part is also about bombs.",
                ),
            ]
        )

    def default_gps_df(self) -> pd.DataFrame:
        """Returns a default gps dataframe."""
        return pd.DataFrame(
            [
                dict(
                    lat=48.858592314273785,
                    lon=2.2932544065215748,
                    time=102,
                    video_id=1,
                ),
                dict(
                    lat=48.858128333256964,
                    lon=2.2939913625693746,
                    time=104,
                    video_id=1,
                ),
                dict(
                    lat=48.857599389651696,
                    lon=2.294844680098407,
                    time=106,
                    video_id=1,
                ),
                dict(
                    lat=52.4594335626035,
                    lon=4.552019317265759,
                    time=102,
                    video_id=2,
                ),
                dict(
                    lat=52.450477438977614,
                    lon=4.555406513604146,
                    time=104,
                    video_id=2,
                ),
                dict(
                    lat=52.44099455767272,
                    lon=4.557301047149346,
                    time=106,
                    video_id=2,
                ),
            ]
        )

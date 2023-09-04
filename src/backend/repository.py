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

"""Repository class for saving and retreiving data from the database."""


import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import sqlalchemy as sqla
import sqlalchemy.ext.automap as automap
import sqlalchemy.orm as orm


class Repository:
    """This class provides an interface to the database."""

    def __init__(
        self,
        db_auth_path: Optional[str] = None,
        db_auth: Optional[Dict[str, Union[str, int]]] = None,
        DROP_AND_CREATE_DANGER: Optional[bool] = False,
    ) -> "Repository":
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
        if (db_auth_path is None and db_auth is None) or (
            db_auth_path is not None and db_auth is not None
        ):
            raise ValueError("Must provide either db_auth_path or db_auth.")

        if db_auth_path is not None:
            with open(db_auth_path, "r") as f:
                db_auth = json.load(f)

        self.auth = db_auth
        self.engine = self.__create_engine()

        self.here = os.path.dirname(os.path.abspath(__file__))

        if DROP_AND_CREATE_DANGER:
            self.drop_and_create(I_AM_SURE_I_WANT_TO_DO_THIS=True)

        self.base = automap.automap_base()
        self.base.prepare(self.engine, reflect=True)
        self._session = None

        self.Video = self.base.classes.video
        self.Audio = self.base.classes.audio
        self.Transcription = self.base.classes.transcription
        self.TextSegment = self.base.classes.text_segment
        self.WordSegment = self.base.classes.word_segment
        self.GPS = self.base.classes.gps

    @property
    def session(self) -> orm.Session:
        """Returns a session object.

        Returns:
            orm.Session: The session object.
        """
        if self._session is None:
            self._session = orm.Session(self.engine)
        return self._session

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
        both_none = video_id is None and checksum is None
        both_given = video_id is not None and checksum is not None
        if both_given or both_none:
            raise ValueError("Must specify `video_id` OR `checksum`")

        if video_id:
            stmt = sqla.select(self.Video).where(self.Video.id == video_id)

        if checksum:
            stmt = sqla.select(self.Video).where(self.Video.checksum == checksum)

        return self.session.scalars(stmt).one_or_none()

    def get_audio(
        self,
        audio_id: Optional[int] = None,
        checksum: Optional[str] = None,
    ) -> Union[Any, None]:
        """Gets an audio row from the database.

        Args:
            audio_id (Optional[int], optional): The audio id.
            checksum (Optional[str], optional): The audio checksum.

        Raises:
            ValueError: If both `audio_id` and `checksum` are given or if
                        neither are given.

        Returns:
            Union[Any, None]: The audio row or None if it doesn't exist.
        """
        both_none = audio_id is None and checksum is None
        both_given = audio_id is not None and checksum is not None
        if both_given or both_none:
            raise ValueError("Must specify `audio_id` OR `checksum`")

        if audio_id:
            stmt = sqla.select(self.Audio).where(self.Audio.id == audio_id)

        if checksum:
            stmt = sqla.select(self.Audio).where(self.Audio.checksum == checksum)

        return self.session.scalars(stmt).one_or_none()

    def save_data(
        self,
        video_kwargs: Dict[str, Any],
        audio_kwargs: Dict[str, Any],
        transcription_kwargs: Dict[str, Any],
        text_segments_dicts: List[Dict[str, Any]],
        gps_kwargs: List[Dict[str, Any]],
        logger: Optional[logging.Logger] = logging.getLogger(__name__),
    ) -> None:
        """Saves data to the database.

        Args:
            video_kwargs (Dict[str, Any]): kwargs for video rows.
            audio_kwargs (Dict[str, Any]): kwargs for audio rows.
            transcription_kwargs (Dict[str, Any]): kwargs for transcript rows.
            text_segments_dicts (List[Dict[str, Any]]): kwargs for text
                                                        segment rows.
            gps_kwargs (List[Dict[str, Any]]): kwargs for gps rows.
            logger (Optional[logging.Logger], optional): Logger object.

        Returns:
            None
        """
        if (video := self.get_video(checksum=video_kwargs["checksum"])) is None:
            logger.info("Video doesn't exist in database")
            video = self.Video(**video_kwargs)
        else:
            logger.info(f"Video exists in database id = {video.id}")

        if (audio := self.get_audio(checksum=audio_kwargs["checksum"])) is None:
            logger.info("Audio doesn't exist in database")
            audio = self.Audio(video=video, **audio_kwargs)
        else:
            logger.info(f"Audio exists in database id = {audio.id}")

        transcription = self.Transcription(audio=audio, **transcription_kwargs)

        text_segments = []
        word_segments = []
        for ts in text_segments_dicts:
            text_segment = self.TextSegment(
                transcription=transcription,
                segment=ts["text"],
                start_time=ts["start"],
                end_time=ts["end"],
                no_speech_prob=ts["no_speech_prob"],
                thumbnail=ts["thumbnail"],
            )

            for word in ts["words"]:
                word_segment = self.WordSegment(
                    text_segment=text_segment,
                    word=word["word"],
                    start_time=word["start"],
                    end_time=word["end"],
                    probability=word["probability"],
                )
                word_segments.append(word_segment)
            text_segments.append(text_segment)

        gps_coords = list(
            map(lambda kwargs: self.GPS(video=video, **kwargs), gps_kwargs)
        )

        logger.info("Saving items to session")
        for item in (
            [video, audio, transcription] + text_segments + word_segments + gps_coords
        ):
            self.session.add(item)

        logger.info("Committing")
        self.session.commit()
        logger.info("Completed")

    def drop_and_create(self, I_AM_SURE_I_WANT_TO_DO_THIS: bool = False) -> None:
        """Drop all tables and recreate them from the schema file.

        Args:
            I_AM_SURE_I_WANT_TO_DO_THIS (bool, optional): Defaults to False.

        Returns:
            None
        """
        # this boolean isn't really necessary, the same check happens in the
        # sql file, but it's a good reminder that this is a dangerous operation
        if I_AM_SURE_I_WANT_TO_DO_THIS:
            self.execute_update(
                self.get_sql("DDL.pysql").format(danger=I_AM_SURE_I_WANT_TO_DO_THIS)
            )

    def execute_query(self, sql: str) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas DataFrame.

        Args:
            sql (str): The query to execute.

        Returns:
            pd.DataFrame: The results of the query.
        """
        if isinstance(sql, str):
            sql = sqla.text(sql)
        with self.engine.connect() as conn:
            return pd.read_sql(sql, conn)

    def execute_update(self, statement: str) -> None:
        """Executes an update statement.

        Args:
            statement (str): The statement to execute.

        Returns:
            None
        """
        if isinstance(statement, str):
            statement = sqla.text(statement)
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(statement)
                trans.commit()
            except Exception:
                trans.rollback()
                raise
        return result

    def __create_engine(self):
        return sqla.create_engine(
            f"mssql+pymssql://{self.auth['user']}:"
            f"{self.auth['pwd']}@{self.auth['host']}:1433/"
            f"{self.auth['database']}?charset=utf8"
        )

    def get_sql(self, sql_file: str) -> str:
        """Gets the text of a sql file.

        Args:
            sql_file (str): The name of the sql file to get.

        Returns:
            str: The text of the sql file.
        """
        with open(os.path.join(self.here, "sql", sql_file), "r") as f:
            return f.read()

    def query_text_segments(self, query: str) -> pd.DataFrame:
        """Queries the text segments table.

        Args:
            query (str): The query to execute.

        Returns:
            pd.DataFrame: The results of the query.
        """
        return self.execute_query(
            self.get_sql("query_text_segments.pysql").format(query=query)
        )

    def query_video_path_by_id(self, video_id: int) -> str:
        """Queries the video path by id.

        Args:
            video_id (int): The video id.

        Returns:
            str: The video path if found, otherwise an empty string
        """
        if (val := self.get_video(id=video_id)) is not None:
            return val.filename
        else:
            return ""

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
        return self.execute_query(
            self.get_sql("query_gps_coords.pysql").format(
                video_id=video_id, time_start=time_start, time_end=time_end
            )
        )

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

import json
from typing import Any, Optional, Union

import pandas as pd
import sqlalchemy as sqla

import job_config as jc


class Repository:
    def __init__(
        self,
        db_auth_path: Optional[str] = None,
        db_auth: Optional[dict[str, Union[str, int]]] = None,
    ) -> "Repository":

        if (db_auth_path is None and db_auth is None) or (
            db_auth_path is not None and db_auth is not None
        ):
            raise ValueError("Must provide either db_auth_path or db_auth.")

        if db_auth_path is not None:
            with open(db_auth_path, "r") as f:
                db_auth = json.load(f)

        self.auth = db_auth
        self.engine = self.__create_engine()
        self.base = sqla.orm.automap_base()
        self.base.prepare(self.engine, reflect=True)
        self._session = None

        self.Video = self.base.classes.video
        self.Audio = self.base.classes.audio
        self.Transcription = self.base.classes.transcription
        self.WordSegment = self.base.classes.word_segment
        self.GPS = self.base.classes.gps

    @property
    def session(self):
        if self._session is None:
            self._session = sqla.orm.Session(self.engine)
        return self._session

    def save_data(
        self,
        video_kwwargs: dict[str, Any],
        audio_kwwargs: dict[str, Any],
        transcription_kwwargs: dict[str, Any],
        word_segment_kwwargs: dict[str, Any],
        gps_kwwargs: dict[str, Any],
    ) -> None:

        video = self.Video(**video_kwwargs)
        audio = self.Audio(video=video, **audio_kwwargs)
        transcription = self.Transcription(audio=audio, **transcription_kwwargs)
        word_segments = list(
            map(
                lambda kwwargs: self.WordSegment(
                    transcription=transcription, **kwwargs
                ),
                word_segment_kwwargs,
            )
        )
        gps_coords = list(
            map(lambda kwwargs: self.GPS(video=video, **kwwargs), gps_kwwargs)
        )

        for item in [video, audio, transcription] + word_segments + gps_coords:
            self.session.add(item)

        self.session.commit()

    def drop_and_create(self, I_AM_SURE_I_WANT_TO_DO_THIS: bool = False) -> None:
        if I_AM_SURE_I_WANT_TO_DO_THIS:
            with open("sql/DDL.sql", "r") as f:
                sql = f.read().format(danger=1)
            self.execute_update(sql)

    def execute_query(self, sql: str) -> pd.DataFrame:
        if type(sql) == str:
            sql = sqla.text(sql)
        with self.engine.connect() as conn:
            return pd.read_sql(sql, conn)

    def execute_update(self, statement: str) -> None:
        if type(statement) == str:
            statement = sqla.text(statement)
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                result = conn.execute(statement)
                trans.commit()
            except:
                trans.rollback()
                raise
        return result

    def __create_engine(self):
        return sqla.create_engine(
            f"mssql+pymssql://{self.auth['user']}:{self.auth['pwd']}@{self.auth['host']}:1433/{self.auth['database']}?charset=utf8"
        )

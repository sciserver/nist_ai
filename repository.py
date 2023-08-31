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
import logging
from typing import Any, Optional, Union

import pandas as pd
import sqlalchemy as sqla
import sqlalchemy.orm as orm
import sqlalchemy.ext.automap as automap

import job_config as jc


class Repository:
    def __init__(
        self,
        db_auth_path: Optional[str] = None,
        db_auth: Optional[dict[str, Union[str, int]]] = None,
        DROP_AND_CREATE_DANGER: Optional[bool] = False,
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
    def session(self):
        if self._session is None:
            self._session = orm.Session(self.engine)
        return self._session

    
    def get_video(self, 
        video_id:Optional[int] = None, 
        checksum:Optional[str] = None,
     ) -> Union[Any, None]:
        
        both_none = video_id is None and checksum is None
        both_given = video_id is not None and checksum is not None
        if both_given or both_none:
            raise ValueError("Must specify `video_id` OR `checksum`")
            
        if video_id:
            stmt = sqla.select(self.Video).where(self.Video.id==video_id)
        
        if checksum:
            stmt = sqla.select(self.Video).where(self.Video.checksum==checksum)
        
        return self.session.scalars(stmt).one_or_none()
        
    def get_audio(self, 
        audio_id:Optional[int] = None, 
        checksum:Optional[str] = None,
     ) -> Union[Any, None]:
        
        both_none = audio_id is None and checksum is None
        both_given = audio_id is not None and checksum is not None
        if both_given or both_none:
            raise ValueError("Must specify `audio_id` OR `checksum`")
            
        if audio_id:
            stmt = sqla.select(self.Audio).where(self.Audio.id==audio_id)
        
        if checksum:
            stmt = sqla.select(self.Audio).where(self.Audio.checksum==checksum)
        
        return self.session.scalars(stmt).one_or_none()
        
    
    def save_data(
        self,
        video_kwargs: dict[str, Any],
        audio_kwargs: dict[str, Any],
        transcription_kwargs: dict[str, Any],
        text_segments_dicts: list[dict[str, Any]],
        gps_kwargs: list[dict[str, Any]],
        logger: Optional[logging.Logger] = logging.getLogger(__name__),
    ) -> None:
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
        for item in [video, audio, transcription] + text_segments + word_segments + gps_coords:
            self.session.add(item)

        logger.info("Committing")
        self.session.commit()
        logger.info("Completed")

    def drop_and_create(self, I_AM_SURE_I_WANT_TO_DO_THIS: bool = False) -> None:
        if I_AM_SURE_I_WANT_TO_DO_THIS:
            with open("sql/DDL.pysql", "r") as f:
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

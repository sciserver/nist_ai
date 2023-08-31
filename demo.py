import functools
import logging
import os

import end_to_end
import job_config as jc
import repository as repo


logging.basicConfig(
    filename="demo_log.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


def run():
    ffmpeg_binaries = '/home/idies/workspace/nist_ai/extras/ffmpeg-6.0-amd64-static'
    assert os.path.exists(ffmpeg_binaries)
    os.environ["PATH"] =  f"{ffmpeg_binaries}:" + os.environ["PATH"]
    
    
    base_path = "/home/idies/workspace/nist_ai/data/video/Tanya"
    with_base = functools.partial(os.path.join, base_path)

    video_path = with_base("Log-20230726-142137 strip mall.mp4")
    audio_path = with_base("Log-20230726-142137 strip mall.mp3")
    gps_path = with_base("Log-20230726-142137 strip mall - Interpolated.csv")

    repository = repo.Repository(
        db_auth_path="nist-ai.json",
        DROP_AND_CREATE_DANGER=True,
    )

    
    job_config = jc.EndToEndConfig(
        transcription_config=jc.WhisperConfig(),
        source_video_type=jc.VideoType.TRACK_ADDICT,
        thumbnail_width=300,
    )

    logger = logging.getLogger("end-to-end-demo")

    end_to_end.process_video(
        video_path=video_path,
        audio_path=audio_path,
        gps_path=gps_path,
        repository=repository,
        job_config=job_config,
        logger=logger,
    )


if __name__ == "__main__":
    run()

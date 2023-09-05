# nist_ai

### Requires



### Run Pipeline

```
python -m pip install -U openai-whisper dash-bootstrap-components dash-extensions dash-leaflet
mamba install -y pymssql
```

Edit `demo.py` to convert the desired video.

Run `nvidia-smi` to see which GPU to use

Run `CUDA_VISIBLE_DEVICES=[GPU_ID] python demo.py`



### Run UI

You need a symlink to the videos directory in the assets folder called `videos`
If you're in `assets`:

`ln -s ../../../data/videos ./videos`


`videos -> ../../../data/videos`


If you get an error about protbuf then try running:

```
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python demo.py
```

Want to make changes?

```
mamba install -y black isort flake8 flake8-docstrings
```

Before committing and pushing:

```
black .
isort .
flake8 .
```
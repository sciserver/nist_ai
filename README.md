# nist_ai

### Requires

```
python -m pip install -U openai-whisper dash-bootstrap-components dash-extensions dash-leaflet
mamba install -y pymssql
```

Edit `demo.py` to convert the desired video.

Run `nvidia-smi` to see which GPU to use

Run `CUDA_VISIBLE_DEVICES=[GPU_ID] python demo.py`

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
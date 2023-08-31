# nist_ai

### Requires

```
python -m pip install -U openai-whisper
mamba install -y pymssql
```

Edit `demo.py` to convert the desired video.

Run `nvidia-smi` to see which GPU to use

Run `CUDA_VISIBLE_DEVICES=[GPU_ID] python demo.py`



Want to make changes?

```
mamba install -y black isort
```

Before committing and pushing:

```
black .
isort .
```
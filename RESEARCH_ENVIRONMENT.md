# Research Environment

To support quantitative research and notebook-driven exploration we ship a JupyterLab workspace.

## Starting Jupyter

```
docker-compose -f docker-compose.dev.yml up -d jupyter
```

- URL: http://localhost:8888
- Token: `devtoken` (change via `JUPYTER_TOKEN` env var in `docker-compose.dev.yml`).
- Workspace files live in `research/notebooks/` and are mounted into the container.

## Notebook quickstart

Use the `Quickstart.ipynb` notebook as a template for calling the local API from pandas.

## Tips
- Keep research notebooks under version control for reproducibility.
- Promote stable logic into services or libraries within the backend once validated.

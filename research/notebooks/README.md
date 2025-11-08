# Research Notebook Workspace

This directory is mounted into the JupyterLab container provided by the `jupyter` service in `docker-compose.dev.yml`.

## Quick start

1. Start the stack (including Jupyter):
   ```bash
   docker-compose -f docker-compose.dev.yml up -d jupyter
   ```
2. Open http://localhost:8888 in your browser and use the token `devtoken` (change via env vars in compose).
3. Create notebooks inside this folder. They will be persisted on your host machine for version control.

## Suggested workflow

- Use the REST API to pull strategies/backtests into pandas dataframes.
- Leverage the `research` directory for experiments, feature engineering, or modeling before promoting code into services.
- Commit notebooks or export analysis summaries for reproducibility.

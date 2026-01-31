# vibe-diff-api 🔍

Fast text and JSON comparison API built with FastAPI.

## Endpoints

### `POST /diff`
Compare two texts and get unified diff output.

```json
{
  "text1": "hello world",
  "text2": "hello there world",
  "context_lines": 3
}
```

### `POST /json-diff`
Compare two JSON objects structurally.

```json
{
  "json1": {"name": "Alice", "age": 30},
  "json2": {"name": "Alice", "age": 31, "city": "NYC"}
}
```

### `POST /similarity`
Calculate text similarity percentage.

```json
{
  "text1": "the quick brown fox",
  "text2": "the quick red fox"
}
```

## Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Docs

Visit `/docs` for interactive Swagger UI.

## Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---
Built with ⚡ FastAPI

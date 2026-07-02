# 5-Minute Run Guide

This project is designed to run with one Docker Compose command after the API
key is configured.

## Prerequisites

- Docker Desktop or Docker Engine with Compose v2.
- Docker Desktop must be running before executing the Compose command.
- A DeepSeek API key.

## Steps

1. Create the environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set:

   ```env
   DEEPSEEK_API_KEY=your_deepseek_key
   ```

3. Run the agent:

   ```bash
   docker compose run --rm agent "Generate today's briefing for the Pilbara lithium project"
   ```

Expected output: a Markdown briefing with news summary, resource data, lithium
price trend, risk notes, and source links.

Chinese prompts are also supported:

```powershell
docker compose run --rm agent "给我生成一份关于 Pilbara 锂矿的今日简报"
```

## MCP Inspector / Host Config

After installing the project locally with `pip install -e .`, copy
`mcp-config.json` into a Claude Desktop / Cursor MCP configuration location.
The servers use stdio and expose the required tools from the interview prompt.

## Troubleshooting

- Missing key: copy `.env.example` to `.env` and set `DEEPSEEK_API_KEY`.
- Slow first run: Docker must build the image once. Re-runs use the cache.
- Base image pull fails: if Docker reports that `python:3.12-slim` cannot be
  pulled and the URL includes a registry mirror such as `docker.m.daocloud.io`
  with `401 Unauthorized`, remove or replace the failing mirror in Docker
  Desktop Settings -> Docker Engine, apply the change, restart Docker, and
  retry:

  ```bash
  docker pull python:3.12-slim
  docker compose run --rm agent "Generate today's briefing for the Pilbara lithium project"
  ```

- Network blocked: fixture MCP data still loads, but DeepSeek generation needs
  outbound HTTPS access to `https://api.deepseek.com`.

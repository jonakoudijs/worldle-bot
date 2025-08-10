[![Build Status](https://img.shields.io/github/actions/workflow/status/jonakoudijs/worldle-bot/deploy.yml)](https://github.com/jonakoudijs/worldle-bot/actions)
[![Image Size](https://img.shields.io/docker/image-size/jonakoudijs/worldle-bot/latest.svg)](https://hub.docker.com/r/jonakoudijs/worldle-bot)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# Worldle Bot

A Python bot that automatically fetches the daily Worldle country shape and uploads it to Slack.

## Features

- Automatically fetches the daily Worldle country shape
- Converts SVG to PNG with white background
- Uploads to Slack channel
- Runs in Docker container

## GitHub Actions CI/CD

This project includes automated CI/CD pipeline that:

1. **Lints the code** using:
   - Black (code formatter)
   - isort (import sorter)
   - flake8 (linter)
   - mypy (type checker)

2. **Builds and pushes Docker images** to:
   - Docker Hub
   - GitHub Container Registry (GHCR)

The pipeline runs on:
- Pull requests to `main` branch (linting only)
- Pushes to `main` branch (linting + build + push)

## Required GitHub Secrets

To enable Docker image pushing, you need to set up the following secrets in your GitHub repository:

### For Docker Hub:
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)

### For GitHub Container Registry:
- No additional secrets needed - uses the built-in `GITHUB_TOKEN`

## Setting up Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Give it a name (e.g., "GitHub Actions")
5. Copy the token and add it as `DOCKERHUB_TOKEN` in your GitHub secrets

## Usage

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

### Docker

```bash
# Build the image
docker build -t worldle-bot .

# Run the container
docker run -e SLACK_BOT_TOKEN=your_token -e SLACK_CHANNEL=your_channel worldle-bot
```

### Environment Variables

- `SLACK_BOT_TOKEN`: Your Slack bot token
- `SLACK_CHANNEL`: The Slack channel ID to post to
- `OUTPUT_DIR`: Directory to save images (default: `/app/output`)

## Image Tags

The CI/CD pipeline creates the following image tags:

- `latest`: Latest build from main branch
- `main`: Latest build from main branch
- `sha-{commit}`: Specific commit SHA
- Semantic version tags (when using git tags)

### Docker Hub
```
docker.io/{username}/worldle-bot:{tag}
```

### GitHub Container Registry
```
ghcr.io/{username}/worldle-bot:{tag}
```

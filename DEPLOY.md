# Deploying the hosted demo

Any Docker host works. Two zero-config paths:

## Render (easiest)

1. Push this repo to GitHub (done if you're reading this there).
2. [dashboard.render.com](https://dashboard.render.com) → New → Blueprint →
   select the repo. `render.yaml` does the rest.
3. Set `ANTHROPIC_API_KEY` in the service's Environment tab (leave unset for
   free mock mode).
4. Your demo is live at `https://quorum-XXXX.onrender.com`.

Free-tier note: the instance sleeps after idle periods and cold-starts in ~30s.
Fine for a demo; upgrade or move before a launch spike.

## Fly.io

```bash
fly launch --copy-config --no-deploy   # uses fly.toml
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly deploy
```

## Launch-day traffic (read before posting to HN)

A front-page Show HN can bring 5k–30k visitors in 24h. Before launching:
- Move off free tier (Render Starter or a Fly machine with min_machines_running=1)
  so there's no cold start.
- Set a spend cap on your LLM API account; consider `QUORUM_BACKEND=mock` as an
  emergency valve — the demo stays interactive even if you kill real inference.
- `/stats` gives you the councils-run counter for your launch-day tweet updates.

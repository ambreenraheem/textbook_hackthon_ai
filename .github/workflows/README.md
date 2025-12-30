# Workflows Directory

This directory is intentionally empty.

## Deployment Strategy

This project uses **Vercel** for deployment (both frontend and backend).

Vercel handles all deployments automatically through its GitHub integration:
- No GitHub Actions workflows needed
- Deployments triggered on push to `main` branch
- Configuration managed in Vercel dashboard

## Deployment Files

- **Backend**: `backend/vercel.json` + `backend/api/index.py`
- **Frontend**: Auto-detected by Vercel (Docusaurus)

## Deployment Guide

See `docs/deployment-vercel.md` for complete deployment instructions.

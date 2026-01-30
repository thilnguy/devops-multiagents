# Local Kubernetes Setup Guide

This guide helps you set up a local Kubernetes cluster for development and testing.

## Option 1: Docker Desktop (Recommended for macOS)
The easiest way if you have Docker Desktop installed:

1. Open **Docker Desktop** → **Settings** → **Kubernetes**
2. Check **Enable Kubernetes**
3. Click **Apply & Restart**
4. Wait 2-3 minutes for cluster to start
5. Verify: `kubectl get nodes`

## Option 2: kind (Kubernetes in Docker)
Lightweight clusters using Docker containers:

```bash
# Install kind
brew install kind

# Create cluster
kind create cluster --name devops-multiagents

# Verify
kubectl cluster-info --context kind-devops-multiagents
```

## Option 3: Minikube
Full-featured local K8s:

```bash
# Start with Docker driver (avoids VM issues)
minikube start --driver=docker

# Verify
minikube status
kubectl get nodes
```

## Verify K8s Manifests
Once your cluster is running:
```bash
cd /path/to/devops_multiagents
kubectl apply --dry-run=client -f infra/kubernetes/base/
```

Expected output:
```
deployment.apps/sample-api created (dry run)
service/sample-api created (dry run)
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Permission denied | Run with `sudo` or check Docker socket permissions |
| Minikube log error | Use `minikube delete && minikube start --driver=docker` |
| kubectl not connected | Run `kubectl config use-context docker-desktop` or `kind-devops-multiagents` |

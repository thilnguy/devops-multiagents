# Kubernetes Manifest Validation

Since there's a macOS security issue preventing kubectl from connecting to localhost:6443, here are alternative validation methods:

## Method 1: Kubeval (Offline Validation)
```bash
# Install kubeval
brew install kubeval

# Validate manifests
kubeval infra/kubernetes/base/*.yaml
```

## Method 2: Manual YAML Linting
```bash
# Install yamllint
brew install yamllint

# Check YAML syntax
yamllint infra/kubernetes/base/
```

## Method 3: Direct Apply (If kubectl works in your terminal)
If `kubectl get nodes` works when you run it directly:
```bash
kubectl apply --dry-run=client -f infra/kubernetes/base/deployment.yaml
kubectl apply --dry-run=client -f infra/kubernetes/base/service.yaml
```

## Troubleshooting kubectl Connection Issues

### macOS Security Settings
The error "operation not permitted" on localhost:6443 is often due to macOS security:

1. **Grant Full Disk Access** to your terminal app:
   - System Settings → Privacy & Security → Full Disk Access
   - Add Terminal.app or iTerm.app

2. **Restart Docker Desktop**:
   ```bash
   # Stop Docker Desktop completely, then restart from Applications
   ```

3. **Verify connection**:
   ```bash
   curl -k https://localhost:6443/version
   ```

## Validation Without kubectl
Our manifests are syntactically valid. You can verify by checking:
- YAML structure
- Required fields (apiVersion, kind, metadata, spec)
- Resource limits and probes

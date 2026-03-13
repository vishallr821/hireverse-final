# Docker Setup Guide for Secure Code Execution

## Why Docker?

Docker provides **isolated sandboxed environments** for running untrusted code:

✅ **Security**: Code runs in isolated containers, can't access host system
✅ **Resource Limits**: CPU and memory limits prevent resource exhaustion
✅ **Network Isolation**: No internet access from code execution
✅ **Clean Environment**: Each execution starts fresh
✅ **Multi-language Support**: Python and Java in separate containers

## Installation Steps

### Windows

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download Docker Desktop for Windows
   - Run the installer

2. **System Requirements**
   - Windows 10/11 64-bit (Pro, Enterprise, or Education)
   - WSL 2 enabled (installer will help with this)
   - Virtualization enabled in BIOS

3. **Install and Start**
   ```bash
   # After installation, start Docker Desktop
   # Look for Docker icon in system tray
   # Wait until it shows "Docker Desktop is running"
   ```

4. **Verify Installation**
   ```bash
   docker --version
   docker ps
   ```

### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (no sudo needed)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker ps
```

### macOS

1. Download Docker Desktop for Mac from docker.com
2. Install and start Docker Desktop
3. Verify: `docker --version`

## Pull Required Images

Once Docker is running, pull the execution images:

```bash
# Python image (lightweight)
docker pull python:3.11-slim

# Java image (lightweight)
docker pull openjdk:17-slim
```

These images are ~150MB each and only need to be downloaded once.

## Configuration

### Enable Docker in .env

```env
# hireverse-dsa/.env
DOCKER_ENABLED=true
```

### Test Docker Integration

```bash
cd d:\Final\hireverse-dsa

# Test Python execution
docker run --rm python:3.11-slim python -c "print('Hello from Docker')"

# Test Java execution
docker run --rm openjdk:17-slim java -version
```

## How It Works

### Security Features

1. **Network Isolation**
   ```python
   network_disabled=True  # No internet access
   ```

2. **Resource Limits**
   ```python
   mem_limit="256m"      # Max 256MB RAM
   cpu_quota=50000       # 50% of one CPU core
   ```

3. **Timeout Protection**
   ```python
   timeout = 5  # Max 5 seconds execution
   ```

4. **Isolated Filesystem**
   - Code runs in `/tmp` inside container
   - No access to host files
   - Container deleted after execution

### Execution Flow

```
User submits code
    ↓
Code encoded in base64
    ↓
Docker container created
    ↓
Code decoded and executed
    ↓
Output captured
    ↓
Container destroyed
    ↓
Results returned
```

## Fallback Mode (Without Docker)

If Docker is not available, the system falls back to subprocess execution:

⚠️ **Less Secure**: Code runs directly on host
⚠️ **Limited Isolation**: Uses Python/Java subprocess
✅ **Still Functional**: Tests will work but with reduced security

## Troubleshooting

### Issue: "Docker daemon not found"

**Solution:**
1. Start Docker Desktop
2. Wait for "Docker Desktop is running" message
3. Restart hireverse-dsa server

### Issue: "Permission denied"

**Windows:**
- Run Docker Desktop as Administrator
- Ensure WSL 2 is enabled

**Linux:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "Image not found"

**Solution:**
```bash
docker pull python:3.11-slim
docker pull openjdk:17-slim
```

### Issue: "Container timeout"

**Solution:**
- Increase timeout in `executor.py`:
```python
timeout = 10  # Increase from 5 to 10 seconds
```

### Issue: "Out of memory"

**Solution:**
- Increase memory limit:
```python
mem_limit="512m"  # Increase from 256m
```

## Performance Comparison

### With Docker (Recommended)
- **Security**: ⭐⭐⭐⭐⭐
- **Isolation**: ⭐⭐⭐⭐⭐
- **Speed**: ⭐⭐⭐⭐ (slight overhead)
- **Resource Control**: ⭐⭐⭐⭐⭐

### Without Docker (Fallback)
- **Security**: ⭐⭐
- **Isolation**: ⭐⭐
- **Speed**: ⭐⭐⭐⭐⭐
- **Resource Control**: ⭐⭐⭐

## Testing the Setup

### 1. Start Docker Desktop

Wait until you see "Docker Desktop is running"

### 2. Verify Images

```bash
docker images
```

Should show:
```
REPOSITORY          TAG          SIZE
python              3.11-slim    ~150MB
openjdk             17-slim      ~400MB
```

### 3. Test Execution

Start hireverse-dsa:
```bash
cd d:\Final\hireverse-dsa
uvicorn main:app --reload --port 8001
```

You should see:
```
INFO: Docker daemon found. Pulling execution images...
INFO: Docker images ready.
```

### 4. Submit Test Code

Go to http://localhost:8001/problems and submit:

**Python:**
```python
def solution(arr):
    return sum(arr)

print(solution([1, 2, 3]))
```

**Java:**
```java
public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello from Docker!");
    }
}
```

### 5. Check Logs

You should see Docker containers being created and destroyed:
```bash
docker ps -a  # Should be empty (containers auto-removed)
```

## Production Recommendations

### 1. Use Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  hireverse-dsa:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - DOCKER_ENABLED=true
```

### 2. Resource Limits

Adjust based on your server:
```python
# For powerful servers
mem_limit="512m"
cpu_quota=100000  # 1 full CPU core

# For shared hosting
mem_limit="128m"
cpu_quota=25000   # 25% of one core
```

### 3. Monitoring

Monitor Docker resource usage:
```bash
docker stats
```

### 4. Cleanup

Periodically clean up:
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f
```

## Security Best Practices

1. ✅ Always use Docker in production
2. ✅ Keep images updated
3. ✅ Set strict resource limits
4. ✅ Disable network access
5. ✅ Use read-only filesystems where possible
6. ✅ Monitor for suspicious activity
7. ✅ Log all code executions
8. ✅ Implement rate limiting

## Advanced Configuration

### Custom Docker Images

Create optimized images:

**Dockerfile.python**
```dockerfile
FROM python:3.11-slim
RUN pip install numpy pandas
WORKDIR /tmp
```

**Dockerfile.java**
```dockerfile
FROM openjdk:17-slim
WORKDIR /tmp
```

Build:
```bash
docker build -f Dockerfile.python -t hireverse-python .
docker build -f Dockerfile.java -t hireverse-java .
```

Update `executor.py`:
```python
image = "hireverse-python" if language == "python" else "hireverse-java"
```

## Quick Start Checklist

- [ ] Install Docker Desktop
- [ ] Start Docker Desktop
- [ ] Pull python:3.11-slim image
- [ ] Pull openjdk:17-slim image
- [ ] Set DOCKER_ENABLED=true in .env
- [ ] Restart hireverse-dsa server
- [ ] Test with sample code
- [ ] Verify containers are created/destroyed
- [ ] Check logs for "Docker images ready"

## Support

If Docker setup fails:
1. The system will automatically fall back to subprocess
2. Tests will still work but with reduced security
3. You'll see: "Docker not found — using subprocess fallback"

For production use, Docker is **strongly recommended** for security.

## Summary

**Current Status**: Fallback mode (subprocess)
**Recommended**: Docker mode (isolated containers)
**Action Required**: Install and start Docker Desktop

Once Docker is running, the system will automatically use it for secure code execution!

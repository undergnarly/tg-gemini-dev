# Security Guidelines

**Classification:** Internal  
**Last Updated:** Январь 2025  
**Owner:** Security Team

---

## 🔒 Security Principles

1. **Defense in Depth**: Множественные уровни защиты
2. **Least Privilege**: Минимальные необходимые права
3. **Zero Trust**: Не доверяй, всегда проверяй
4. **Security by Design**: Безопасность встроена, а не добавлена

---

## 🚨 Critical Security Controls

### 1. Sandbox Isolation

**Threat**: Arbitrary code execution from user input

**Controls**:
```yaml
# Docker runtime security
security_opt:
  - no-new-privileges:true
  - apparmor:docker-default
  - seccomp:seccomp-profile.json

# Resource limits
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 512M

# Network isolation
networks:
  sandbox:
    internal: true
    driver: bridge
```

**gVisor Configuration**:
```bash
# /etc/docker/daemon.json
{
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc",
      "runtimeArgs": [
        "--network=sandbox",
        "--platform=ptrace",
        "--file-access=exclusive"
      ]
    }
  }
}
```

### 2. Authentication & Authorization

**JWT Token Structure**:
```python
{
  "sub": "telegram_user_id",
  "iat": 1234567890,
  "exp": 1234654290,  # 24h expiry
  "scope": ["execute_shell", "create_task"],
  "rate_limit": {
    "rpm": 10,
    "daily": 1000
  }
}
```

**Validation Middleware**:
```python
async def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=["HS256"]
        )
        # Check expiry
        if payload["exp"] < time.time():
            raise HTTPException(401, "Token expired")
        # Verify scope
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### 3. Input Validation & Sanitization

**Command Whitelist**:
```python
ALLOWED_COMMANDS = {
    "ls": ["-la", "-l", "-a"],
    "cat": ["*.txt", "*.md", "*.py"],
    "grep": ["-n", "-i", "-r"],
    "pwd": [],
    "echo": [],
    "git": ["status", "log", "diff"]
}

def validate_command(cmd: str) -> bool:
    parts = shlex.split(cmd)
    base_cmd = parts[0]
    
    if base_cmd not in ALLOWED_COMMANDS:
        return False
    
    # Additional validation for arguments
    return True
```

**Path Traversal Prevention**:
```python
def sanitize_path(user_path: str, base_dir: str) -> str:
    # Resolve to absolute path
    abs_path = os.path.abspath(os.path.join(base_dir, user_path))
    
    # Ensure it's within base_dir
    if not abs_path.startswith(os.path.abspath(base_dir)):
        raise ValueError("Path traversal detected")
    
    return abs_path
```

### 4. Secrets Management

**Development (SOPS)**:
```bash
# Encrypt secrets
sops -e -i .env.encrypted

# Decrypt for local use
sops -d .env.encrypted > .env
```

**Production (HashiCorp Vault)**:
```python
# vault_client.py
import hvac

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),
            token=self._get_vault_token()
        )
    
    def get_secret(self, path: str) -> dict:
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point='secret'
        )
        return response['data']['data']
    
    def rotate_database_credentials(self):
        # Automatic rotation every 90 days
        self.client.write('database/rotate-root/postgres')
```

### 5. Rate Limiting

**Implementation**:
```python
from typing import Optional
import aioredis
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        limit: int = 10, 
        window: int = 60
    ) -> tuple[bool, Optional[int]]:
        key = f"rate_limit:{user_id}:{datetime.now().minute}"
        
        try:
            current = await self.redis.incr(key)
            
            if current == 1:
                await self.redis.expire(key, window)
            
            if current > limit:
                ttl = await self.redis.ttl(key)
                return False, ttl
            
            return True, None
            
        except Exception as e:
            # Fail open in case of Redis failure
            logger.error(f"Rate limit check failed: {e}")
            return True, None
```

### 6. Audit Logging

**Audit Event Structure**:
```python
class AuditEvent(BaseModel):
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    result: str  # success/failure
    ip_address: str
    user_agent: str
    details: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Critical Events to Log**:
- Authentication attempts (success/failure)
- Authorization failures
- Command execution in sandbox
- File access/modification
- Configuration changes
- Security exceptions

---

## 🛡️ Security Checklist

### Pre-Deployment
- [ ] All secrets are encrypted and not in source control
- [ ] Docker images are scanned for vulnerabilities
- [ ] Dependencies are up-to-date and scanned
- [ ] Security headers are configured
- [ ] SSL/TLS certificates are valid
- [ ] Firewall rules are restrictive

### Runtime Security
- [ ] Sandbox isolation is verified
- [ ] Rate limiting is active
- [ ] Monitoring alerts are configured
- [ ] Backup encryption is enabled
- [ ] Audit logs are being collected
- [ ] Intrusion detection is active

### Incident Response
- [ ] Security contacts are documented
- [ ] Incident response plan exists
- [ ] Backup restoration tested
- [ ] Communication plan ready
- [ ] Post-mortem process defined

---

## 🚫 Security Anti-Patterns to Avoid

1. **Never** execute user input directly without validation
2. **Never** store secrets in environment variables in production
3. **Never** disable security features for convenience
4. **Never** trust client-side validation
5. **Never** log sensitive data (passwords, tokens, PII)
6. **Never** use outdated cryptographic algorithms

---

## 📊 Security Metrics

Track these KPIs monthly:
- Failed authentication attempts
- Sandbox escape attempts
- Rate limit violations
- Vulnerability scan findings
- Time to patch critical vulnerabilities
- Security training completion rate

---

## 🔐 Cryptographic Standards

- **Encryption at rest**: AES-256-GCM
- **Encryption in transit**: TLS 1.3+
- **Password hashing**: Argon2id
- **Token signing**: HMAC-SHA256
- **Random generation**: cryptographically secure PRNG

---

## 📞 Security Contacts

- **Security Lead**: security@company.com
- **Incident Response**: incident-response@company.com
- **Bug Bounty**: security-bounty@company.com

---

## 🐛 Vulnerability Disclosure

We follow responsible disclosure:
1. Report to security@company.com
2. 90-day disclosure timeline
3. Credit given to researchers
4. No legal action for good-faith research

---

Remember: **Security is everyone's responsibility!** 
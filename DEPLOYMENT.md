# Production Deployment Guide

This guide covers deploying the Algorithmic Trading Platform to production environments.

## Prerequisites

- Docker and Docker Compose installed
- Kubernetes cluster (for K8s deployment)
- PostgreSQL 15+ database
- Redis 7+ instance
- Domain name and SSL certificates
- Monitoring tools (Prometheus, Grafana)

## Environment Setup

### 1. Environment Variables

Create a `.env` file with production values:

```bash
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/trading_platform
REDIS_URL=redis://redis-host:6379

# Security
SECRET_KEY=<generate-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
ALPHA_VANTAGE_API_KEY=<your-key>
IEX_CLOUD_API_KEY=<your-key>
POLYGON_API_KEY=<your-key>

# Application
DEBUG=False
ALLOWED_HOSTS=https://yourdomain.com,https://api.yourdomain.com

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_ENABLED=True
```

### 2. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Docker Deployment

### 1. Build Images

```bash
docker-compose build
```

### 2. Run Database Migrations

```bash
docker-compose run --rm backend alembic upgrade head
```

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check health
curl http://localhost/health

# Check logs
docker-compose logs -f backend
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace trading-platform
```

### 2. Create Secrets

```bash
kubectl create secret generic trading-platform-secrets \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=redis-url=$REDIS_URL \
  --from-literal=secret-key=$SECRET_KEY \
  -n trading-platform
```

### 3. Deploy Services

```bash
kubectl apply -f k8s/ -n trading-platform
```

### 4. Check Deployment Status

```bash
kubectl get pods -n trading-platform
kubectl get services -n trading-platform
```

## Database Setup

### 1. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Create initial admin user (if needed)
python scripts/create_admin.py
```

### 2. Set Up TimescaleDB

```sql
-- Connect to TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert market_data table to hypertable
SELECT create_hypertable('market_data', 'timestamp');
```

## Monitoring Setup

### 1. Prometheus Configuration

Update `monitoring/prometheus.yml` with your service endpoints.

### 2. Grafana Dashboards

Import dashboards from `monitoring/grafana/dashboards/`.

### 3. Set Up Alerts

Configure alerting rules in `monitoring/prometheus/rules/`.

## Security Hardening

### 1. SSL/TLS Configuration

- Use Let's Encrypt for SSL certificates
- Configure Nginx with SSL
- Enable HSTS headers

### 2. Firewall Rules

- Only expose necessary ports (80, 443)
- Restrict database access to internal network
- Use VPN for admin access

### 3. Authentication

- Enable JWT authentication
- Implement rate limiting
- Use strong password policies

### 4. Data Encryption

- Encrypt sensitive data at rest
- Use TLS for all connections
- Secure API keys and secrets

## Performance Optimization

### 1. Database Optimization

- Create appropriate indexes
- Use connection pooling
- Enable query caching
- Regular VACUUM and ANALYZE

### 2. Caching Strategy

- Cache frequently accessed data
- Use Redis for session storage
- Implement CDN for static assets

### 3. Load Balancing

- Use Nginx as reverse proxy
- Configure multiple backend instances
- Implement health checks

## Backup and Recovery

### 1. Database Backups

```bash
# Automated daily backups
pg_dump -h db-host -U user trading_platform > backup_$(date +%Y%m%d).sql
```

### 2. Configuration Backups

- Version control all configuration files
- Backup environment variables securely
- Document all changes

### 3. Disaster Recovery Plan

- Regular backup testing
- Document recovery procedures
- Maintain off-site backups

## Scaling

### 1. Horizontal Scaling

- Add more backend instances
- Use load balancer
- Scale Celery workers

### 2. Vertical Scaling

- Increase database resources
- Add more Redis memory
- Optimize application code

## Maintenance

### 1. Regular Updates

- Keep dependencies updated
- Apply security patches
- Monitor for vulnerabilities

### 2. Log Management

- Rotate logs regularly
- Archive old logs
- Monitor log sizes

### 3. Health Monitoring

- Set up health check alerts
- Monitor resource usage
- Track error rates

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check connection string
   - Verify network connectivity
   - Check firewall rules

2. **Redis Connection Errors**
   - Verify Redis is running
   - Check connection pool settings
   - Monitor Redis memory usage

3. **High Memory Usage**
   - Review query patterns
   - Optimize data processing
   - Increase server resources

## Support

For production support:
- Check logs: `docker-compose logs -f`
- Monitor metrics in Grafana
- Review error tracking
- Contact DevOps team

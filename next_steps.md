# Cursor AI Prompt: Production-Grade Algorithmic Trading Platform

## 🎯 Project Context

You are working on a **full-stack algorithmic trading platform** built with:
- **Backend**: Python, FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery
- **Frontend**: React, TypeScript, Redux Toolkit, Tailwind CSS
- **DevOps**: Docker, Docker Compose

**Current Status**: Core features implemented (auth, dashboards, market data, backtesting, ML models)
**Goal**: Transform into a production-ready, enterprise-grade application

---

## 🎓 Your Role & Guidelines

### Core Principles
1. **Production-First Mindset**: Every change must be production-ready (security, performance, reliability)
2. **Test-Driven**: Write tests BEFORE implementing features
3. **Security-Conscious**: Validate all inputs, secure all endpoints, follow OWASP guidelines
4. **Performance-Aware**: Optimize queries, use caching, minimize API calls
5. **User-Centric**: Clear error messages, loading states, accessibility
6. **Type-Safe**: Full TypeScript coverage, Pydantic models everywhere
7. **Well-Documented**: Inline comments, docstrings, API docs

### Code Quality Standards
- **Python**: PEP 8, type hints, async/await, comprehensive error handling
- **TypeScript**: Strict mode, no `any`, proper interfaces
- **Testing**: >80% coverage, unit + integration + E2E
- **Security**: Input validation, SQL injection prevention, XSS protection
- **Performance**: Database indexes, query optimization, caching

---

## 📋 Implementation Priority

### Phase 1: Foundation (Security & Testing) - HIGHEST PRIORITY

#### 1.1 Testing Infrastructure
```plaintext
TASK: Set up comprehensive testing framework
- Backend: pytest, pytest-asyncio, pytest-cov, factory_boy
- Frontend: Jest, React Testing Library, MSW for API mocking
- E2E: Playwright or Cypress
- Target: >80% code coverage

REQUIREMENTS:
- Write tests FIRST (TDD approach)
- Test all API endpoints (success + error cases)
- Test authentication flows
- Test database operations
- Mock external APIs (Yahoo Finance)
- Test edge cases and error handling

FILES TO CREATE:
- backend/tests/conftest.py (fixtures, test db setup)
- backend/tests/test_auth.py
- backend/tests/test_strategies.py
- backend/tests/test_market_data.py
- backend/tests/test_backtesting.py
- frontend/src/__tests__/components/
- frontend/src/__tests__/features/
- e2e/tests/

COMMANDS TO RUN:
pytest --cov=backend --cov-report=html
npm test -- --coverage
```

#### 1.2 Security Hardening
```plaintext
TASK: Implement enterprise-grade security

REQUIREMENTS:
✓ Input Validation:
  - Pydantic models for all API inputs
  - SQL injection prevention (parameterized queries)
  - XSS protection (sanitize HTML inputs)
  - File upload validation (if applicable)

✓ Authentication & Authorization:
  - JWT token expiration (15 min access, 7 day refresh)
  - Token blacklisting for logout
  - Password requirements (min 8 chars, complexity)
  - Rate limiting on auth endpoints (5 attempts/min)
  - CSRF protection

✓ API Security:
  - Rate limiting (100 requests/min per user)
  - Request size limits
  - CORS properly configured
  - Security headers (CSP, X-Frame-Options, etc.)
  - API key rotation mechanism

✓ Data Security:
  - Encrypt sensitive data at rest
  - Secure password hashing (bcrypt, cost=12)
  - No secrets in code (env variables only)
  - Audit logging for sensitive operations

FILES TO MODIFY/CREATE:
- backend/app/core/security.py (enhanced)
- backend/app/middleware/rate_limiter.py (new)
- backend/app/middleware/security_headers.py (new)
- backend/app/core/config.py (security settings)
- backend/app/models/audit_log.py (new)
```

#### 1.3 Error Handling & Monitoring
```plaintext
TASK: Implement comprehensive error tracking and monitoring

REQUIREMENTS:
✓ Error Tracking:
  - Integrate Sentry for error tracking
  - Custom error classes for different error types
  - Structured error responses
  - Error context (user ID, request ID, timestamp)

✓ Logging:
  - Structured logging (JSON format)
  - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Request/response logging
  - Performance logging (slow queries)
  - Correlation IDs for request tracing

✓ Monitoring:
  - Health check endpoints (/health, /ready)
  - Metrics endpoint (Prometheus format)
  - Database connection pool monitoring
  - Redis connection monitoring
  - Background task monitoring

FILES TO CREATE:
- backend/app/core/logging.py (structured logging)
- backend/app/core/monitoring.py (metrics)
- backend/app/middleware/request_logger.py
- backend/app/api/health.py (health checks)
- backend/app/core/exceptions.py (custom exceptions)

INTEGRATIONS:
- Sentry SDK
- Prometheus client
- Grafana dashboards (optional)
```

---

### Phase 2: Performance Optimization

#### 2.1 Database Optimization
```plaintext
TASK: Optimize database performance

REQUIREMENTS:
✓ Indexing:
  - Add indexes on frequently queried columns
  - Composite indexes for multi-column queries
  - Index on foreign keys
  - EXPLAIN ANALYZE on slow queries

✓ Query Optimization:
  - Use select_related/joinedload for relationships
  - Implement pagination (limit/offset)
  - Avoid N+1 queries
  - Use database views for complex queries
  - Batch operations where possible

✓ Connection Pooling:
  - Configure optimal pool size
  - Connection timeout settings
  - Pool pre-ping for stale connections

FILES TO MODIFY:
- backend/alembic/versions/*.py (add indexes)
- backend/app/models/*.py (add indexes to models)
- backend/app/db/session.py (pool configuration)
- backend/app/crud/*.py (optimize queries)

SQL EXAMPLES:
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_strategy_user_id ON strategies(user_id);
CREATE INDEX idx_backtest_strategy_id ON backtests(strategy_id);
```

#### 2.2 Caching Strategy
```plaintext
TASK: Implement comprehensive caching

REQUIREMENTS:
✓ Redis Caching:
  - Market data caching (30s-5min TTL)
  - User session caching
  - Frequently accessed data (strategies, preferences)
  - Cache invalidation strategy

✓ HTTP Caching:
  - ETags for static content
  - Cache-Control headers
  - CDN integration (CloudFlare/AWS CloudFront)

✓ Database Query Caching:
  - SQLAlchemy query caching
  - Cached properties for computed values

FILES TO CREATE/MODIFY:
- backend/app/core/cache.py (caching utilities)
- backend/app/api/deps.py (cache dependencies)
- backend/app/services/market_data.py (add caching)
- frontend/src/services/cache.ts (client-side caching)
```

#### 2.3 Frontend Performance
```plaintext
TASK: Optimize frontend performance

REQUIREMENTS:
✓ Code Splitting:
  - Route-based code splitting
  - Lazy loading for heavy components
  - Dynamic imports for large libraries

✓ Bundle Optimization:
  - Tree shaking
  - Minimize bundle size (<500KB initial)
  - Use production builds
  - Analyze bundle with webpack-bundle-analyzer

✓ Rendering Optimization:
  - React.memo for expensive components
  - useMemo/useCallback for expensive computations
  - Virtual scrolling for large lists
  - Debounce/throttle for frequent updates

✓ Asset Optimization:
  - Image optimization (WebP format)
  - Lazy loading images
  - CDN for static assets
  - Service worker for offline support

FILES TO MODIFY:
- frontend/vite.config.ts (optimization settings)
- frontend/src/App.tsx (code splitting)
- frontend/src/components/*.tsx (memoization)
```

---

### Phase 3: Production Features

#### 3.1 Live Trading (Paper Mode)
```plaintext
TASK: Implement paper trading functionality

REQUIREMENTS:
✓ Order Management:
  - Market orders (buy/sell)
  - Limit orders
  - Stop-loss orders
  - Order validation (balance, quantity)
  - Order status tracking

✓ Position Management:
  - Track open positions
  - Calculate P&L (realized/unrealized)
  - Position sizing
  - Risk management (max position size)

✓ Portfolio Tracking:
  - Real-time portfolio value
  - Asset allocation
  - Performance metrics
  - Transaction history

FILES TO CREATE:
- backend/app/models/order.py
- backend/app/models/position.py
- backend/app/models/portfolio.py
- backend/app/services/trading_engine.py
- backend/app/api/trading.py
- frontend/src/features/trading/

API ENDPOINTS:
POST /api/orders - Place order
GET /api/orders - List orders
GET /api/positions - List positions
GET /api/portfolio - Get portfolio
```

#### 3.2 Advanced Strategy Builder
```plaintext
TASK: Create visual strategy builder

REQUIREMENTS:
✓ UI Components:
  - Drag-and-drop interface
  - Strategy blocks (indicators, conditions, actions)
  - Visual flow editor
  - Code preview

✓ Strategy Templates:
  - Moving average crossover
  - RSI divergence
  - Bollinger bands breakout
  - MACD strategy
  - Custom template creation

✓ Strategy Testing:
  - Quick backtest (last 30 days)
  - Parameter optimization
  - Walk-forward testing
  - Monte Carlo simulation

FILES TO CREATE:
- frontend/src/features/strategy-builder/
- backend/app/services/strategy_compiler.py
- backend/app/models/strategy_template.py
```

#### 3.3 Notifications & Alerts
```plaintext
TASK: Implement notification system

REQUIREMENTS:
✓ Alert Types:
  - Price alerts (target price reached)
  - Strategy signals (buy/sell)
  - Risk alerts (max drawdown, stop-loss)
  - System alerts (errors, maintenance)

✓ Delivery Channels:
  - In-app notifications
  - Email notifications
  - Push notifications (optional)
  - Webhook integrations

✓ Alert Management:
  - Create/edit/delete alerts
  - Alert history
  - Notification preferences
  - Mute/unmute alerts

FILES TO CREATE:
- backend/app/models/alert.py
- backend/app/services/notification_service.py
- backend/app/services/email_service.py
- backend/app/tasks/alert_checker.py (Celery task)
- frontend/src/features/notifications/
```

---

### Phase 4: DevOps & Infrastructure

#### 4.1 CI/CD Pipeline
```plaintext
TASK: Set up automated deployment pipeline

REQUIREMENTS:
✓ GitHub Actions Workflow:
  - Run tests on every PR
  - Lint code (pylint, eslint)
  - Type checking (mypy, tsc)
  - Security scanning (bandit, npm audit)
  - Build Docker images
  - Deploy to staging on merge to develop
  - Deploy to production on release tag

✓ Quality Gates:
  - All tests must pass
  - Code coverage >80%
  - No critical security vulnerabilities
  - No type errors
  - Lint score >8/10

FILES TO CREATE:
- .github/workflows/ci.yml
- .github/workflows/cd.yml
- .github/workflows/security-scan.yml
- scripts/deploy.sh
- docker-compose.production.yml
```

#### 4.2 Monitoring & Logging
```plaintext
TASK: Set up production monitoring

REQUIREMENTS:
✓ Application Monitoring:
  - Prometheus metrics
  - Grafana dashboards
  - Uptime monitoring
  - Response time tracking
  - Error rate tracking

✓ Log Aggregation:
  - Centralized logging (ELK stack or Loki)
  - Log parsing and indexing
  - Log retention policy
  - Log search and analysis

✓ Alerting:
  - CPU/Memory alerts
  - Error rate alerts
  - Slow query alerts
  - Disk space alerts

FILES TO CREATE:
- monitoring/prometheus.yml
- monitoring/grafana/dashboards/
- monitoring/alertmanager.yml
- docker-compose.monitoring.yml
```

#### 4.3 Backup & Disaster Recovery
```plaintext
TASK: Implement backup and recovery

REQUIREMENTS:
✓ Database Backups:
  - Automated daily backups
  - Point-in-time recovery
  - Backup retention (30 days)
  - Backup encryption
  - Backup verification

✓ Application State:
  - Redis snapshot backups
  - Configuration backups
  - User data exports

✓ Disaster Recovery:
  - Recovery playbook
  - Failover procedures
  - Data restoration tests

FILES TO CREATE:
- scripts/backup_database.sh
- scripts/restore_database.sh
- docs/disaster-recovery.md
```

---

## 🔧 Implementation Commands

### When Starting a Task
```bash
# 1. Create feature branch
git checkout -b feature/task-name

# 2. Install dependencies if needed
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 3. Run tests before changes
pytest
npm test
```

### During Implementation
```bash
# Run tests frequently
pytest -v
npm test

# Check code quality
pylint backend/app
eslint frontend/src
mypy backend/app

# Check security
bandit -r backend/app
npm audit
```

### Before Committing
```bash
# Format code
black backend/app
prettier --write frontend/src

# Run full test suite
pytest --cov=backend --cov-report=html
npm test -- --coverage

# Check types
mypy backend/app
tsc --noEmit

# Verify Docker builds
docker-compose build
```

---

## 📝 Code Examples & Patterns

### Backend: API Endpoint Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.strategy import StrategyCreate, StrategyResponse
from app.services.strategy_service import StrategyService
import structlog

router = APIRouter()
logger = structlog.get_logger()

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    *,
    db: AsyncSession = Depends(deps.get_db),
    strategy_in: StrategyCreate,
    current_user: User = Depends(deps.get_current_user),
) -> StrategyResponse:
    """
    Create new trading strategy.
    
    - **name**: Strategy name (unique per user)
    - **type**: Strategy type (momentum, mean_reversion, etc.)
    - **parameters**: Strategy parameters as JSON
    """
    try:
        # Validate input
        if not strategy_in.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strategy name is required"
            )
        
        # Create strategy
        strategy = await StrategyService.create(
            db=db,
            user_id=current_user.id,
            strategy_data=strategy_in
        )
        
        logger.info(
            "strategy_created",
            user_id=current_user.id,
            strategy_id=strategy.id,
            strategy_name=strategy.name
        )
        
        return strategy
        
    except ValueError as e:
        logger.warning("strategy_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("strategy_creation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create strategy"
        )
```

### Backend: Service Layer Pattern
```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.core.cache import cache
import structlog

logger = structlog.get_logger()

class StrategyService:
    """Strategy business logic service."""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        strategy_data: StrategyCreate
    ) -> Strategy:
        """Create a new strategy."""
        # Validate uniqueness
        existing = await StrategyService.get_by_name(
            db=db,
            user_id=user_id,
            name=strategy_data.name
        )
        if existing:
            raise ValueError(f"Strategy '{strategy_data.name}' already exists")
        
        # Create strategy
        strategy = Strategy(
            user_id=user_id,
            **strategy_data.dict()
        )
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)
        
        # Invalidate cache
        await cache.delete(f"user_strategies:{user_id}")
        
        return strategy
    
    @staticmethod
    @cache.cached(ttl=300, key_prefix="user_strategies")
    async def get_user_strategies(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Strategy]:
        """Get all strategies for a user."""
        result = await db.execute(
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Strategy.created_at.desc())
        )
        return result.scalars().all()
```

### Frontend: Component Pattern
```typescript
import React, { useState, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { createStrategy } from '@/store/features/strategies/strategiesSlice';
import { StrategyForm } from './StrategyForm';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import type { StrategyCreate } from '@/types/strategy';

export const CreateStrategy: React.FC = () => {
  const dispatch = useAppDispatch();
  const { loading, error } = useAppSelector(state => state.strategies);
  const [showForm, setShowForm] = useState(false);

  const handleSubmit = useCallback(async (data: StrategyCreate) => {
    try {
      await dispatch(createStrategy(data)).unwrap();
      setShowForm(false);
      // Show success toast
    } catch (err) {
      // Error handled by Redux slice
      console.error('Failed to create strategy:', err);
    }
  }, [dispatch]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-4">
      <button
        onClick={() => setShowForm(true)}
        className="btn btn-primary"
        disabled={loading}
      >
        Create Strategy
      </button>

      {error && <ErrorMessage message={error} />}

      {showForm && (
        <StrategyForm
          onSubmit={handleSubmit}
          onCancel={() => setShowForm(false)}
          loading={loading}
        />
      )}
    </div>
  );
};
```

### Testing Pattern
```python
import pytest
from httpx import AsyncClient
from app.models.user import User
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_create_strategy_success(
    client: AsyncClient,
    test_user: User,
    test_db
):
    """Test successful strategy creation."""
    # Arrange
    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    strategy_data = {
        "name": "Test Strategy",
        "type": "momentum",
        "parameters": {"period": 20}
    }
    
    # Act
    response = await client.post(
        "/api/strategies",
        json=strategy_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == strategy_data["name"]
    assert data["type"] == strategy_data["type"]
    assert data["user_id"] == test_user.id

@pytest.mark.asyncio
async def test_create_strategy_duplicate_name(
    client: AsyncClient,
    test_user: User,
    test_strategy
):
    """Test strategy creation with duplicate name fails."""
    token = create_access_token(test_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    strategy_data = {
        "name": test_strategy.name,  # Duplicate name
        "type": "momentum",
        "parameters": {}
    }
    
    response = await client.post(
        "/api/strategies",
        json=strategy_data,
        headers=headers
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
```

---

## ✅ Definition of Done

### For Each Feature
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Type hints/interfaces complete
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Documentation updated
- [ ] Code reviewed (self-review checklist)
- [ ] Performance tested
- [ ] Security reviewed
- [ ] Accessibility checked (frontend)

### For Each API Endpoint
- [ ] Input validation (Pydantic)
- [ ] Authentication required
- [ ] Rate limiting applied
- [ ] Error responses documented
- [ ] Success responses documented
- [ ] Tests cover success + error cases
- [ ] OpenAPI schema updated

### For Each Component
- [ ] TypeScript strict mode
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Accessibility (ARIA labels)
- [ ] Responsive design
- [ ] Tests written
- [ ] Storybook story (optional)

---

## 🚨 Critical Reminders

### Security
- ❌ NEVER commit secrets, API keys, or passwords
- ❌ NEVER trust user input without validation
- ❌ NEVER use string concatenation for SQL queries
- ✅ ALWAYS use parameterized queries
- ✅ ALWAYS validate and sanitize input
- ✅ ALWAYS use HTTPS in production

### Performance
- ❌ NEVER fetch all records without pagination
- ❌ NEVER make N+1 queries
- ❌ NEVER block the event loop (use async)
- ✅ ALWAYS add database indexes
- ✅ ALWAYS use caching for expensive operations
- ✅ ALWAYS paginate large result sets

### Testing
- ❌ NEVER skip tests
- ❌ NEVER commit without running tests
- ✅ ALWAYS write tests first (TDD)
- ✅ ALWAYS test error cases
- ✅ ALWAYS test edge cases

---

## 📚 Reference Documentation

### Backend
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/

### Frontend
- React: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/
- Redux Toolkit: https://redux-toolkit.js.org/
- Tailwind: https://tailwindcss.com/docs

### Security
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- JWT Best Practices: https://tools.ietf.org/html/rfc8725

---

## 🎯 Start Here

Begin with **Phase 1: Foundation** in this order:
1. Testing Infrastructure (1.1)
2. Security Hardening (1.2)
3. Error Handling & Monitoring (1.3)

**For each task:**
1. Read the requirements carefully
2. Write tests FIRST
3. Implement the feature
4. Run all tests
5. Review code quality
6. Update documentation
7. Create PR with checklist

**Good luck building production-grade software! 🚀**
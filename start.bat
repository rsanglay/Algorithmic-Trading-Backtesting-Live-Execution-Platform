@echo off
REM Startup script for Trading Platform (Windows)

echo Starting Algorithmic Trading Platform...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker Desktop and try again.
    exit /b 1
)

REM Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Start services
echo Building and starting containers...
docker-compose -f docker-compose.dev.yml up --build -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo Checking service status...
docker-compose -f docker-compose.dev.yml ps

REM Run database migrations
echo Running database migrations...
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

echo.
echo Trading Platform is starting up!
echo.
echo Services available at:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - PostgreSQL: localhost:5432
echo    - Redis: localhost:6379
echo.
echo View logs with: docker-compose -f docker-compose.dev.yml logs -f
echo Stop services with: docker-compose -f docker-compose.dev.yml down
echo.
pause

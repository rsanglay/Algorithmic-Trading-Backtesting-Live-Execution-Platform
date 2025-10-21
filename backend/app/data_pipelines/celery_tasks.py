"""
Celery tasks for data processing
"""
from celery import Celery
from typing import List, Dict, Any
from datetime import datetime
import asyncio

from app.core.config import settings
from app.core.database import SessionLocal
from app.data_pipelines.etl_pipeline import ETLPipeline, NewsETLPipeline
from app.data_pipelines.streaming_pipeline import StreamingPipeline, DataQualityPipeline

# Initialize Celery
celery_app = Celery(
    "trading_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@celery_app.task(bind=True)
def run_etl_pipeline(self, symbols: List[str], start_date: str, end_date: str, source: str = "yfinance"):
    """Run ETL pipeline as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting ETL pipeline"})
        
        # Create database session
        db = SessionLocal()
        
        # Create ETL pipeline
        etl_pipeline = ETLPipeline(db)
        
        # Convert date strings to datetime objects
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Run ETL pipeline
        results = asyncio.run(etl_pipeline.run_etl_pipeline(symbols, start_dt, end_dt, source))
        
        # Update task state
        self.update_state(state="SUCCESS", meta={"status": "ETL pipeline completed", "results": results})
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "ETL pipeline failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def run_news_etl_pipeline(self, symbols: List[str], start_date: str, end_date: str):
    """Run news ETL pipeline as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting news ETL pipeline"})
        
        # Create database session
        db = SessionLocal()
        
        # Create news ETL pipeline
        news_etl_pipeline = NewsETLPipeline(db)
        
        # Convert date strings to datetime objects
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Run news ETL pipeline
        results = asyncio.run(news_etl_pipeline.run_news_etl_pipeline(symbols, start_dt, end_dt))
        
        # Update task state
        self.update_state(state="SUCCESS", meta={"status": "News ETL pipeline completed", "results": results})
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "News ETL pipeline failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def run_data_quality_check(self, data: Dict[str, Any]):
    """Run data quality check as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Running data quality check"})
        
        # Create database session
        db = SessionLocal()
        
        # Create data quality pipeline
        quality_pipeline = DataQualityPipeline(db)
        
        # Run data quality check
        results = asyncio.run(quality_pipeline.run_data_quality_check(data))
        
        # Update task state
        self.update_state(state="SUCCESS", meta={"status": "Data quality check completed", "results": results})
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "Data quality check failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def process_market_data_batch(self, data_batch: List[Dict[str, Any]]):
    """Process a batch of market data as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Processing market data batch"})
        
        # Create database session
        db = SessionLocal()
        
        # Process each data item
        processed_count = 0
        errors = []
        
        for data in data_batch:
            try:
                # Validate data
                quality_pipeline = DataQualityPipeline(db)
                quality_results = asyncio.run(quality_pipeline.run_data_quality_check(data))
                
                if quality_results["validation"]["is_valid"]:
                    # Store data
                    from app.models.market_data import MarketData
                    
                    market_data = MarketData(
                        symbol=data["symbol"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        open_price=data["open_price"],
                        high_price=data["high_price"],
                        low_price=data["low_price"],
                        close_price=data["close_price"],
                        volume=data["volume"],
                        source=data.get("source", "batch_processing")
                    )
                    
                    db.add(market_data)
                    db.commit()
                    processed_count += 1
                else:
                    errors.append({
                        "data": data,
                        "errors": quality_results["validation"]["errors"]
                    })
                    
            except Exception as e:
                errors.append({
                    "data": data,
                    "error": str(e)
                })
        
        # Update task state
        self.update_state(state="SUCCESS", meta={
            "status": "Batch processing completed",
            "processed_count": processed_count,
            "errors": errors
        })
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "errors": errors
        }
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "Batch processing failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def sync_market_data(self, symbols: List[str], start_date: str, end_date: str, source: str = "yfinance"):
    """Sync market data from external sources as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting market data sync"})
        
        # Create database session
        db = SessionLocal()
        
        # Create ETL pipeline
        etl_pipeline = ETLPipeline(db)
        
        # Convert date strings to datetime objects
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Run ETL pipeline
        results = asyncio.run(etl_pipeline.run_etl_pipeline(symbols, start_dt, end_dt, source))
        
        # Update task state
        self.update_state(state="SUCCESS", meta={"status": "Market data sync completed", "results": results})
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "Market data sync failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def cleanup_old_data(self, days_to_keep: int = 365):
    """Clean up old market data as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Starting data cleanup"})
        
        # Create database session
        db = SessionLocal()
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Delete old data
        from app.models.market_data import MarketData
        
        deleted_count = db.query(MarketData).filter(
            MarketData.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        # Update task state
        self.update_state(state="SUCCESS", meta={
            "status": "Data cleanup completed",
            "deleted_count": deleted_count
        })
        
        return {"status": "success", "deleted_count": deleted_count}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "Data cleanup failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


@celery_app.task(bind=True)
def generate_market_report(self, symbols: List[str], start_date: str, end_date: str):
    """Generate market report as a Celery task"""
    try:
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Generating market report"})
        
        # Create database session
        db = SessionLocal()
        
        # Generate report
        report_data = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "details": {}
        }
        
        # Add summary statistics for each symbol
        for symbol in symbols:
            # Get market data for symbol
            from app.models.market_data import MarketData
            
            market_data = db.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.timestamp >= datetime.fromisoformat(start_date),
                MarketData.timestamp <= datetime.fromisoformat(end_date)
            ).all()
            
            if market_data:
                prices = [row.close_price for row in market_data]
                volumes = [row.volume for row in market_data]
                
                report_data["summary"][symbol] = {
                    "data_points": len(market_data),
                    "price_range": {
                        "min": min(prices),
                        "max": max(prices),
                        "avg": sum(prices) / len(prices)
                    },
                    "volume_range": {
                        "min": min(volumes),
                        "max": max(volumes),
                        "avg": sum(volumes) / len(volumes)
                    }
                }
        
        # Update task state
        self.update_state(state="SUCCESS", meta={"status": "Market report generated", "report": report_data})
        
        return {"status": "success", "report": report_data}
        
    except Exception as e:
        # Update task state with error
        self.update_state(state="FAILURE", meta={"status": "Market report generation failed", "error": str(e)})
        raise e
    
    finally:
        db.close()


# Periodic tasks
@celery_app.task
def daily_data_sync():
    """Daily data sync task"""
    from datetime import datetime, timedelta
    
    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    start_date = yesterday.strftime("%Y-%m-%d")
    end_date = yesterday.strftime("%Y-%m-%d")
    
    # Default symbols to sync
    symbols = ["SPY", "QQQ", "IWM", "GLD", "TLT"]
    
    # Run sync task
    sync_market_data.delay(symbols, start_date, end_date, "yfinance")


@celery_app.task
def hourly_data_quality_check():
    """Hourly data quality check task"""
    from datetime import datetime, timedelta
    
    # Get recent data
    recent_time = datetime.now() - timedelta(hours=1)
    
    # This would query recent data and run quality checks
    # For now, just log the task
    print(f"Running hourly data quality check at {datetime.now()}")


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'daily-data-sync': {
        'task': 'app.data_pipelines.celery_tasks.daily_data_sync',
        'schedule': 60.0 * 60.0 * 24.0,  # Run daily
    },
    'hourly-data-quality-check': {
        'task': 'app.data_pipelines.celery_tasks.hourly_data_quality_check',
        'schedule': 60.0 * 60.0,  # Run hourly
    },
}

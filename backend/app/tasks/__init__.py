from celery import Celery
from celery.schedules import crontab

from app.config import get_settings
from app.agents.monitoring_agent import monitoring_agent
from app.agents.analysis_agent import analysis_agent

settings = get_settings()

celery_app = Celery(
    "picks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.stock_tasks",
        "app.tasks.monitoring_tasks",
        "app.tasks.analysis_tasks",
        "app.tasks.recommendation_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    beat_schedule={
        # 既存タスク
        "fetch-watchlist-prices": {
            "task": "app.tasks.stock_tasks.fetch_watchlist_prices",
            "schedule": crontab(minute="*/5", hour="9-15", day_of_week="mon-fri"),
        },
        "fetch-all-prices": {
            "task": "app.tasks.stock_tasks.fetch_daily_stock_prices",
            "schedule": crontab(hour=16, minute=0, day_of_week="mon-fri"),
        },
        "monitor-watchlist": {
            "task": "app.tasks.monitoring_tasks.monitor_stocks_task",
            "schedule": crontab(minute="*/10", hour="9-15", day_of_week="mon-fri"),
        },
        "daily-recommendations": {
            "task": "app.tasks.recommendation_tasks.generate_daily_recommendations",
            "schedule": crontab(hour=17, minute=0, day_of_week="mon-fri"),
        },
        # AIエージェントタスク（PydanticAI統合後）
        "agent-monitoring": {
            "task": "app.tasks.analysis_tasks.run_monitoring_agent",
            "schedule": crontab(minute="*/10", hour="9-15", day_of_week="mon-fri"),
        },
        "agent-analysis": {
            "task": "app.tasks.analysis_tasks.run_analysis_agent",
            "schedule": crontab(minute="*/30", hour="9-15", day_of_week="mon-fri"),
        },
    },
)

from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler
from pathlib import Path
from run_pipeline import run_all


def main() -> None:
    root = Path(__file__).resolve().parent
    scheduler = BlockingScheduler(timezone='Asia/Kolkata')
    scheduler.add_job(lambda: run_all(root), 'cron', hour=8, minute=0, id='daily_full_pipeline')
    scheduler.add_job(lambda: run_all(root), 'cron', day_of_week='mon', hour=9, minute=0, id='weekly_strategy_refresh')
    scheduler.start()


if __name__ == '__main__':
    main()

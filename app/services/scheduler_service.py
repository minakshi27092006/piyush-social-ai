from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import add_log, get_setting, set_setting
from app.pipeline import run_auto_pilot_pipeline

scheduler = BackgroundScheduler()
JOB_ID = "facebook_auto_pilot_job"

def scheduler_task_wrapper():
    """Executed automatically on the scheduled interval."""
    try:
        add_log("Scheduler triggered auto-post cycle", "INFO", "SCHEDULER_TICK")
        run_auto_pilot_pipeline()
    except Exception as e:
        add_log(f"Scheduler job error: {str(e)}", "ERROR", "SCHEDULER_ERROR")

def start_scheduler(hours: float = 1.0):
    """Starts or reschedules the auto-pilot interval job."""
    global scheduler
    if not scheduler.running:
        scheduler.start()
        
    minutes = int(hours * 60)
    if minutes < 1:
        minutes = 60 # minimum 1 minute protection
        
    trigger = IntervalTrigger(minutes=minutes)
    
    # Check if job already exists
    if scheduler.get_job(JOB_ID):
        scheduler.reschedule_job(JOB_ID, trigger=trigger)
    else:
        scheduler.add_job(
            scheduler_task_wrapper,
            trigger=trigger,
            id=JOB_ID,
            name="Facebook Autonomous Auto-Pilot Post Job",
            replace_existing=True
        )
        
    set_setting("auto_pilot_enabled", "true")
    set_setting("interval_hours", str(hours))
    add_log(f"Auto-pilot started with interval: every {hours} hour(s) [{minutes} minutes]", "SUCCESS", "SCHEDULER_STARTED")

def stop_scheduler():
    """Pauses/removes the auto-pilot job."""
    global scheduler
    if scheduler.get_job(JOB_ID):
        scheduler.remove_job(JOB_ID)
    set_setting("auto_pilot_enabled", "false")
    add_log("Auto-pilot interval posting has been paused.", "WARNING", "SCHEDULER_STOPPED")

def get_scheduler_status():
    """Returns live status, next execution time, and interval."""
    job = scheduler.get_job(JOB_ID)
    enabled = get_setting("auto_pilot_enabled", "false").lower() == "true"
    interval = float(get_setting("interval_hours", "1.0"))
    
    next_run = None
    seconds_remaining = None
    if job and job.next_run_time:
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        remaining = job.next_run_time - datetime.now(job.next_run_time.tzinfo)
        seconds_remaining = max(0, int(remaining.total_seconds()))
        
    return {
        "running": enabled and job is not None,
        "interval_hours": interval,
        "next_run_time": next_run,
        "seconds_remaining": seconds_remaining,
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

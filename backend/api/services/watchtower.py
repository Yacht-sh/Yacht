import os
from apscheduler.schedulers.background import BackgroundScheduler
from api.actions.compose import compose_action
from api.settings import Settings
from api.utils.compose import find_yml_files
import logging

logger = logging.getLogger("yacht.watchtower")

settings = Settings()
scheduler = BackgroundScheduler()

def update_compose_project(project_name):
    """
    Pulls images and updates the stack for a given compose project.
    """
    logger.info(f"Auto-updating project: {project_name}")
    try:
        # Pull is implicitly handled if we do 'pull' action or if 'up' pulls?
        # docker-compose up -d usually pulls if missing, but to force update we need pull first.
        # api.actions.compose.compose_action handles basic actions.
        # We need to extend it or call it twice.

        # 1. Pull
        logger.info(f"Pulling images for {project_name}...")
        # compose_action doesn't support "pull" explicitly yet in the original code unless updated.
        # But 'docker-compose pull' is a valid command.
        # api.actions.compose.compose_action calls docker_compose(action, ...)
        # So it should work if we pass "pull" as action.
        compose_action(project_name, "pull")

        # 2. Up -d
        logger.info(f"Recreating containers for {project_name}...")
        compose_action(project_name, "up")

        logger.info(f"Successfully updated {project_name}")
    except Exception as e:
        logger.error(f"Failed to update {project_name}: {e}")

def update_all_projects():
    """
    Iterates through all compose projects and updates them.
    """
    files = find_yml_files(settings.COMPOSE_DIR)
    for project_name in files.keys():
        update_compose_project(project_name)

def start_scheduler():
    # Schedule update every 24 hours (example)
    # Ideally this should be configurable via DB settings
    scheduler.add_job(update_all_projects, 'interval', hours=24, id='auto_update_all')
    scheduler.start()
    logger.info("Watchtower scheduler started.")

def stop_scheduler():
    scheduler.shutdown()

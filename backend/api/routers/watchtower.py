from fastapi import APIRouter, Depends, BackgroundTasks
from api.auth.jwt import get_auth_wrapper
from api.auth.auth import auth_check
from api.services.watchtower import update_compose_project, update_all_projects

router = APIRouter()

@router.post("/update/{project_name}")
def trigger_project_update(project_name: str, background_tasks: BackgroundTasks, Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    background_tasks.add_task(update_compose_project, project_name)
    return {"message": f"Update triggered for {project_name}"}

@router.post("/update-all")
def trigger_all_updates(background_tasks: BackgroundTasks, Authorize: get_auth_wrapper = Depends(get_auth_wrapper)):
    auth_check(Authorize)
    background_tasks.add_task(update_all_projects)
    return {"message": "Update triggered for all projects"}

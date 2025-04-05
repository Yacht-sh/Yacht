from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from api.db.models import containers as models
from api.utils.templates import conv_sysctls2dict, conv_ports2dict

from datetime import datetime
import urllib.request
from urllib.parse import urlparse
import json
import yaml
import os

# Templates


def get_templates(db: Session):
    return db.query(models.Template).all()


def get_template(db: Session, url: str):
    return db.query(models.Template).filter(models.Template.url == url).first()


def get_template_by_id(db: Session, id: int):
    return db.query(models.Template).filter(models.Template.id == id).first()


def get_template_items(db: Session, template_id: int):
    return (
        db.query(models.TemplateItem)
        .filter(models.TemplateItem.template_id == template_id)
        .all()
    )


def delete_template(db: Session, template_id: int):
    _template = (
        db.query(models.Template).filter(models.Template.id == template_id).first()
    )
    db.delete(_template)
    db.commit()
    return _template


def add_template(db: Session, template: models.Template):
    try:
        _template_path = urlparse(template.url).path
        ext = os.path.splitext(_template_path)[1]
        # Opens the JSON and iterate over the content.
        _template = models.Template(title=template.title, url=template.url)
        with urllib.request.urlopen(template.url) as file:
            if ext.rstrip() in (".yml", ".yaml"):
                loaded_file = yaml.load(file, Loader=yaml.SafeLoader)
            elif ext.rstrip() in (".json", "json"):
                loaded_file = json.load(file)
            else:
                print("Invalid filetype")
                raise
            if type(loaded_file) == list:
                for entry in loaded_file:
                    ports = conv_ports2dict(entry.get("ports", []))
                    sysctls = conv_sysctls2dict(entry.get("sysctls", []))

                    # Optional use classmethod from_dict
                    try:
                        template_content = models.TemplateItem(
                            type=int(entry.get("type", 1)),
                            title=entry["title"],
                            platform=entry["platform"],
                            description=entry.get("description", ""),
                            name=entry.get("name", entry["title"].lower()),
                            command=entry.get("command"),
                            logo=entry.get("logo", ""),  # default logo here!
                            image=entry.get("image", ""),
                            notes=entry.get("note", ""),
                            categories=entry.get("categories", ""),
                            restart_policy=entry.get("restart_policy"),
                            ports=ports,
                            network_mode=entry.get("network_mode", ""),
                            network=entry.get("network", ""),
                            volumes=entry.get("volumes", []),
                            env=entry.get("env", []),
                            devices=entry.get("devices", []),
                            labels=entry.get("labels", []),
                            sysctls=sysctls,
                            cap_add=entry.get("cap_add", []),
                            cpus=entry.get("cpus"),
                            mem_limit=entry.get("mem_limit"),
                        )
                    except Exception as exc:
                        raise HTTPException(
                            status_code=exc.response.status_code,
                            detail=entry.get("name") + " " + exc.explanation,
                        )
                    _template.items.append(template_content)
            elif type(loaded_file) == dict:
                entry = loaded_file
                ports = conv_ports2dict(entry.get("ports", []))
                sysctls = conv_sysctls2dict(entry.get("sysctls", []))

                # Optional use classmethod from_dict
                template_content = models.TemplateItem(
                    type=int(entry.get("type", 1)),
                    title=entry["title"],
                    platform=entry["platform"],
                    description=entry.get("description", ""),
                    name=entry.get("name", entry["title"].lower()),
                    command=entry.get("command"),
                    logo=entry.get("logo", ""),  # default logo here!
                    image=entry.get("image", ""),
                    notes=entry.get("note", ""),
                    categories=entry.get("categories", ""),
                    restart_policy=entry.get("restart_policy"),
                    ports=ports,
                    network_mode=entry.get("network_mode", ""),
                    network=entry.get("network", ""),
                    volumes=entry.get("volumes", []),
                    env=entry.get("env", []),
                    devices=entry.get("devices", []),
                    labels=entry.get("labels", []),
                    sysctls=sysctls,
                    cap_add=entry.get("cap_add", []),
                    cpus=entry.get("cpus"),
                    mem_limit=entry.get("mem_limit"),
                )
                _template.items.append(template_content)
    except (OSError, TypeError, ValueError) as err:
        # Optional handle KeyError here too.
        print("data request failed", err)
        raise HTTPException(status_code=err.status_code, detail=err.explanation)

    try:
        db.add(_template)
        db.commit()
    except IntegrityError as err:
        # TODO raises IntegrityError on duplicates (uniqueness)
        #       status
        db.rollback()

    return get_template(db=db, url=template.url)


def refresh_template(db: Session, template_id: id):
    template = (
        db.query(models.Template).filter(models.Template.id == template_id).first()
    )

    _template_path = urlparse(template.url).path
    ext = os.path.splitext(_template_path)[1]

    items = []
    try:
        with urllib.request.urlopen(template.url) as fp:
            if ext.rstrip() in (".yml", ".yaml"):
                loaded_file = yaml.load(fp, Loader=yaml.SafeLoader)
            elif ext.rstrip() in (".json"):
                loaded_file = json.load(fp)
            else:
                print("Invalid filetype")
                raise HTTPException(status_code=422, detail="Invalid filetype")
            if type(loaded_file) == list:
                for entry in loaded_file:

                    if entry.get("ports"):
                        ports = conv_ports2dict(entry.get("ports", []))
                    sysctls = conv_sysctls2dict(entry.get("sysctls", []))

                    item = models.TemplateItem(
                        type=int(entry["type"]),
                        title=entry["title"],
                        platform=entry["platform"],
                        description=entry.get("description", ""),
                        name=entry.get("name", entry["title"].lower()),
                        command=entry.get("command"),
                        logo=entry.get("logo", ""),  # default logo here!
                        image=entry.get("image", ""),
                        notes=entry.get("note", ""),
                        categories=entry.get("categories", ""),
                        restart_policy=entry.get("restart_policy"),
                        ports=ports,
                        network_mode=entry.get("network_mode", ""),
                        network=entry.get("network", ""),
                        volumes=entry.get("volumes", []),
                        env=entry.get("env", []),
                        devices=entry.get("devices", []),
                        labels=entry.get("labels", []),
                        sysctls=sysctls,
                        cap_add=entry.get("cap_add", []),
                        cpus=entry.get("cpus"),
                        mem_limit=entry.get("mem_limit"),
                    )
                    items.append(item)
            elif type(loaded_file) == dict:
                entry = loaded_file
                ports = conv_ports2dict(entry.get("ports", []))
                sysctls = conv_sysctls2dict(entry.get("sysctls", []))

                # Optional use classmethod from_dict
                template_content = models.TemplateItem(
                    type=int(entry["type"]),
                    title=entry["title"],
                    platform=entry["platform"],
                    description=entry.get("description", ""),
                    name=entry.get("name", entry["title"].lower()),
                    command=entry.get("command"),
                    logo=entry.get("logo", ""),  # default logo here!
                    image=entry.get("image", ""),
                    notes=entry.get("note", ""),
                    categories=entry.get("categories", ""),
                    restart_policy=entry.get("restart_policy"),
                    ports=ports,
                    network_mode=entry.get("network_mode", ""),
                    network=entry.get("network", ""),
                    volumes=entry.get("volumes", []),
                    env=entry.get("env", []),
                    devices=entry.get("devices", []),
                    labels=entry.get("labels", []),
                    sysctls=sysctls,
                    cap_add=entry.get("cap_add", []),
                    cpus=entry.get("cpus"),
                    mem_limit=entry.get("mem_limit"),
                )
                items.append(template_content)
    except Exception as exc:
        if hasattr(exc, "code") and exc.code == 404:
            raise HTTPException(status_code=exc.code, detail=exc.url)
        else:
            print("Template update failed. ERR_001", exc)
            raise HTTPException(status_code=exc.status_code, detail=exc.explanation)
    else:
        # db.delete(template)
        # make_transient(template)
        # db.commit()

        template.updated_at = datetime.utcnow()
        template.items = items

        try:
            # db.add(template)
            db.commit()
            print(f'Template "{template.title}" updated successfully.')
        except Exception as exc:
            db.rollback()
            print("Template update failed. ERR_002", exc)
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.explanation
            )

    return template


def read_app_template(db, app_id):
    try:
        template_item = (
            db.query(models.TemplateItem)
            .filter(models.TemplateItem.id == app_id)
            .first()
        )
        return template_item
    except Exception as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.explanation
        )


def set_template_variables(db: Session, new_variables: models.TemplateVariables):
    try:
        template_vars = db.query(models.TemplateVariables).all()

        variables = []
        t_vars = new_variables

        for entry in t_vars:
            template_variables = models.TemplateVariables(
                variable=entry.variable, replacement=entry.replacement
            )
            variables.append(template_variables)

        db.query(models.TemplateVariables).delete()
        db.add_all(variables)
        db.commit()

        new_template_variables = db.query(models.TemplateVariables).all()

        return new_template_variables

    except IntegrityError as exc:
        print(exc)
        raise HTTPException(status_code=exc.status_code, detail=exc.explanation)


def read_template_variables(db: Session):
    return db.query(models.TemplateVariables).all()

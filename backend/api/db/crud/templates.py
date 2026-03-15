from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException

from api.db.models import containers as models
from api.utils.templates import conv_sysctls2dict, conv_ports2dict

from datetime import datetime
from urllib.parse import urlparse, urlunparse
import ipaddress
import json
import yaml
import os
import requests
import socket

# Templates


def _validated_template_url(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"}:
        raise HTTPException(
            status_code=422, detail="Template URL must use http or https."
        )
    if parsed_url.username or parsed_url.password:
        raise HTTPException(status_code=422, detail="Template URL cannot include credentials.")
    if not parsed_url.hostname:
        raise HTTPException(status_code=422, detail="Template URL must include a hostname.")

    try:
        addresses = socket.getaddrinfo(parsed_url.hostname, parsed_url.port or None)
    except socket.gaierror as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for _, _, _, _, sockaddr in addresses:
        ip = ipaddress.ip_address(sockaddr[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise HTTPException(
                status_code=422,
                detail="Template URL must resolve to a public IP address.",
            )

    safe_netloc = parsed_url.hostname
    if parsed_url.port is not None:
        safe_netloc = f"{safe_netloc}:{parsed_url.port}"

    safe_path = parsed_url.path or "/"
    return urlunparse(
        (
            parsed_url.scheme,
            safe_netloc,
            safe_path,
            "",
            parsed_url.query,
            "",
        )
    )


def _template_extension(url: str) -> str:
    return os.path.splitext(urlparse(url).path)[1].lower()


def _load_template_data(url: str):
    safe_url = _validated_template_url(url)
    ext = _template_extension(safe_url)
    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.get(safe_url, timeout=10, allow_redirects=False)
        response.raise_for_status()
        if ext in {".yml", ".yaml"}:
            return yaml.load(response.text, Loader=yaml.SafeLoader)
        if ext == ".json":
            return response.json()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        detail = exc.response.reason if exc.response is not None else str(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    raise HTTPException(status_code=422, detail="Invalid filetype")


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
        # Opens the JSON and iterate over the content.
        _template = models.Template(title=template.title, url=template.url)
        loaded_file = _load_template_data(template.url)
        if isinstance(loaded_file, list):
            for entry in loaded_file:
                ports = conv_ports2dict(entry.get("ports", []))
                sysctls = conv_sysctls2dict(entry.get("sysctls", []))
                template_content = models.TemplateItem(
                    type=int(entry.get("type", 1)),
                    title=entry["title"],
                    platform=entry["platform"],
                    description=entry.get("description", ""),
                    name=entry.get("name", entry["title"].lower()),
                    command=entry.get("command"),
                    logo=entry.get("logo", ""),
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
        elif isinstance(loaded_file, dict):
            entry = loaded_file
            ports = conv_ports2dict(entry.get("ports", []))
            sysctls = conv_sysctls2dict(entry.get("sysctls", []))

            template_content = models.TemplateItem(
                type=int(entry.get("type", 1)),
                title=entry["title"],
                platform=entry["platform"],
                description=entry.get("description", ""),
                name=entry.get("name", entry["title"].lower()),
                command=entry.get("command"),
                logo=entry.get("logo", ""),
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
        else:
            raise HTTPException(status_code=422, detail="Invalid template format")
    except KeyError as err:
        print("data request failed", err)
        raise HTTPException(status_code=422, detail=f"Missing template key: {err}") from err

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

    items = []
    try:
        loaded_file = _load_template_data(template.url)
        if isinstance(loaded_file, list):
            for entry in loaded_file:
                ports = conv_ports2dict(entry.get("ports", []))
                sysctls = conv_sysctls2dict(entry.get("sysctls", []))

                item = models.TemplateItem(
                    type=int(entry["type"]),
                    title=entry["title"],
                    platform=entry["platform"],
                    description=entry.get("description", ""),
                    name=entry.get("name", entry["title"].lower()),
                    command=entry.get("command"),
                    logo=entry.get("logo", ""),
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
        elif isinstance(loaded_file, dict):
            entry = loaded_file
            ports = conv_ports2dict(entry.get("ports", []))
            sysctls = conv_sysctls2dict(entry.get("sysctls", []))

            template_content = models.TemplateItem(
                type=int(entry["type"]),
                title=entry["title"],
                platform=entry["platform"],
                description=entry.get("description", ""),
                name=entry.get("name", entry["title"].lower()),
                command=entry.get("command"),
                logo=entry.get("logo", ""),
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
        else:
            raise HTTPException(status_code=422, detail="Invalid template format")
    except KeyError as exc:
        print("Template update failed. ERR_001", exc)
        raise HTTPException(status_code=422, detail=f"Missing template key: {exc}") from exc
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
            raise HTTPException(status_code=500, detail="Template update failed") from exc

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

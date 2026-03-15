from datetime import datetime

from fastapi import HTTPException

from api.db.models.hosts import Host


def get_hosts(db):
    return db.query(Host).order_by(Host.name.asc()).all()


def get_host(db, host_id):
    host = db.query(Host).filter(Host.id == host_id).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Host not found.")
    return host


def get_default_host(db):
    host = db.query(Host).filter(Host.is_default == True).first()
    if host is None:
        raise HTTPException(status_code=404, detail="Default host not found.")
    return host


def set_default_host(db, host):
    db.query(Host).filter(Host.is_default == True).update({"is_default": False})
    host.is_default = True
    host.updated_at = datetime.utcnow()
    db.add(host)
    db.commit()
    db.refresh(host)
    return host


def ensure_local_host(db):
    host = db.query(Host).filter(Host.connection_type == "local").first()
    default_host = db.query(Host).filter(Host.is_default == True).first()
    if host is None:
        host = Host(
            name="local",
            connection_type="local",
            is_active=True,
            is_default=default_host is None,
            last_seen=datetime.utcnow(),
        )
        db.add(host)
        db.commit()
        db.refresh(host)
        return host

    host.last_seen = datetime.utcnow()
    if default_host is None:
        host.is_default = True
    db.add(host)
    db.commit()
    db.refresh(host)
    return host


def create_host(db, host_create):
    existing = db.query(Host).filter(Host.name == host_create.name).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Host name already exists.")

    if host_create.connection_type not in {"docker_api"}:
        raise HTTPException(
            status_code=400,
            detail="Only docker_api hosts can be created manually in this version.",
        )

    if not host_create.docker_host:
        raise HTTPException(
            status_code=400, detail="docker_host is required for docker_api hosts."
        )

    host = Host(
        name=host_create.name,
        connection_type=host_create.connection_type,
        docker_host=host_create.docker_host,
        is_active=True,
        is_default=host_create.is_default,
        last_seen=datetime.utcnow(),
    )
    db.add(host)
    db.commit()
    db.refresh(host)
    if host_create.is_default:
        host = set_default_host(db, host)
    return host

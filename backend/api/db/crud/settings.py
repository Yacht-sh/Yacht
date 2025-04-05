from sqlalchemy.orm import Session

from api.db.models import containers as models
from api.db.models.settings import SecretKey
from datetime import datetime
from api.settings import Settings
import json

settings = Settings()


def export_settings(db: Session):
    file_export = {}
    file_export["templates"] = db.query(models.Template).all()
    file_export["variables"] = db.query(models.TemplateVariables).all()
    return file_export


def get_secret_key(db: Session):
    check = db.query(models.SecretKey).first()
    if check:
        return True
    else:
        return False


def generate_secret_key(db: Session):
    check = db.query(SecretKey).first()
    if check is None:
        key = SecretKey(key=settings.SECRET_KEY)
        db.add(key)
        db.commit()
        print("Secret key generated")
        return key.key
    else:
        print("Secret key exists")
        return check.key


def import_settings(db: Session, upload):
    import_file = upload.file.read()
    decoded_import = import_file.decode("utf-8")
    import_contents = json.loads(decoded_import)

    _templates = import_contents["templates"]
    _variables = import_contents["variables"]

    _template_list = []
    _var_list = []

    for template in _templates:
        template_model = models.Template(
            id=template["id"],
            title=template["title"],
            url=template["url"],
            updated_at=datetime.fromisoformat(template["updated_at"]),
            created_at=datetime.fromisoformat(template["created_at"]),
        )
        for item in template["items"]:
            _item = models.TemplateItem(**item)
            template_model.items.append(_item)
        _template_list.append(template_model)

    for variable in _variables:
        variable_model = models.TemplateVariables(**variable)
        _var_list.append(variable_model)

    # Remove Existing
    db.query(models.TemplateVariables).delete()
    db.query(models.Template).delete()
    db.query(models.TemplateItem).delete()

    # Add New
    db.add_all(_template_list)
    db.add_all(_var_list)
    db.commit()
    response = {"success": "Import Successful"}
    return response

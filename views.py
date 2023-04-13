from flask import Blueprint, request, abort, current_app
from functools import wraps
from werkzeug.utils import secure_filename
import os
import datetime
import re
from .models import User, Site, Subject, Gallery, Photo
from .exts import db


bp = Blueprint("views", __name__)

ALLOWED_EXTENSIONS = ["gif", "jpg", "jpeg", "png"]


def mes_404(res, id):
    return f"The {res} with the given id ({id}) doesn't exist"


def unique_filename(filename):
    return str(datetime.datetime.now().date()) + '_' + str(datetime.datetime.now().time()).replace(':', '.')+"_"+filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "source" not in request.json and "source" not in request.form:
            abort(400, "The source object is required in request json")
        user_id = request.json["source"]["user_id"]
        site = \
            User.query\
            .get_or_404(user_id, mes_404("user", user_id))\
            .sites\
            .filter(Site.id == kwargs["site_id"])\
            .first()
        if not site:
            abort(403, f"The user with id ({user_id}) is not allowed to access that site")
        return f(*args, **kwargs)
    return decorated


@bp.route("/ping")
def ping_api_get():
    """
    [Public] Odbija request w celu sprawdzenia działania api
    """
    return '', 200


@bp.route("/site/<int:site_id>/module/gallery", methods=["GET"])
@check_user
def gallery_get_list(site_id):
    """
    [User] Podaje listę albumów w galerii z paginacją
    """
    paginate = request.json["paginate"]
    key = getattr(Gallery, paginate["order"] if paginate["order"] else "sort")
    key = key.desc() if paginate["order_desc"] else key.asc()

    galleries = \
        Gallery.query\
        .filter_by(site_id=site_id)\
        .order_by(key)\
        .paginate(page=paginate["page"], per_page=paginate["per_page"], error_out=False)

    pagination = {
            "page": galleries.page,
            "pages": galleries.pages,
            "per_page": galleries.per_page,
            "total": galleries.total
            }
    galleries = [x.as_dict() for x in galleries]
    return {"pagination": pagination, "data": galleries}, 200


@bp.route("/site/<int:site_id>/module/gallery", methods=["POST"])
@check_user
def gallery_add(site_id):
    """
    [User] Dodaje album do galerii
    """
    site = \
        Site.query\
        .get_or_404(site_id, description=mes_404("site", site_id))
    payload = request.json["payload"]
    gallery = Gallery(
            name=payload["name"],
            description=payload["description"],
            )
    site.galleries.append(gallery)
    db.session.commit()
    db.session.refresh(gallery)
    return {"gallery_id": gallery.id}, 201


@bp.route("/site/<int:site_id>/module/gallery", methods=["OPTIONS"])
@check_user
def gallery_get_options(site_id):
    """
    [User] Podaje opcje galerii
    """
    return '', 200


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>", methods=["GET"])
@check_user
def gallery_get_one(site_id, gallery_id):
    """
    [User] Podaje dane galerii i zdjęcia
    """
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    result = {"data": gallery.as_dict()}
    return result, 200


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>", methods=["POST"])
@check_user
def gallery_photo_upload(site_id, gallery_id):
    """
    [User] Dodaje zdjęcie do albumu
    """
    if 'file' not in request.files:
        abort(400, "The file was not provided")
    file = request.files['file']
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    if file.filename == '':
        abort(500, description="Filename must be provided")
    if not allowed_file(file.filename):
        abort(400, "Only jpg, jpeg, gif and png files are allowed")

    filename = secure_filename(file.filename)
    filename = unique_filename(filename)
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

    description = request.form['description']

    photo = Photo(
            filename=filename,
            description=description,
            sort=1
            )
    gallery.photos.append(photo)
    db.session.commit()
    db.session.refresh(photo)

    return {"photo_id": photo.id}, 200


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>", methods=["PUT"])
@check_user
def gallery_change(site_id, gallery_id):
    """
    [User] Aktualizuje nazwę i opis albumu
    """
    payload = request.json["payload"]
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    gallery.name = payload["name"]
    gallery.description = payload["description"]
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>", methods=["DELETE"])
@check_user
def gallery_delete(site_id, gallery_id):
    """
    [User] Usuwa album z galerii
    """
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    db.session.delete(gallery)
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/move_up", methods=["PUT"])
@check_user
def gallery_move_up(site_id, gallery_id):
    """
    [User] Przesuwa album na liście w górę
    """
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    gallery.sort += 1
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/move_down", methods=["PUT"])
@check_user
def gallery_move_down(site_id, gallery_id):
    """
    [User] Przesuwa album na liście w dół
    """
    gallery = \
        Gallery.query\
        .filter_by(site_id=site_id, id=gallery_id)\
        .first_or_404(mes_404("gallery", gallery_id))
    gallery.sort = max(gallery.sort-1, 1)
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photos/update", methods=["PUT"])
@check_user
def gallery_photos_update(site_id, gallery_id):
    """
    [User] Aktualizuje informacje listy zdjęć
    """
    for p in request.json["photos"]:
        photo = \
            Photo.query\
            .filter_by(gallery_id=gallery_id, id=p["id"])\
            .first()
        if photo:
            photo.description = p["description"]

    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photo/<int:photo_id>", methods=["PUT"])
def gallery_photo_reupload(site_id, gallery_id, photo_id):
    """
    [User] Reaploaduje zdjęcie
    """
    if 'file' not in request.files:
        abort(400, "The file was not provided")
    photo = \
        Photo.query\
        .filter_by(gallery_id=gallery_id, id=photo_id)\
        .first_or_404(mes_404("photo", photo_id))
    file = request.files['file']
    filename = file.filename
    if filename == '':
        abort(500, description="Filename must be provided")
    if not allowed_file(filename):
        abort(400, "Only jpg, jpeg, gif and png files are allowed")
    filename = secure_filename(filename)
    filename = unique_filename(filename)

    try:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], photo.filename))
    except FileNotFoundError:
        pass
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

    photo.filename = filename
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photo/<int:photo_id>", methods=["DELETE"])
@check_user
def gallery_photo_delete(site_id, gallery_id, photo_id):
    """
    [User] Usuwa zdjęcie z albumu
    """
    photo = \
        Photo.query\
        .filter_by(gallery_id=gallery_id, id=photo_id)\
        .first_or_404(mes_404("photo", photo_id))
    db.session.delete(photo)
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photo/<int:photo_id>/update", methods=["PUT"])
@check_user
def gallery_photo_update(site_id, gallery_id, photo_id):
    """
    [User] Aktualizuje informacje zdjęcia
    """
    description = request.json["payload"]["description"]
    photo = \
        Photo.query\
        .filter_by(gallery_id=gallery_id, id=photo_id)\
        .first_or_404(mes_404("photo", photo_id))
    photo.description = description
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photo/<int:photo_id>/move_up", methods=["PUT"])
@check_user
def gallery_photo_move_up(site_id, gallery_id, photo_id):
    """
    [User] Przesuwa zdjęcie na liście w górę
    """
    photo = \
        Photo.query\
        .filter_by(gallery_id=gallery_id, id=photo_id)\
        .first_or_404(mes_404("photo", photo_id))
    photo.sort += 1
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/gallery/<int:gallery_id>/photo/<int:photo_id>/move_down", methods=["PUT"])
@check_user
def gallery_photo_move_down(site_id, gallery_id, photo_id):
    """
    [User] Przesuwa zdjęcie na liście w dół
    """
    photo = \
        Photo.query\
        .filter_by(gallery_id=gallery_id, id=photo_id)\
        .first_or_404(mes_404("photo", photo_id))
    photo.sort = max(photo.sort-1, 1)
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/subject", methods=["GET"])
@check_user
def subjects_get_list(site_id):
    """
    [User] Podaje listę tematyk strony
    """
    subjects = \
        Site.query\
        .get(site_id)\
        .subjects
    result = [x.as_dict() for x in subjects]
    return result, 200


@bp.route("/site/<int:site_id>/module/subject", methods=["POST"])
@check_user
def subjects_add(site_id):
    """
    [User] Dodaje tematykę do strony
    """
    site = Site.query.get(site_id)
    subject = request.json["payload"]["subject"]

    if len(subject) == 0 or len(subject) > 64:
        abort(400, "The subject length should be beetween 1 and 64")

    new_subject = Subject(subject=subject)
    site.subjects.append(new_subject)
    db.session.commit()

    return '', 201


@bp.route("/site/<int:site_id>/module/subject/<int:subject_id>", methods=["GET"])
@check_user
def subjects_get_one(site_id, subject_id):
    """
    [User] Podaje tematykę o określonym id
    """
    subject = \
        Site.query\
        .get(site_id)\
        .subjects\
        .filter(Subject.id == subject_id)\
        .first_or_404(mes_404("subject", subject_id))

    return subject.as_dict(), 200


@bp.route("/site/<int:site_id>/module/subject/<int:subject_id>", methods=["PUT"])
@check_user
def subjects_change(site_id, subject_id):
    """
    [User] Aktualizuje tematykę
    """
    subject = \
        Site.query\
        .get(site_id)\
        .subjects\
        .filter(Subject.id == subject_id)\
        .first_or_404(mes_404("subject", subject_id))

    subject.subject = request.json["payload"]["subject"]
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/subject/<int:subject_id>", methods=["DELETE"])
@check_user
def subjects_delete(site_id, subject_id):
    """
    [User] Usuwa tematykę
    """
    site = \
        Site.query\
        .get(site_id)
    subject = \
        site.subjects\
        .filter(Subject.id == subject_id)\
        .first_or_404(mes_404("subject", subject_id))
    
    site.subjects.remove(subject)
    db.session.commit()
    return '', 204


@bp.route("/site/<int:site_id>/module/subject/<string:row_prefix>", methods=["GET"])
@check_user
def subject_prefix_row_get_list(site_id, row_prefix):
    """
    [User] Podaje listę tematyk strony dla danego prefixu i rekordu
    """
    subjects = \
        Site.query\
        .get(site_id)\
        .subjects\
        .filter(Subject.subject.startswith(row_prefix))\
        .all()
    subjects = [{"id": x.id} for x in subjects]
    return subjects, 200

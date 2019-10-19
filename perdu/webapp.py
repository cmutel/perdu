from . import (
    search_gs1,
    search_corrector_gs1,
    search_naics,
    search_corrector_naics,
    base_dir,
    File,
)
from .ingestion import mapping
from flask import (
    abort,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    Response,
    send_file,
    url_for,
    jsonify,
    json
)
from peewee import DoesNotExist, IntegrityError
from werkzeug.utils import secure_filename

perdu_app = Flask(
    "perdu_app", static_folder="perdu/assets/", template_folder="perdu/assets/templates"
)

import os

UPLOAD_FOLDER = base_dir / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"xml", "spold", "csv"}

# Default limit for file uploads is 5 MB
perdu_app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
perdu_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Generate a secret key for the session, otherwise flash() returns an exception
perdu_app.config["SECRET_KEY"] = os.urandom(24)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


search_mapping = {"naics": search_naics, "gs1": search_gs1}
corrector_mapping = {"naics": search_corrector_naics, "gs1": search_corrector_gs1}


@perdu_app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", title="Perdu index page")


@perdu_app.route("/search", methods=["GET"])
def search():
    catalogue = request.args.get("catalogue")
    search_term = request.args.get("search_term")
    if not catalogue:
        catalogue = list(search_mapping)[0]

    if catalogue not in search_mapping:
        abort(404)

    if not search_term:
        return render_template(
            "search.html",
            title="Perdu search",
            catalogues=search_mapping,
            catalogue=catalogue,
        )
    else:
        search_results = search_mapping[catalogue](search_term, limit=5)

        if len(search_term.split(" ")) == 1 and len(search_results) < 5:
            correction_results = corrector_mapping[catalogue](search_term)[0]
        else:
            correction_results = []

        if catalogue == "gs1":
            for obj in search_results:
                obj["name"] = obj.pop("brick")

        return render_template(
            "search_result.html",
            title="Perdu search result",
            results=search_results,
            corrections=correction_results,
            search_term=search_term,
            catalogue=catalogue,
        )


@perdu_app.route("/file/<hash>/selection", methods=["POST"])
def selection_made(hash):
    d = json.loads(request.form['json'])
    item_to_match = d['item to match']
    selection = d['match']
    return ""


@perdu_app.route("/file/<hash>", methods=["GET"])
def uploaded_file(hash):
    try:
        file = File.get(sha256=hash)
    except DoesNotExist:
        raise (404)
    data = mapping[file.kind](file.filepath)
    return render_template(
        "file.html", title="File: {}".format(file.name), filename=file.name, data=data
    )


@perdu_app.route("/upload", methods=["POST"])
def upload():

    # check if the post request has the file part
    if "file_upload" not in request.files:
        abort(400)
    file = request.files["file_upload"]

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))
    if file and allowed_file(file.filename):

        filename = secure_filename(file.filename)
        # If the file has already been uploaded once, peewee will throw an IntegrityError exception because the
        # entry is already in the DB
        try:
            file.save(str(UPLOAD_FOLDER / filename))
            file_row = File.create(
                name=filename, filepath=UPLOAD_FOLDER / filename, kind="csv"
            )
        except IntegrityError:
            file_row = File.get(name=filename)
            return redirect(url_for("uploaded_file", hash=file_row.sha256))

        return redirect(url_for("uploaded_file", hash=file_row.sha256))
    else:
        flash("The extension of the file provided may be wrong")
        return redirect(url_for("index"))

@perdu_app.route("/get_search_results/<catalogue>/<item_to_search_for>")
def get_search_results(catalogue, item_to_search_for):

    if catalogue == "gs1":
        data = [[results[d] for d in results
                 if d in ('brick', 'definition', 'family')]
                for results in search_gs1(item_to_search_for)]
    elif catalogue == "naics":
        data = [[results[d] for d in results
                 if d in ('brick', 'definition', 'family')]
                for results in search_naics(item_to_search_for)]
    else:
        data = [[results[d] for d in results
         if d in ('brick', 'definition', 'family')]
        for results in search_gs1(item_to_search_for)]

        data.extend([[results[d] for d in results
                 if d in ('brick', 'definition', 'family')]
                for results in search_naics(item_to_search_for)])

    return jsonify(data)

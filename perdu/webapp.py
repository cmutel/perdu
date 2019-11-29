from . import (
    base_dir,
    export_dir,
    File,
    search_corrector_gs1,
    search_corrector_naics,
    search_corrector_useeio,
    search_gs1,
    search_gs1_disjoint,
    search_naics,
    search_naics_disjoint,
    search_useeio,
    search_useeio_disjoint,
)
from .ingestion import mapping
from .semantic_web import write_matching_to_rdf
from .export_generic import write_matching_to_csv_dataframe
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
    json,
)
import hashlib
from pathlib import Path
from peewee import DoesNotExist
from werkzeug.utils import secure_filename
import os


perdu_app = Flask(
    "perdu_app", static_folder="perdu/assets/", template_folder="perdu/assets/templates"
)


UPLOAD_FOLDER = base_dir / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    # "xml",
    # "spold",
    "csv",
    "xlsx",
    "xls",
    "zip",
}

# Default limit for file uploads is 5 MB
perdu_app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
perdu_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Generate a secret key for the session, otherwise flash() returns an exception
perdu_app.config["SECRET_KEY"] = os.urandom(24)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# search_mapping = {"naics": search_naics_disjoint, "gs1": search_gs1_disjoint, 'useeio': search_useeio_disjoint}
search_mapping = {"naics": search_naics, "gs1": search_gs1, "useeio": search_useeio}
corrector_mapping = {
    "naics": search_corrector_naics,
    "gs1": search_corrector_gs1,
    "useeio": search_corrector_useeio,
}
file_kind_mapping = {"csv": "csv", "xlsx": "bom", "xls": "bom", "zip": "jsonld"}


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


@perdu_app.route("/export/<method>", methods=["POST"])
def export_linked_data(method):
    content = request.get_json()

    if method == "ttl":
        fp = write_matching_to_rdf(content)
    elif method == "jsonld":
        fp = write_matching_to_rdf(content, "json-ld", "json")
    elif method == "csv":
        fp = write_matching_to_csv_dataframe(content)
    return jsonify({"fp": fp.name})


@perdu_app.route("/download/<path>", methods=["GET"])
def download_export(path):
    fp = export_dir / path
    return send_file(fp, as_attachment=True)


@perdu_app.route("/file/<hash>", methods=["GET"])
def uploaded_file(hash):
    try:
        file = File.get(sha256=hash)
    except DoesNotExist:
        raise (404)
    data = mapping[file.kind](file.filepath)
    return render_template(
        "file.html",
        title="File: {}".format(file.name),
        filename=file.name,
        data=data,
        catalogues=list(search_mapping),
        hash=hash,
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
        filehash = hashlib.sha256(file.read()).hexdigest()

        try:
            file_obj = File.get(sha256=filehash)
            return redirect(url_for("uploaded_file", hash=file_obj.sha256))
        except DoesNotExist:
            file.seek(0)
            filename = secure_filename(file.filename)
            fn_path = Path(filename)
            stem, suffix = fn_path.stem, fn_path.suffix
            shorthash = filehash[:12]
            filename = f"{stem}.{shorthash}{suffix}"
            file.save(str(UPLOAD_FOLDER / filename))

            file_obj = File.create(
                name=filename,
                filepath=UPLOAD_FOLDER / filename,
                kind=file_kind_mapping[suffix[1:]],
                sha256=filehash,
            )
            return redirect(url_for("uploaded_file", hash=file_obj.sha256))
    else:
        flash("The extension of the file provided may be wrong")
        return redirect(url_for("index"))


def normalize_search_results(result):
    if "brick" in result:
        return {
            "description": result.pop("definition"),
            "name": result.pop("brick"),
            "class": result.pop("klass"),
        }
    else:
        return result


@perdu_app.route("/get_search_results/<catalog>/<query>")
def get_search_results(catalog, query):
    search_function = search_mapping[catalog]
    results = [normalize_search_results(o) for o in search_function(query)]
    return jsonify(results)

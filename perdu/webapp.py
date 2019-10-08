# -*- coding: utf-8 -*-
from . import (
    search_gs1,
    search_corrector_gs1,
    search_naics,
    search_corrector_naics,

)
from flask import (
    abort,
    Flask,
    render_template,
    request,
    Response,
    send_file,
    url_for,
    redirect,
)
from copy import deepcopy


perdu_app = Flask(
    "perdu_app",
    static_folder="perdu/assets/",
    template_folder="perdu/assets/templates"
)

# Default limit for file uploads is 5 MB
perdu_app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


search_mapping = {
    'naics': search_naics,
    'gs1': search_gs1,
}
corrector_mapping = {
    'naics': search_corrector_naics,
    'gs1': search_corrector_gs1,
}


@perdu_app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title="Perdu index page")


@perdu_app.route('/search', methods=['GET'])
def search():
    catalogue = request.args.get('catalogue')
    search_term = request.args.get('search_term')
    if not catalogue:
        catalogue = list(search_mapping)[0]

    if catalogue not in search_mapping:
        abort(404)

    if not search_term:
        return render_template('search.html',
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
                obj['name'] = obj.pop('brick')

        return render_template('search_result.html',
                               title="Perdu search result",
                               results=search_results,
                               corrections=correction_results,
                               search_term=search_term,
                               catalogue=catalogue,
                               )

@perdu_app.route('/upload', methods=['POST'])
def upload():
    return

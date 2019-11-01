from .filesystem import export_dir
from rdflib import Literal, RDF, URIRef, Namespace, Graph
from rdflib.namespace import DC, RDFS, OWL, SKOS


verb_mapping = {
    "exact": OWL.sameAs,
    "approximate": SKOS.related,
    "narrower": SKOS.narrower,
    "broader": SKOS.broader,
}


def write_matching_to_rdf(data, format="turtle", extension="ttl"):
    g = Graph()

    olca = Namespace("http://greendelta.github.io/olca-schema/context.jsonld#")

    g.bind("olca", "http://greendelta.github.io/olca-schema/context.jsonld")
    g.bind("dc", DC)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)

    olca_object = olca.Flow if data["catalog"] == "gs1" else olca.Process

    # Start by describing what we are linking against (only those elements used)
    node_dict = {}
    for key in (key for key in data if key.startswith("row-")):
        for o in data[key]["matches"]:
            match = o["data"]
            if match["code"] not in node_dict:
                uri = "http://perdu.data/{}/{}".format(data["catalog"], match["code"])
                node = URIRef(uri)
                g.add((node, RDF.type, olca_object))
                g.add((node, DC.title, Literal(match["name"])))
                g.add((node, RDFS.label, Literal(match["name"])))
                g.add((node, DC.description, Literal(match["description"])))
                node_dict[match["code"]] = node

    # Now describe our links
    for key in (key for key in data if key.startswith("row-")):
        uri = "http://perdu.data/source/{}/{}".format(data["hash"], key.replace("row-", ""))
        node = URIRef(uri)
        g.add((node, RDF.type, olca.Flow))
        g.add((node, RDFS.label, Literal(data[key]["source"])))
        g.add((node, DC.publisher, Literal("perdu.data")))
        g.add((node, DC.creator, URIRef("https://github.com/cmutel/perdu")))
        for match in data[key]["matches"]:
            g.add(
                (node, verb_mapping[match["method"]], node_dict[match["data"]["code"]])
            )

    fp = export_dir / "{}.{}.{}".format(data["hash"], data["catalog"], extension)
    if fp.is_file():
        fp.unlink()

    with open(fp, "wb") as f:
        g.serialize(f, format=format, encoding="utf-8")
    return fp

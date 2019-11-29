import pandas as pd
from .filesystem import export_dir

match = {"approximate": "~", "broader": ">", "narrower": "<", "exact": "="}


def write_matching_to_csv_dataframe(data):
    """Create a dataframe CSV inspired by https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List/blob/master/format%20specs/FlowMapping.md."""
    is_row = lambda x: x.startswith("row-")
    reformatted = []

    for key in filter(is_row, data):
        for elem in data[key]["matches"]:
            reformatted.append(
                {
                    "TargetListName": data["catalog"],
                    "TargetFlowName": elem["data"]["name"],
                    "TargetFlowClass": elem["data"].get("class"),
                    "TargetFlowDescription": elem["data"].get("description"),
                    "SourceFlowName": data[key]["source"],
                    "MatchCondition": match[elem["method"]],
                }
            )

    fp = export_dir / "{}.{}.csv".format(data["hash"], data["catalog"])
    if fp.is_file():
        fp.unlink()

    df = pd.DataFrame(reformatted)
    df.to_csv(fp, index=False)
    return fp

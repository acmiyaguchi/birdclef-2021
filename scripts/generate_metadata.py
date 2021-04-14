import pandas as pd
import json
from pathlib import Path
import tqdm

ROOT = Path(__file__).parent.parent


def write_info(df, output):
    for row in (
        df[["primary_label", "scientific_name", "common_name"]]
        .drop_duplicates()
        .to_dict(orient="records")
    ):
        p = output / row["primary_label"]
        p.mkdir(exist_ok=True)
        (p / "info.json").write_text(json.dumps(row))


def write_metadata(df, output):
    fields = [
        "name",
        "secondary_labels",
        "type",
        "date",
        "latitude",
        "longitude",
        "rating",
        "url",
    ]
    df["name"] = df.filename.str.rstrip(".ogg")

    for label in tqdm.tqdm(df.primary_label.drop_duplicates()):
        p = output / label
        p.mkdir(exist_ok=True)
        res = []
        for row in df[df.primary_label == label][fields].to_dict(orient="records"):
            for i in ["secondary_labels", "type"]:
                row[i] = eval(row[i])
            res.append(row)
        (p / "metadata.json").write_text(json.dumps(res, indent=2))


def main():
    df = pd.read_csv(f"{ROOT}/data/input/train_metadata.csv")
    output = Path(f"{ROOT}/data/metadata")
    output.mkdir(exist_ok=True, parents=True)
    write_info(df, output)
    write_metadata(df, output)


if __name__ == "__main__":
    main()

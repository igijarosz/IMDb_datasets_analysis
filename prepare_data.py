import pandas as pd
import os


def prepare_movies_data():
    # -------- SETTINGS --------
    CHUNK_SIZE = 200_000

    OUTPUT_DIR = "processed_data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    OUTPUT_MOVIES = f"{OUTPUT_DIR}/movies_processed.csv"

    # -------- CLEAN FILE --------
    if os.path.exists(OUTPUT_MOVIES):
        os.remove(OUTPUT_MOVIES)

    # -------- LOAD NAMES --------
    print("\nLoading names...")

    names_df = pd.read_csv(
        "raw_data/name.basics.tsv",
        sep="\t",
        dtype=str,
        keep_default_na=False
    )

    names_df = names_df.replace("\\N", pd.NA).dropna(subset=["primaryName"])
    name_map = dict(zip(names_df["nconst"], names_df["primaryName"]))
    del names_df

    # -------- LOAD RATINGS --------
    print("Loading ratings...")

    ratings_df = pd.read_csv(
        "raw_data/title.ratings.tsv",
        sep="\t",
        dtype=str,
        keep_default_na=False
    )

    ratings_df = ratings_df.replace("\\N", pd.NA)
    ratings_df["averageRating"] = pd.to_numeric(ratings_df["averageRating"], errors="coerce")
    ratings_df["numVotes"] = pd.to_numeric(ratings_df["numVotes"], errors="coerce")
    ratings_df = ratings_df.drop_duplicates("tconst")

    # -------- LOAD CREW --------
    print("Loading crew...")

    crew_df = pd.read_csv(
        "raw_data/title.crew.tsv",
        sep="\t",
        dtype=str,
        keep_default_na=False
    )

    crew_df = crew_df.replace("\\N", pd.NA).drop_duplicates("tconst")

    # -------- NAME MAP --------
    def map_names(nconst_list):
        if pd.isna(nconst_list):
            return None

        names = []
        for n in str(nconst_list).split(","):
            name = name_map.get(n)
            names.append(str(name) if pd.notna(name) else n)

        return ", ".join(names)

    # -------- PROCESS --------
    print("\nProcessing MOVIES only...")

    file_exists = False
    processed_total = 0
    written_movies = 0

    for chunk in pd.read_csv(
            "raw_data/title.basics.tsv",
            sep="\t",
            chunksize=CHUNK_SIZE,
            dtype=str,
            keep_default_na=False
    ):

        processed_total += len(chunk)

        chunk = chunk.replace("\\N", pd.NA)

        # FILTER MOVIES
        chunk = chunk[chunk["titleType"] == "movie"]

        if chunk.empty:
            continue

        chunk["startYear"] = pd.to_numeric(chunk["startYear"], errors="coerce").astype("Int16")
        chunk = chunk.merge(ratings_df, on="tconst", how="left")
        chunk = chunk.merge(crew_df, on="tconst", how="left")
        chunk["directors"] = chunk["directors"].apply(map_names)
        chunk["writers"] = chunk["writers"].apply(map_names)

        # COLUMNS
        chunk = chunk[
            [
                "tconst",
                "primaryTitle",
                "directors",
                "writers",
                "runtimeMinutes",
                "genres",
                "startYear",
                "averageRating",
                "numVotes",
            ]
        ]

        chunk.to_csv(
            OUTPUT_MOVIES,
            mode="a",
            header=not file_exists,
            index=False
        )
        file_exists = True

        written_movies += len(chunk)

        print(f"Processed: {processed_total} | Movies: {written_movies}")

    print("\nDONE")
    print(f"Total movies written: {written_movies}")


if __name__ == "__main__":
    prepare_movies_data()
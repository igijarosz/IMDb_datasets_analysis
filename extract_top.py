import pandas as pd
import os

def extract_top_movies():
    # -------- SETTINGS --------
    m = 25000
    input_file = "processed_data/movies_processed.csv"
    output_file = "processed_data/top_1000_movies.csv"

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Missing input file: {input_file}")

    # -------- LOAD DATA --------
    df = pd.read_csv(input_file)

    df["averageRating"] = pd.to_numeric(df["averageRating"], errors="coerce")
    df["numVotes"] = pd.to_numeric(df["numVotes"], errors="coerce")

    df = df.dropna(subset=["averageRating", "numVotes"])

    # -------- PARAMETERS --------
    C = df["averageRating"].mean()

    print(f"\nGlobal mean (C): {C:.3f}")
    print(f"Vote threshold (m): {m}")

    # -------- WEIGHTED SCORE --------
    v = df["numVotes"]
    R = df["averageRating"]

    df["weightedScore"] = (v / (v + m)) * R + (m / (v + m)) * C

    # -------- FILTER --------
    df = df[df["numVotes"] >= m]

    # -------- TOP 1000 --------
    top_1000 = (
        df.sort_values("weightedScore", ascending=False)
        .head(1000)
    )

    # -------- SAVE --------
    top_1000.to_csv(output_file, index=False)

    print("\nDONE")
    print(f"Saved: {output_file}")
    print(f"Rows: {len(top_1000)}")

if __name__ == "__main__":
    extract_top_movies()
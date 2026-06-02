import os
import sys

from download_data import download_and_unpack
from prepare_data import prepare_movies_data
from extract_top import extract_top_movies
from data_analysis import (
    load_data,
    analyze_rating_distribution,
    analyze_runtime_distribution,
    analyze_genre,
    analyze_golden_age,
    analyze_popularity_vs_rating,
    analyze_directors_ranking,
    run_all_analyses
)

# -------- SETTINGS --------
PROCESSED_FILE = "processed_data/movies_processed.csv"
TOP_1000_FILE = "processed_data/top_1000_movies.csv"


def download_and_process_flow():
    if os.path.exists(PROCESSED_FILE):
        print(f"\nWarning: Processed data detected at '{PROCESSED_FILE}'.")
        choice = input("Proceed to download and process again? (y/n): ").strip().lower()
        if choice != 'y':
            print("Aborting download and process step.")
            return

    print("\n=== Starting Data Pipeline ===")
    download_and_unpack()
    prepare_movies_data()
    extract_top_movies()
    print("\n=== Data Pipeline Complete ===")


def analysis_flow():
    if not os.path.exists(PROCESSED_FILE):
        print(f"\nError: '{PROCESSED_FILE}' not found. Please run Option 1 first.")
        return

    # -------- SELECT DATASET --------
    print("\nWhich dataset would you like to analyze?")
    print("1. All Processed Movies")
    print("2. Top 1000 Movies")
    data_choice = input("Select an option (1-2): ").strip()

    if data_choice == '1':
        file_path = PROCESSED_FILE
        output_dir = "analysis/charts/charts_all_movies"
    elif data_choice == '2':
        if not os.path.exists(TOP_1000_FILE):
            print("Top 1000 file missing. Did the extraction step run successfully?")
            return
        file_path = TOP_1000_FILE
        output_dir = "analysis/charts/charts_top_1000_movies"
    else:
        print("Invalid choice. Returning to main menu.")
        return

    # -------- SELECT ANALYSIS --------
    print("\nWhich analysis would you like to run?")
    print("1. Rating Distribution")
    print("2. Runtime Distribution")
    print("3. Genre Analysis")
    print("4. Average Rating by Decade")
    print("5. Popularity vs. Rating")
    print("6. Directors Ranking")
    print("7. Run All Analyses")

    analysis_choice = input("Select an option (1-7): ").strip()

    print(f"\n=== Starting Analysis ===")

    os.makedirs(output_dir, exist_ok=True)

    if analysis_choice == '7':
        run_all_analyses(file_path, output_dir)
        print(f"=== Analysis Complete ===")
        return

    print(f"Loading data from {file_path}...")
    df = load_data(file_path)

    if analysis_choice == '1':
        analyze_rating_distribution(df, output_dir)
        print(f"Saved Rating Distribution to {output_dir}")
    elif analysis_choice == '2':
        analyze_runtime_distribution(df, output_dir)
        print(f"Saved Runtime Distribution to {output_dir}")
    elif analysis_choice == '3':
        analyze_genre(df, output_dir)
        print(f"Saved Genre Analysis to {output_dir}")
    elif analysis_choice == '4':
        analyze_golden_age(df, output_dir)
        print(f"Saved Decade Ratings to {output_dir}")
    elif analysis_choice == '5':
        analyze_popularity_vs_rating(df, output_dir)
        print(f"Saved Popularity vs Rating to {output_dir}")
    elif analysis_choice == '6':
        analyze_directors_ranking(df)
        print("Printed Directors Ranking to terminal.")
    else:
        print("Invalid choice. Returning to main menu.")
        return

    print(f"=== Analysis Complete ===")


def main():
    while True:
        print("\n" + "=" * 35)
        print("    IMDb Data Pipeline Menu")
        print("=" * 35)
        print("1. Download and Process Data")
        print("2. Run Data Analysis")
        print("3. Exit")
        print("=" * 35)

        choice = input("Select an option (1-3): ").strip()

        if choice == '1':
            download_and_process_flow()
        elif choice == '2':
            analysis_flow()
        elif choice == '3':
            print("Exiting pipeline.")
            sys.exit(0)
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
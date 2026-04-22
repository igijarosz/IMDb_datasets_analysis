import os
import gzip
import shutil
import requests

# -------- CONFIGURATION --------
DATASETS = [
    "https://datasets.imdbws.com/name.basics.tsv.gz",
    "https://datasets.imdbws.com/title.basics.tsv.gz",
    "https://datasets.imdbws.com/title.crew.tsv.gz",
    "https://datasets.imdbws.com/title.ratings.tsv.gz"
]
TARGET_DIR = "raw_data"


def download_and_unpack():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created directory: {TARGET_DIR}")

    for url in DATASETS:
        file_name_gz = url.split("/")[-1]
        file_name_tsv = file_name_gz.replace(".gz", "")

        gz_path = os.path.join(TARGET_DIR, file_name_gz)
        tsv_path = os.path.join(TARGET_DIR, file_name_tsv)

        print(f"Downloading {url}...")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(gz_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"Unpacking to {tsv_path}...")
            with gzip.open(gz_path, 'rb') as f_in:
                with open(tsv_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Clean up the .gz file to save space
            os.remove(gz_path)
            print(f"Successfully unpacked {file_name_tsv}\n")

        except Exception as e:
            print(f"Failed to process {url}: {e}\n")


if __name__ == "__main__":
    download_and_unpack()
    print("All downloads complete.")
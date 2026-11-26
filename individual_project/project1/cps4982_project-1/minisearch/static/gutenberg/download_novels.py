import os
import time
import urllib.request
import urllib.error

# Gutenberg IDs of additional classic fiction works.
# Existing books: 11 (Alice), 84 (Frankenstein),
# 1342 (Pride and Prejudice), 2701 (Moby-Dick).

BOOK_IDS = [
    74, 76, 98, 100, 120, 145, 158, 174, 35, 36,
    55, 45, 1184, 1260, 1661, 2600, 2554, 1400,
    768, 46, 113, 500, 4300, 844, 203, 730, 766,
    1023, 16, 1268, 1727, 219, 60, 974, 244, 103,
    308, 215, 139, 236, 2852, 2814, 996, 161, 121,
    105, 141, 521, 135, 155, 43, 300, 600, 28054,
    2591, 514, 1257, 1251, 205, 209, 863, 2852,
    2000, 208, 766, 730, 19942, 106, 514, 202,
    1934, 1184, 2600, 2554, 36, 35, 55, 45, 16,
    521, 103, 308, 215, 139, 236, 135, 155, 43,
    300, 600, 28054, 2591, 74, 76, 98, 100, 120,
    145, 158, 174, 768, 46, 113, 500, 4300, 844,
    203, 1268, 1727, 219, 60, 974, 244, 996,
    161, 121, 105, 141, 1257, 1251, 205, 209,
    863, 2000, 208, 202, 1934, 106, 514,
    345, 33, 41, 12, 1399, 64317, 2641, 67979,
    16389, 394, 146, 73, 271, 1448, 1837, 1874,
    523, 159, 1013, 583, 969, 95, 77, 114,
    169, 8492, 175, 940, 1513, 1524, 932, 1952,
    2009, 218, 2197, 28520, 30254, 36, 98, 1661
]


TARGET = 100
BASE_URL = "https://gutenberg.pglaf.org/cache/epub"

def valid_text(path):
    if not os.path.exists(path):
        return False

    if os.path.getsize(path) < 10000:
        return False

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            sample = f.read(5000)
        return bool(sample.strip()) and "Project Gutenberg" in sample
    except (UnicodeDecodeError, OSError):
        return False

def count_books():
    return sum(
        1 for name in os.listdir(".")
        if name.endswith(".txt") and valid_text(name)
    )

print("Starting collection count:", count_books())

for book_id in BOOK_IDS:
    if count_books() >= TARGET:
        break

    filename = f"pg_{book_id}.txt"
    temp_filename = filename + ".part"

    if valid_text(filename):
        continue

    url = f"{BASE_URL}/{book_id}/pg{book_id}.txt"

    print(f"\nTrying Gutenberg book #{book_id}...")

    success = False

    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "MiniSearchNovelDownloader/1.0"}
            )

            with urllib.request.urlopen(request, timeout=90) as response:
                content = response.read()

            if len(content) < 10000:
                raise ValueError("Downloaded file is too small")

            text = content.decode("utf-8-sig")

            if "Project Gutenberg" not in text[:10000]:
                raise ValueError("Not a recognised Gutenberg text")

            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(text)

            os.replace(temp_filename, filename)
            success = True

            print("Downloaded:", filename)
            print("Current valid collection:", count_books(), "/", TARGET)
            break

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            time.sleep(2)

    time.sleep(1)

    if not success:
        print("Skipping book:", book_id)

print("\n===================================")
print("DOWNLOAD FINISHED")
print("Valid text files:", count_books(), "/", TARGET)
print("===================================")

if count_books() < TARGET:
    print("The candidate list was exhausted before reaching 100.")
    print("No invalid or failed downloads were counted.")

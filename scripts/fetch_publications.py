import requests
from tabulate import tabulate
import csv

def filter_by_author(items, target_author):
    target_lower = target_author.lower()
    filtered = []
    for item in items:
        authors = item.get('author', [])
        for a in authors:
            full_name = f"{a.get('given','')} {a.get('family','')}".strip().lower()
            if target_lower in full_name:
                filtered.append(item)
                break  # Found author, no need to check others
    return filtered

def remove_duplicates_by_title(items):
    seen_titles = set()
    unique_items = []
    for item in items:
        title = item.get('title', ['No title'])[0].strip().lower()
        if title not in seen_titles:
            unique_items.append(item)
            seen_titles.add(title)
    return unique_items

def fetch_crossref(author, start_year=None, end_year=None, keyword=None, max_results=200):
    if not author.strip():
        raise ValueError("Author name is required.")

    base_url = "https://api.crossref.org/works"
    rows = 100  # max per page
    offset = 0
    results = []

    while offset < max_results:
        params = {
            'query.author': author,
            'rows': rows,
            'offset': offset
        }

        filters = []
        if start_year:
            filters.append(f"from-pub-date:{start_year}-01-01")
        if end_year:
            filters.append(f"until-pub-date:{end_year}-12-31")
        if filters:
            params['filter'] = ','.join(filters)

        if keyword:
            params['query'] = keyword

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        items = response.json().get('message', {}).get('items', [])
        if not items:
            break

        results.extend(items)
        if len(items) < rows:
            break
        offset += rows

    return results[:max_results]

def format_results(items):
    table = []
    for i, item in enumerate(items, start=1):
        title = item.get('title', ['No title'])[0]
        authors = item.get('author', [])
        author_names = ', '.join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors]) or "N/A"
        pub_year = item.get('issued', {}).get('date-parts', [[None]])[0][0] or "N/A"
        doi = item.get('DOI', 'N/A')
        doi_link = f"https://doi.org/{doi}" if doi != 'N/A' else 'N/A'
        table.append([i, title, author_names, pub_year, doi_link])
    return table

def print_results(table):
    headers = ["#", "Title", "Authors", "Year", "DOI"]
    print(tabulate(table, headers=headers, tablefmt="fancy_grid", maxcolwidths=[5, 50, 30, 6, 40]))

def export_csv(table, filename="crossref_results.csv"):
    headers = ["#", "Title", "Authors", "Year", "DOI"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(table)
    print(f"Results saved to {filename}")

# ---- Main ----
if __name__ == "__main__":
    author = input("Author name (required): ")
    start = input("Start year (optional): ")
    end = input("End year (optional): ")
    keyword = input("Keyword (optional): ")

    start_year = int(start) if start.isdigit() else None
    end_year = int(end) if end.isdigit() else None

    items = fetch_crossref(author, start_year, end_year, keyword, max_results=200)
    items = filter_by_author(items, author)
    items = remove_duplicates_by_title(items)  # Remove duplicates

    if not items:
        print("No results found.")
    else:
        table = format_results(items)
        print_results(table)
        export_csv(table)

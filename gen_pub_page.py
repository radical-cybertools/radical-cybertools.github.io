
import csv
from collections import defaultdict

# Read CSV and group by year
csv_file = "crossref_results.csv"
grouped_by_year = defaultdict(list)

with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        year = row['Year']
        title = row['Title']
        authors = row['Authors']
        doi = row['DOI']
        grouped_by_year[year].append({
            "title": title,
            "authors": authors,
            "doi": doi
        })

# Generate Markdown with bullet points
md_file = "docs/publications.md"

with open(md_file, "w", encoding="utf-8") as f:
    f.write("# Publications\n\n")

    # Sort years descending
    for year in sorted(grouped_by_year.keys(), reverse=True):
        f.write(f"## {year}\n\n")
        for pub in grouped_by_year[year]:
            title = pub["title"]
            authors = pub["authors"]
            doi = pub["doi"]
            doi_link = f"[{doi}](https://doi.org/{doi})" if doi != "N/A" else "N/A"

            # Bullet point format
            f.write(f"- **{title}**  \n  Authors: {authors}  \n  DOI: {doi_link}\n\n")

print(f"Markdown file saved as {md_file}")


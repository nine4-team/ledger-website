#!/usr/bin/env python3
"""Regenerate the docs page shells, homepage, and search index.

The article body of each page (the HTML inside <article class="docs-article">)
is the content source: this script reads it from the existing page, then
rewrites the full page around it (topbar, sidebar, page header, prev/next).
The homepage is fully generated.

To add a page: create <section>/<slug>.html containing at minimum
<article class="docs-article">...body...</article>, add it to NAV below in the
position it belongs, then run:  python3 docs/build.py
"""

import html as htmllib
import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent

NAV = [
    ("Getting Started", "getting-started", [
        ("what-ledger-is", "What Ledger Is"),
        ("first-day-quick-start", "First-Day Quick Start"),
        ("navigation-overview", "Navigation Overview"),
        ("roles-and-permissions", "Roles and Permissions"),
    ]),
    ("Core Concepts", "core-concepts", [
        ("projects", "Projects"),
        ("items-and-item-quick-drafts", "Items and Item Quick Drafts"),
        ("transactions", "Transactions"),
        ("spaces", "Spaces"),
        ("inventory", "Inventory"),
        ("budgets", "Budgets"),
        ("billing-and-invoices", "Billing and Invoices"),
        ("review-queue", "Review Queue"),
        ("search", "Search"),
    ]),
    ("Workflows", "workflows", [
        ("create-a-project", "Create a Project"),
        ("add-an-item-to-a-project", "Add an Item to a Project"),
        ("capture-item-quick-drafts", "Capture Item Quick Drafts"),
        ("create-a-transaction", "Create a Transaction"),
        ("move-inventory-items-to-a-project", "Move Inventory Items to a Project"),
        ("return-items", "Return Items"),
        ("review-pending-transactions", "Review Pending Transactions"),
        ("create-an-invoice", "Create an Invoice"),
        ("generate-client-reports", "Generate Client Reports"),
        ("export-transactions", "Export Transactions"),
        ("find-items-transactions-and-spaces", "Find Items, Transactions, and Spaces"),
    ]),
    ("Admin", "admin", [
        ("manage-users", "Manage Users"),
        ("manage-financial-access", "Manage Financial Access"),
        ("manage-budget-categories", "Manage Budget Categories"),
        ("manage-space-templates", "Manage Space Templates"),
        ("manage-vendors", "Manage Vendors"),
        ("archive-or-delete-projects", "Archive or Delete Projects"),
    ]),
    ("Reference", "reference", [
        ("glossary", "Glossary"),
        ("item-statuses", "Item Statuses"),
        ("transaction-types", "Transaction Types"),
        ("budget-category-types", "Budget Category Types"),
        ("invoice-statuses", "Invoice Statuses"),
        ("common-issues", "Common Issues"),
    ]),
]

# Workflows surfaced on the homepage as "Common tasks".
COMMON_TASKS = [
    "workflows/create-a-project.html",
    "workflows/add-an-item-to-a-project.html",
    "workflows/capture-item-quick-drafts.html",
    "workflows/create-a-transaction.html",
    "workflows/return-items.html",
    "workflows/create-an-invoice.html",
    "workflows/generate-client-reports.html",
    "workflows/review-pending-transactions.html",
]

PAGES = [
    {"section": section, "path": f"{directory}/{slug}.html", "title": title}
    for section, directory, entries in NAV
    for slug, title in entries
]
BY_PATH = {p["path"]: p for p in PAGES}

ARTICLE_RE = re.compile(r'<article class="docs-article">\s*(.*?)\s*</article>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def extract_body(path):
    page_file = DOCS / path
    match = ARTICLE_RE.search(page_file.read_text())
    if not match:
        raise SystemExit(f'{path}: no <article class="docs-article"> block found')
    return match.group(1)


def index_text(body_html):
    text = htmllib.unescape(TAG_RE.sub(" ", body_html))
    return re.sub(r"\s+", " ", text).strip().lower()[:2000]


def sidebar_html(root, active_path):
    parts = [
        '    <aside id="docs-sidebar" class="docs-sidebar" aria-label="Docs navigation">',
        '      <input class="docs-search" type="search" placeholder="Search docs" aria-label="Search docs">',
    ]
    for section, directory, entries in NAV:
        parts.append('      <section class="docs-nav-section">')
        parts.append(f'        <h2 class="docs-nav-section-title">{section}</h2>')
        parts.append('        <ul class="docs-nav-list">')
        for slug, title in entries:
            path = f"{directory}/{slug}.html"
            cls = "docs-nav-link active" if path == active_path else "docs-nav-link"
            parts.append(
                f'          <li><a class="{cls}" href="{root}{path}" data-doc-link data-href="{path}">{title}</a></li>'
            )
        parts.append("        </ul>")
        parts.append("      </section>")
    parts.append('      <p class="docs-empty">No matching docs found.</p>')
    parts.append("    </aside>")
    return "\n".join(parts)


def page_shell(root, head_title, description, active_path, main_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <title>{head_title}</title>
  <link rel="stylesheet" href="{root}docs.css">
  <link rel="icon" type="image/png" sizes="32x32" href="{root}../ledger_logo.png">
</head>
<body data-root="{root}">
  <header class="docs-topbar">
    <div class="docs-topbar-inner">
      <a class="docs-brand" href="{root}../index.html"><img src="{root}../ledger_logo.png" alt="Ledger"><span>Ledger Docs</span></a>
      <div class="docs-topbar-right">
        <nav class="docs-toplinks" aria-label="Top navigation">
          <a href="{root}index.html">Docs Home</a>
          <a href="{root}../index.html">Website</a>
        </nav>
        <button class="docs-menu-toggle" type="button" aria-expanded="false" aria-controls="docs-sidebar">Menu</button>
      </div>
    </div>
  </header>
  <div class="docs-shell">
{sidebar_html(root, active_path)}
    <main class="docs-content">
{main_html}
    </main>
  </div>
  <script src="{root}search-index.js"></script>
  <script src="{root}docs.js"></script>
</body>
</html>
"""


def pagenav_html(root, prev_page, next_page):
    links = []
    if prev_page:
        links.append(
            f'        <a class="docs-pagenav-link prev" href="{root}{prev_page["path"]}">'
            f'<span class="docs-pagenav-label">Previous</span>'
            f'<span class="docs-pagenav-title">{prev_page["title"]}</span></a>'
        )
    if next_page:
        links.append(
            f'        <a class="docs-pagenav-link next" href="{root}{next_page["path"]}">'
            f'<span class="docs-pagenav-label">Next</span>'
            f'<span class="docs-pagenav-title">{next_page["title"]}</span></a>'
        )
    if not links:
        return ""
    inner = "\n".join(links)
    return f'      <nav class="docs-pagenav" aria-label="Page navigation">\n{inner}\n      </nav>'


def article_main(page, body, prev_page, next_page):
    root = "../"
    parts = [
        '      <header class="docs-page-header">',
        f'        <p class="docs-kicker">{page["section"]}</p>',
        f'        <h1>{page["title"]}</h1>',
        "      </header>",
        '      <article class="docs-article">',
        body,
        "      </article>",
    ]
    nav = pagenav_html(root, prev_page, next_page)
    if nav:
        parts.append(nav)
    return "\n".join(parts)


def homepage_main():
    tasks = "\n".join(
        f'          <a href="{path}">{BY_PATH[path]["title"]}</a>' for path in COMMON_TASKS
    )
    return f"""      <header class="docs-page-header docs-home-header">
        <p class="docs-kicker">Employee Help Center</p>
        <h1>Ledger Docs</h1>
        <p class="docs-intro">Quick answers for everyday work in Ledger.</p>
      </header>
      <div class="docs-home-search-wrap">
        <input class="docs-search docs-home-search" type="search" placeholder="Search the docs" aria-label="Search the docs">
        <ul class="docs-home-results"></ul>
      </div>
      <div class="docs-callout">
        <strong>New to Ledger?</strong> Read <a href="getting-started/what-ledger-is.html">What Ledger Is</a>, then follow the <a href="getting-started/first-day-quick-start.html">First-Day Quick Start</a>.
      </div>
      <section class="docs-home-section">
        <h2>Common tasks</h2>
        <div class="docs-task-grid">
{tasks}
        </div>
      </section>
      <p class="docs-home-help">Stuck on something? Check <a href="reference/common-issues.html">Common Issues</a>, or ask an account admin.</p>"""


def main():
    index_entries = []
    for i, page in enumerate(PAGES):
        body = extract_body(page["path"])
        index_entries.append({
            "title": page["title"],
            "section": page["section"],
            "href": page["path"],
            "text": index_text(body),
        })
        prev_page = PAGES[i - 1] if i > 0 else None
        next_page = PAGES[i + 1] if i < len(PAGES) - 1 else None
        description = f"Ledger employee docs: {page['title']}."
        out = page_shell(
            "../",
            f"{page['title']} - Ledger Docs",
            description,
            page["path"],
            article_main(page, body, prev_page, next_page),
        )
        (DOCS / page["path"]).write_text(out)

    (DOCS / "search-index.js").write_text(
        "window.DOCS_INDEX = " + json.dumps(index_entries, indent=1) + ";\n"
    )

    home = page_shell(
        "",
        "Ledger Docs - Employee Help Center",
        "Ledger employee help docs for common workflows, concepts, admin tasks, and reference information.",
        None,
        homepage_main(),
    )
    (DOCS / "index.html").write_text(home)
    print(f"built {len(PAGES)} pages + index.html + search-index.js")


if __name__ == "__main__":
    main()

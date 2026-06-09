# Ledger Website Agent Notes

This repo is a plain static website. There is no app framework, package script,
static-site generator, or in-repo deploy configuration at the time of writing.

## Site Structure

- `index.html` is the main marketing homepage.
- `brand-theme.css` contains shared brand styles used by older/simple pages.
- `images/` contains static homepage imagery.
- `docs/` is the employee docs subsite.
  - `docs/index.html` is served as `/docs/`.
  - `docs/docs.css` contains docs-specific layout and sidebar/search styles.
  - The original Markdown docs are kept alongside generated HTML pages.
  - The docs source was copied from:
    `/Users/benjaminmackenzie/Dev/ledger_mobile/user-docs`

Because the site is static HTML, a directory-level `index.html` is the route
entry point for a subsite. For example, `/docs/` maps to `docs/index.html`.

## Live Site And Deployment

The live site verified on 2026-06-09 is:

- `https://ledger.nine4.co`
- Docs are live at `https://ledger.nine4.co/docs/`

Observed deployment behavior:

- The repo remote is GitHub.
- The default branch is `main`.
- Pushing to `origin main` published the latest site changes.
- GitHub reported the repository has moved to:
  `git@github.com:nine4-team/ledger-website.git`
- The existing remote still accepted pushes through the old path:
  `git@github.com:assiist-team/ledger-website.git`
- The live site is served through Cloudflare.
- GitHub Pages was not enabled when checked.
- No GitHub Actions workflows or deployment runs were present when checked.

Practical publish flow:

1. Make and verify static file changes locally.
2. Commit only the intended files.
3. Push `main` to `origin`.
4. Verify the live URL with `curl` or a browser.

Useful verification commands:

```sh
npx --yes htmlhint index.html 'docs/**/*.html'
python3 -m http.server 4173
curl -fsS -L https://ledger.nine4.co/docs/ | rg 'Ledger User Docs'
```

## Docs Editing Notes

Employee-facing docs should stay organized under these sections:

- Getting Started
- Core Concepts
- Workflows
- Admin
- Reference

When adding or moving docs:

- Keep Markdown source files in `docs/`.
- Publish matching `.html` files so the static site works without a Markdown
  renderer.
- Rewrite internal published links from `.md` to `.html`.
- Update `docs/index.html` and the docs sidebar navigation.
- Keep the tone employee-facing, not developer-facing.

## Git Notes

- Do not commit `.DS_Store`.
- This repo may have local uncommitted `.DS_Store` changes; ignore them unless
  the user explicitly asks to clean them up.

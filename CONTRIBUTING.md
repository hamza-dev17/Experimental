# Contributing

Thanks for contributing to `Experimental`.

## Goal

Keep every new project easy to find, easy to run, and consistent with the repository style.

## Add a New Project

1. Copy `projects/_template` into a new folder: `projects/<project-slug>`.
2. Use lowercase kebab-case for `<project-slug>`.
3. Keep the main demo entrypoint as `index.html`.
4. Add a project `README.md` with the sections below.
5. Add the project card/link to root `index.html`.
6. Add the project row to the root `README.md` projects table.

## Required README Sections (Per Project)

- `# Project Name`
- `## Summary`
- `## Controls`
- `## Requirements`
- `## Live Page`

## Optional Assets

- If needed, add assets under your project folder (for example `projects/<project-slug>/assets/`).
- Keep asset names descriptive and lightweight.

## Webcam/Permission Note

If your project needs camera input:

- Mention camera usage in `## Requirements`.
- Add clear in-page messaging when permission is denied or unavailable.

## Quality Checklist

- Folder name follows kebab-case.
- `index.html` loads without missing local files.
- Root gallery link works.
- Root README table entry is added.
- Project README is complete.
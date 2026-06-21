# Beardfish RPG Resources (Tales of the Valiant PreGens)

This repository hosts a beautiful static website displaying pre-generated characters and rules cheat sheets for the **Tales of the Valiant** roleplaying game.

## Features

- **Roster Index**: A modern, glassmorphic dashboard showcasing the characters with their class, ancestry, and distinctive fantasy icons.
- **Interactive Cheat Sheets**: Rendered HTML pages displaying each character's core capabilities, class features, lineage traits, weapons, and spell lists directly in the browser.
- **Resource Downloads**: Quick access buttons to download:
  - Pre-generated character sheets for levels 1 through 4 (PDF).
  - Print-friendly cheat sheets in PDF, Microsoft Word (DOCX), or raw Markdown format.

## Directory Structure

- `index.html`: The main roster page.
- `characters/`: Individual HTML pages for each character.
- `css/styles.css`: The styling system containing the dark-fantasy midnight theme, responsive layouts, and animations.
- `assets/pdf/`: Copied character sheet PDFs grouped by character.
- `assets/cheatsheet/`: Copied cheat sheet PDFs, DOCX, and MD files.
- `generate_site.py`: The automation script that parses the raw RPG files, creates the web pages, and copies all assets.

## Running the Generator

If the source pre-generated character sheets or cheat sheets are updated, you can regenerate the website by running:

```bash
python3 generate_site.py
```

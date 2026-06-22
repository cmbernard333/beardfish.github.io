import os
import shutil
import re

# Paths
SOURCE_PREGEN_DIR = os.environ.get(
    "SOURCE_PREGEN_DIR",
    "/home/christian/Documents/Tales of the Valiant/All Valiant 6/Valiant 6 PreGen Character Sheets/PG2",
)
SOURCE_CHEAT_DIR = os.environ.get(
    "SOURCE_CHEAT_DIR",
    "/home/christian/Documents/Tales of the Valiant/All Valiant 6/Cheat Sheets/PG2",
)
SOURCE_IMG_DIR = os.environ.get(
    "SOURCE_IMG_DIR",
    "/home/christian/Documents/Tales of the the Valiant/All Valiant 6/Images/PG2",
)
TARGET_DIR = os.environ.get("TARGET_DIR", ".")


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_inline(text):
    # bold **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # italic *text* or _text_
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)
    return text


def markdown_to_html(md_text):
    html_lines = []
    in_list = False
    for line in md_text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Headers
        if line_stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{parse_inline(line_stripped[2:])}</h1>")
        elif line_stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{parse_inline(line_stripped[3:])}</h2>")
        elif line_stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{parse_inline(line_stripped[4:])}</h3>")
        elif line_stripped.startswith("#### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h4>{parse_inline(line_stripped[5:])}</h4>")
        elif line_stripped.startswith("---"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
        # Bullet lists
        elif line_stripped.startswith("* ") or line_stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = line_stripped[2:]
            html_lines.append(f"<li>{parse_inline(content)}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{parse_inline(line_stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


def main():
    print("Starting site generation...")

    # Destination assets directories
    dest_pdf_dir = os.path.join(TARGET_DIR, "assets", "pdf")
    dest_cheatsheet_dir = os.path.join(TARGET_DIR, "assets", "cheatsheet")
    dest_img_dir = os.path.join(TARGET_DIR, "assets", "img")
    dest_chars_dir = os.path.join(TARGET_DIR, "characters")

    os.makedirs(dest_pdf_dir, exist_ok=True)
    os.makedirs(dest_cheatsheet_dir, exist_ok=True)
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_chars_dir, exist_ok=True)

    # Get all PG2 character folders
    pregen_folders = sorted(
        [
            f
            for f in os.listdir(SOURCE_PREGEN_DIR)
            if os.path.isdir(os.path.join(SOURCE_PREGEN_DIR, f))
        ]
    )
    cheat_folders = sorted(
        [
            f
            for f in os.listdir(SOURCE_CHEAT_DIR)
            if os.path.isdir(os.path.join(SOURCE_CHEAT_DIR, f))
        ]
    )

    print(
        f"Found {len(pregen_folders)} PreGen folders and {len(cheat_folders)} Cheat Sheet folders."
    )

    characters_data = []

    for pregen_folder in pregen_folders:
        # Expected base format: "02 Avena Elodie - Human Witch - Character Sheets"
        # We can extract the main base name by removing " - Character Sheets"
        base_name = pregen_folder.replace(" - Character Sheets", "").strip()

        # Extract Name and Class
        # e.g., "02 Avena Elodie - Human Witch"
        # Let's split by " - "
        parts = base_name.split(" - ")
        if len(parts) >= 2:
            raw_name = parts[0]
            # Strip leading numbers/spaces, e.g. "02 Avena Elodie" -> "Avena Elodie"
            name = re.sub(r"^\d+\s+", "", raw_name).strip()
            char_class = parts[1].strip()
        else:
            name = base_name
            char_class = "Unknown"

        slug = slugify(name)
        print(f"Processing: {name} (Class: {char_class}, Slug: {slug})")

        # Copy Character Sheet PDFs
        char_sheet_src_dir = os.path.join(SOURCE_PREGEN_DIR, pregen_folder)
        char_sheet_dest_dir = os.path.join(dest_pdf_dir, slug)
        os.makedirs(char_sheet_dest_dir, exist_ok=True)

        pdf_links = []
        for file in sorted(os.listdir(char_sheet_src_dir)):
            if file.endswith(".pdf"):
                src_path = os.path.join(char_sheet_src_dir, file)
                dest_path = os.path.join(char_sheet_dest_dir, file)
                shutil.copy2(src_path, dest_path)

                # We need a nice label, e.g. "Level 1" or "Level 2"
                level_match = re.search(r"Level\s+(\d+)", file, re.IGNORECASE)
                label = f"Level {level_match.group(1)} Sheet" if level_match else file
                relative_url = f"../assets/pdf/{slug}/{file}"
                pdf_links.append({"label": label, "url": relative_url})

        # Find matching Cheat Sheet Folder
        cheat_folder_match = None
        for cf in cheat_folders:
            cf_base = cf.replace(" - Cheat Sheets", "").strip()
            if cf_base == base_name:
                cheat_folder_match = cf
                break

        cheat_links = []
        md_content_html = ""

        if cheat_folder_match:
            cheat_src_dir = os.path.join(SOURCE_CHEAT_DIR, cheat_folder_match)
            cheat_dest_dir = os.path.join(dest_cheatsheet_dir, slug)
            os.makedirs(cheat_dest_dir, exist_ok=True)

            # Find the markdown file and PDF/DOCX files
            md_file_path = None
            for file in sorted(os.listdir(cheat_src_dir)):
                src_path = os.path.join(cheat_src_dir, file)
                dest_path = os.path.join(cheat_dest_dir, file)
                shutil.copy2(src_path, dest_path)

                relative_url = f"../assets/cheatsheet/{slug}/{file}"

                if file.endswith(".md"):
                    md_file_path = src_path
                    cheat_links.append(
                        {"label": "Cheat Sheet (Markdown Source)", "url": relative_url}
                    )
                elif file.endswith(".pdf"):
                    cheat_links.append(
                        {"label": "Cheat Sheet (PDF)", "url": relative_url}
                    )
                elif file.endswith(".docx"):
                    cheat_links.append(
                        {"label": "Cheat Sheet (Word)", "url": relative_url}
                    )

            if md_file_path:
                with open(md_file_path, "r", encoding="utf-8") as f:
                    md_text = f.read()
                md_content_html = markdown_to_html(md_text)
        else:
            print(f"Warning: No matching Cheat Sheet folder found for {base_name}")

        characters_data.append(
            {
                "name": name,
                "class": char_class,
                "slug": slug,
                "pdf_links": pdf_links,
                "cheat_links": cheat_links,
                "content_html": md_content_html,
            }
        )

    # Now generate the HTML files
    # 1. Main CSS file is generated elsewhere

    # 2. Character Pages
    for char in characters_data:
        char_page_path = os.path.join(dest_chars_dir, f"{char['slug']}.html")

        pdf_buttons = "".join(
            [
                f'<a href="{link["url"]}" class="btn pdf-btn" download><i class="fas fa-file-pdf"></i> {link["label"]}</a>'
                for link in char["pdf_links"]
            ]
        )
        cheat_buttons = "".join(
            [
                f'<a href="{link["url"]}" class="btn cheat-btn" download><i class="fas fa-file-alt"></i> {link["label"]}</a>'
                for link in char["cheat_links"]
            ]
        )

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{char["name"]} - {char["class"]} | Beardfish RPG Resources</title>
    <meta name="description" content="Cheat sheet and character sheets for {char["name"]}, the {char["class"]} in Tales of the Valiant RPG.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <div class="bg-glow"></div>
    <div class="container">
        <header class="char-header">
            <a href="../index.html" class="back-link"><i class="fas fa-arrow-left"></i> Back to Roster</a>
            <h1 class="char-title">{char["name"]}</h1>
            <p class="char-subtitle">{char["class"]}</p>
        </header>

        <section class="downloads-section">
            <div class="downloads-container">
                <div class="download-group">
                    <h3><i class="fas fa-user-shield"></i> PreGen Character Sheets</h3>
                    <div class="btn-grid">
                        {pdf_buttons}
                    </div>
                </div>
                <div class="download-group">
                    <h3><i class="fas fa-book-open"></i> Cheat Sheets</h3>
                    <div class="btn-grid">
                        {cheat_buttons}
                    </div>
                </div>
            </div>
        </section>

        <main class="content-card">
            <div class="cheat-sheet-content">
                {char["content_html"]}
            </div>
        </main>

        <footer>
            <p>&copy; Kobold Press, Tales of the Valiant are trademarks of Open Design LLC. 2026. All Rights Reserved.</p>
        </footer>
    </div>
</body>
</html>
"""
        with open(char_page_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    # 3. Index Page
    index_path = os.path.join(TARGET_DIR, "index.html")
    char_list_html = ""
    for char in characters_data:
        # Determine class icons for styling or decorative elements
        icon_class = "fa-wand-magic-sparkles"  # Witch
        cls_lower = char["class"].lower()
        if "witch" in cls_lower:
            icon_class = "fa-hat-wizard"
        elif "vanguard" in cls_lower:
            icon_class = "fa-shield-halved"
        elif "bard" in cls_lower:
            icon_class = "fa-guitar"
        elif "theurge" in cls_lower:
            icon_class = "fa-dharmachakra"
        elif "barbarian" in cls_lower:
            icon_class = "fa-gavel"
        elif "ranger" in cls_lower:
            icon_class = "fa-location-crosshairs"

        char_list_html += f"""
        <a href="characters/{char["slug"]}.html" class="char-card" id="char-card-{char["slug"]}">
            <div class="card-glow"></div>
            <div class="card-icon"><i class="fas {icon_class}"></i></div>
            <div class="card-info">
                <h2>{char["name"]}</h2>
                <p class="class-tag">{char["class"]}</p>
            </div>
            <div class="card-arrow">
                <i class="fas fa-chevron-right"></i>
            </div>
        </a>
        """

    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beardfish RPG Resources | Tales of the Valiant PreGens</title>
    <meta name="description" content="Access PreGen character sheets and level-up cheat sheets for the Tales of the Valiant roleplaying game.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="bg-glow"></div>
    <div class="container">
        <header class="main-header">
            <h1 class="main-title">Beardfish RPG Resources</h1>
            <p class="main-subtitle">Tales of the Valiant PreGen Characters &amp; Cheat Sheets</p>
        </header>

        <main class="roster-section">
            <h2 class="section-title"><i class="fas fa-users"></i> PreGen Character Roster</h2>
            <div class="roster-grid">
                {char_list_html}
            </div>
        </main>

        <footer>
            <p>&copy; 2026 Beardfish RPG Resources. Generated for GitHub Pages hosting.</p>
        </footer>
    </div>
</body>
</html>
"""
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print("Site generation complete!")


if __name__ == "__main__":
    main()

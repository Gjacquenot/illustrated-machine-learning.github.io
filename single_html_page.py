# pandoc --metadata title="CV"  --embed-resources --standalone --toc --toc-depth=4  --number-sections --highlight-style pygments -f markdown cv-index.md --css pandoc.css -o cv.html
# pandoc --metadata title="ML"  --embed-resources --standalone --toc --toc-depth=4  --number-sections --highlight-style pygments -f markdown ml-index.md --css pandoc.css -o ml.html

# pandoc --metadata title="CV"  --embed-resources --standalone --number-sections --highlight-style pygments -f markdown cv-index.md --css pandoc.css -o cv-notoc.html
# pandoc --metadata title="ML"  --embed-resources --standalone --number-sections --highlight-style pygments -f markdown ml-index.md --css pandoc.css -o ml-notoc.html


import re
from typing import List

import bs4
from bs4 import BeautifulSoup


def extract_svg_image_from_url(html_page: str) -> str:
    soup = BeautifulSoup(open(html_page, "r").read(), "html.parser")
    objects = soup.find_all("object")
    svg_images = []
    for current_object in objects:
        if (
            current_object
            and current_object.attrs.get("type") == "image/svg+xml"
            and current_object.attrs.get("class") == ["img-content"]
        ):
            svg_images.append(current_object.attrs["data"])
    return svg_images


def extract_svg_image_from_url_and_id(html_page: str, keyword: str) -> str:
    soup = BeautifulSoup(open(html_page, "r").read(), "html.parser")
    is_to_be_considered = False
    for k in soup.find_all("div"):
        if "class" in k.attrs and k.attrs["class"] == ["container"]:
            for m in k:
                # print(type(m))
                if is_to_be_considered and isinstance(m, bs4.element.Tag):
                    # print("Bingo")
                    # print(m)
                    # print()
                    svg_image = m.attrs["data"]
                    # print("Bingo")
                    break
                if m.name == "a":
                    # print("GJ1")
                    # print(m)
                    # print(m.attrs)
                    if keyword == m.attrs["name"]:
                        is_to_be_considered = True
                        # print("FOUND")
                    # print("GJ2")
    return svg_image


def add_section(
    new_content: List[str], already_added_svg: List[str], add_svg: bool, level: int, line: str
) -> List[str]:
    new_line = "#" * (level + 1) + "  " + line[2 + 3 * (level - 1) :]
    new_content.append(new_line.rstrip())
    if not add_svg:
        return new_content, already_added_svg
    url = line.split("(")[1].split(")")[0]
    if "#" in url and len(url) > 1:
        svg_image = extract_svg_image_from_url_and_id(url.split("#")[0], url.split("#")[1])
        svg_image = svg_image.replace(r"./../../", r"./")
        if svg_image not in already_added_svg:
            already_added_svg.append(svg_image)
            new_content.append(f"![]({svg_image})")
    elif len(url) > 1:
        svg_images = extract_svg_image_from_url(url)
        for svg_image in svg_images:
            svg_image = svg_image.replace(r"./../../", r"./")
            if svg_image not in already_added_svg:
                already_added_svg.append(svg_image)
                new_content.append(f"![]({svg_image})")
    return new_content, already_added_svg


def process_one_file(index_md: str, output_md: str):
    title1 = re.compile(r"^[0-9]\.")
    title2 = re.compile(r"^   [0-9]\.")
    title3 = re.compile(r"^      [0-9]\.")
    title4 = re.compile(r"^         [0-9]\.")
    with open(index_md, "rt") as fid:
        content = fid.readlines()
    new_content = []
    already_added_svg = []
    for i_line, line in enumerate(content):
        if title1.match(line):
            add_svg = not (i_line < (len(content) - 1) and title2.match(content[i_line + 1]))
            new_content, already_added_svg = add_section(
                new_content, already_added_svg, add_svg, 1, line
            )
        elif title2.match(line):
            add_svg = not (i_line < (len(content) - 1) and title3.match(content[i_line + 1]))
            new_content, already_added_svg = add_section(
                new_content, already_added_svg, add_svg, 2, line
            )
        elif title3.match(line):
            add_svg = not (i_line < (len(content) - 1) and title4.match(content[i_line + 1]))
            new_content, already_added_svg = add_section(
                new_content, already_added_svg, add_svg, 3, line
            )
        elif title4.match(line):
            new_content, already_added_svg = add_section(
                new_content, already_added_svg, True, 4, line
            )
        else:
            new_line = line
            new_content.append(new_line.rstrip())
    print(new_content)

    with open(output_md, "wt") as fid:
        for line in new_content:
            fid.write(line + "\n\n")


process_one_file("indexes/cv-index.md", "cv-index.md")
process_one_file("indexes/ml-index.md", "ml-index.md")

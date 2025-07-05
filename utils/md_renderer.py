import markdown

def render_markdown_report(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        md_content = f.read()
    return markdown.markdown(md_content, extensions=["extra", "nl2br"])

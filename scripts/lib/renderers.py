import html
from typing import Iterable, List, Sequence, Tuple


def escape_text(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def render_badge(text: str, tone: str) -> str:
    return '<span class="badge badge-{0}">{1}</span>'.format(
        escape_text(tone), escape_text(text)
    )


def render_empty_state(message: str = "未登録") -> str:
    return '<div class="empty-state">{0}</div>'.format(escape_text(message))


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    html_parts: List[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        if line.startswith("# "):
            close_list()
            html_parts.append("<h1>{0}</h1>".format(escape_text(line[2:])))
            continue

        if line.startswith("## "):
            close_list()
            html_parts.append("<h2>{0}</h2>".format(escape_text(line[3:])))
            continue

        if line.startswith("### "):
            close_list()
            html_parts.append("<h3>{0}</h3>".format(escape_text(line[4:])))
            continue

        if line.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append("<li>{0}</li>".format(escape_text(line[2:])))
            continue

        close_list()
        html_parts.append("<p>{0}</p>".format(escape_text(line)))

    close_list()
    return "\n".join(html_parts)


def render_table(
    columns: Sequence[Tuple[str, str]],
    rows: Sequence[dict],
    empty_message: str = "未登録",
) -> str:
    if not rows:
        return render_empty_state(empty_message)

    header_html = "".join(
        "<th>{0}</th>".format(escape_text(label)) for _, label in columns
    )

    body_rows: List[str] = []
    for row in rows:
        cells = []
        for key, _ in columns:
            value = row.get(key, "")
            cells.append("<td>{0}</td>".format(value if key.startswith("__html__") else escape_text(value)))
        body_rows.append("<tr>{0}</tr>".format("".join(cells)))

    return (
        '<div class="table-wrap"><table class="data-table">'
        "<thead><tr>{0}</tr></thead>"
        "<tbody>{1}</tbody>"
        "</table></div>"
    ).format(header_html, "".join(body_rows))


def render_chip_row(values: Iterable[str]) -> str:
    chips = "".join('<span class="chip">{0}</span>'.format(escape_text(value)) for value in values)
    return '<div class="chip-row">{0}</div>'.format(chips)


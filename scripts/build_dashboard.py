import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.constants import (
    CONFIG_PATH,
    DASHBOARD_OUTPUT_PATH,
    DAY_ORDER,
    DOC_TAB_FILES,
    HOTEL_PATH,
    MYMAPS_OUTPUT_PATH,
    PAGES_INDEX_OUTPUT_PATH,
    RESTAURANT_PATH,
    ROOT_INDEX_OUTPUT_PATH,
    SIGHTSEEING_PATH,
    TRANSPORT_PATH,
)
from lib.loaders import load_trip_config, read_csv_rows, read_markdown
from lib.renderers import (
    escape_text,
    markdown_to_html,
    render_badge,
    render_chip_row,
    render_empty_state,
    render_table,
)
from lib.validators import load_and_validate_sightseeing


THEME_PRESETS = {
    "professional": {
        "eyebrow": "Travel Planning Dashboard",
        "hero_tag": "PLAN OVERVIEW",
        "hero_note_label": "旅のテーマ",
        "topbar_label": "Planning view",
        "generated_prefix": "Generated",
        "footer": "Static local MVP dashboard for travel planning.",
        "stats_title": "検討メモ",
        "summary_class": "hero-summary",
        "sans": '"Hiragino Sans", "Yu Gothic", -apple-system, BlinkMacSystemFont, sans-serif',
        "serif": '"Hiragino Mincho ProN", "Yu Mincho", Georgia, serif',
        "bg_top": "#f6efe4",
        "bg_bottom": "#fffaf2",
        "surface": "rgba(255, 255, 255, 0.8)",
        "surface_strong": "#fffdf8",
        "ink": "#1f2933",
        "muted": "#5f6c76",
        "line": "rgba(145, 114, 73, 0.18)",
        "accent": "#b14d32",
        "accent_soft": "rgba(177, 77, 50, 0.12)",
        "accent_soft_strong": "rgba(177, 77, 50, 0.2)",
        "gold": "#c6952d",
        "green": "#2c6b4f",
        "blue": "#335c81",
        "card_glow": "rgba(198, 149, 45, 0.16)",
        "card_blush": "rgba(177, 77, 50, 0.12)",
        "shadow": "0 18px 40px rgba(84, 56, 18, 0.12)",
        "hero_border": "rgba(255, 255, 255, 0.7)",
        "tab_surface": "rgba(255, 253, 248, 0.85)",
        "table_head": "rgba(255, 250, 242, 0.92)",
    },
    "couple": {
        "eyebrow": "Anniversary Escape",
        "hero_tag": "FOR THE TWO OF US",
        "hero_note_label": "この旅で大事にしたいこと",
        "topbar_label": "Couple itinerary",
        "generated_prefix": "Updated",
        "footer": "A small keepsake site for planning a gentle birthday getaway together.",
        "stats_title": "ふたりの旅メモ",
        "summary_class": "hero-summary hero-summary-soft",
        "sans": '"Hiragino Maru Gothic ProN", "Hiragino Sans", "Yu Gothic", -apple-system, BlinkMacSystemFont, sans-serif',
        "serif": '"Tsukushi A Round Gothic", "Hiragino Mincho ProN", "Yu Mincho", Georgia, serif',
        "bg_top": "#fff1ee",
        "bg_bottom": "#fffaf5",
        "surface": "rgba(255, 252, 250, 0.86)",
        "surface_strong": "rgba(255, 255, 255, 0.92)",
        "ink": "#3f2f38",
        "muted": "#7a6570",
        "line": "rgba(197, 120, 131, 0.2)",
        "accent": "#d56a7c",
        "accent_soft": "rgba(213, 106, 124, 0.14)",
        "accent_soft_strong": "rgba(213, 106, 124, 0.22)",
        "gold": "#d6a35b",
        "green": "#5f8a72",
        "blue": "#59719d",
        "card_glow": "rgba(214, 163, 91, 0.16)",
        "card_blush": "rgba(213, 106, 124, 0.18)",
        "shadow": "0 20px 46px rgba(170, 103, 117, 0.14)",
        "hero_border": "rgba(255, 255, 255, 0.9)",
        "tab_surface": "rgba(255, 247, 246, 0.88)",
        "table_head": "rgba(255, 244, 243, 0.95)",
    },
}


def _priority_badge(priority: str) -> str:
    return render_badge(priority, "priority-{0}".format(priority.lower()))


def _heat_badge(heat_risk: str) -> str:
    tone_map = {"高": "heat-high", "中": "heat-mid", "低": "heat-low"}
    return render_badge(heat_risk, tone_map.get(heat_risk, "neutral"))


def _rain_badge(rain_ok: str) -> str:
    tone_map = {"可": "rain-good", "一部可": "rain-mid", "不可": "rain-bad"}
    return render_badge(rain_ok, tone_map.get(rain_ok, "neutral"))


def _birthday_badge(score: str) -> str:
    tone = "birthday-high" if score and int(score) >= 4 else "birthday-mid"
    return render_badge("{0}/5".format(score), tone)


def _format_source_link(url: str) -> str:
    if not url:
        return "未登録"
    safe_url = escape_text(url)
    return '<a href="{0}" target="_blank" rel="noreferrer">link</a>'.format(safe_url)


def _load_optional_rows(path: Path) -> List[Dict[str, str]]:
    _, rows = read_csv_rows(path)
    return rows


def _build_stats(rows: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    priority_counts = Counter(row["priority"] for row in rows)
    rain_friendly = sum(1 for row in rows if row["rain_ok"] in {"可", "一部可"})
    birthday_friendly = sum(int(row["birthday_score"]) >= 4 for row in rows)
    return [
        {"label": "候補総数", "value": str(len(rows))},
        {"label": "優先度S", "value": str(priority_counts.get("S", 0))},
        {"label": "雨天対応可", "value": str(rain_friendly)},
        {"label": "誕生日向き4以上", "value": str(birthday_friendly)},
    ]


def _resolve_theme(trip: Dict[str, object]) -> Dict[str, str]:
    tone = str(trip.get("tone", "professional")).strip().lower()
    return dict(THEME_PRESETS.get(tone, THEME_PRESETS["professional"]))


def _build_stats_html(stats: Sequence[Dict[str, str]], theme: Dict[str, str]) -> str:
    cards = []
    for stat in stats:
        cards.append(
            (
                '<article class="stat-card">'
                '<div class="stat-label">{0}</div>'
                '<div class="stat-value">{1}</div>'
                "</article>"
            ).format(escape_text(stat["label"]), escape_text(stat["value"]))
        )
    return (
        '<section class="stats-section">'
        '<div class="section-mini-label">{0}</div>'
        '<div class="stats-grid">{1}</div>'
        "</section>"
    ).format(escape_text(theme["stats_title"]), "".join(cards))


def _build_overview_section(
    trip: Dict[str, object],
    docs: Dict[str, str],
    rows: Sequence[Dict[str, str]],
    theme: Dict[str, str],
) -> str:
    stats_html = _build_stats_html(_build_stats(rows), theme)
    priorities = trip.get("priorities", [])
    areas = trip.get("areas", [])
    meta_html = (
        '<div class="hero-meta">'
        '<span>{0}</span>'
        '<span>{1} - {2}</span>'
        '<span>{3}泊{4}日</span>'
        "</div>"
    ).format(
        escape_text(" / ".join(areas if isinstance(areas, list) else [])),
        escape_text(trip.get("start_date", "")),
        escape_text(trip.get("end_date", "")),
        escape_text(trip.get("nights", "")),
        escape_text(trip.get("days", "")),
    )
    priorities_html = render_chip_row(priorities if isinstance(priorities, list) else [])
    purpose = str(trip.get("purpose", "")).strip()
    purpose_html = ""
    if purpose:
        purpose_html = (
            '<div class="hero-note">'
            '<div class="section-mini-label">{0}</div>'
            '<p>{1}</p>'
            "</div>"
        ).format(escape_text(theme["hero_note_label"]), escape_text(purpose))
    return (
        '<section class="hero">'
        '<div class="hero-copy">'
        '<p class="eyebrow">{0}</p>'
        '<div class="hero-tag">{1}</div>'
        '<h1>{2}</h1>'
        '<p class="{3}">{4}</p>'
        "{5}"
        "{6}"
        "</div>"
        '<div class="hero-side">'
        "{7}"
        "{8}"
        "</div>"
        "</section>"
        '<section class="content-card content-card-overview">{9}</section>'
    ).format(
        escape_text(theme["eyebrow"]),
        escape_text(theme["hero_tag"]),
        escape_text(trip.get("trip_name", "")),
        escape_text(theme["summary_class"]),
        escape_text(trip.get("summary", "")),
        meta_html,
        priorities_html,
        stats_html,
        purpose_html,
        markdown_to_html(docs["overview"]),
    )


def _build_day_cards(rows: Sequence[Dict[str, str]]) -> str:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["day_candidate"]].append(row)

    cards = []
    for day in DAY_ORDER:
        day_rows = sorted(grouped.get(day, []), key=lambda row: (row["priority"], row["name"]))
        if not day_rows:
            cards.append(
                '<article class="day-card"><h3>{0}</h3>{1}</article>'.format(
                    escape_text(day), render_empty_state("候補なし")
                )
            )
            continue

        items = []
        for row in day_rows:
            items.append(
                (
                    "<li>"
                    '<div class="candidate-name">{0}</div>'
                    '<div class="candidate-badges">{1}{2}{3}{4}</div>'
                    '<p class="candidate-memo">{5}</p>'
                    "</li>"
                ).format(
                    escape_text(row["name"]),
                    _priority_badge(row["priority"]),
                    _heat_badge(row["heat_risk"]),
                    _rain_badge(row["rain_ok"]),
                    _birthday_badge(row["birthday_score"]),
                    escape_text(row["memo"]),
                )
            )
        cards.append(
            '<article class="day-card"><h3>{0}</h3><ul class="candidate-list">{1}</ul></article>'.format(
                escape_text(day), "".join(items)
            )
        )

    return '<section class="day-grid">{0}</section>'.format("".join(cards))


def _build_sightseeing_table(rows: Sequence[Dict[str, str]]) -> str:
    table_rows: List[Dict[str, str]] = []
    for row in rows:
        table_rows.append(
            {
                "name": row["name"],
                "area": row["area"],
                "category": row["category"],
                "__html__priority": _priority_badge(row["priority"]),
                "day_candidate": row["day_candidate"],
                "stay_minutes": row["stay_minutes"],
                "__html__birthday": _birthday_badge(row["birthday_score"]),
                "__html__heat": _heat_badge(row["heat_risk"]),
                "__html__rain": _rain_badge(row["rain_ok"]),
                "memo": row["memo"],
                "__html__source": _format_source_link(row["source_url"]),
            }
        )

    columns = [
        ("name", "名称"),
        ("area", "エリア"),
        ("category", "カテゴリ"),
        ("__html__priority", "優先度"),
        ("day_candidate", "日程候補"),
        ("stay_minutes", "滞在分"),
        ("__html__birthday", "誕生日向き"),
        ("__html__heat", "暑さ"),
        ("__html__rain", "雨天"),
        ("memo", "メモ"),
        ("__html__source", "情報源"),
    ]
    return render_table(columns, table_rows, empty_message="観光候補なし")


def _build_simple_table(rows: Sequence[Dict[str, str]], columns, empty_message: str) -> str:
    return render_table(columns, list(rows), empty_message=empty_message)


def _build_reservation_review(rows: Sequence[Dict[str, str]]) -> str:
    review_rows: List[Dict[str, str]] = []
    for row in rows:
        reasons = []
        if row["category"] in {"温泉", "美術館", "体験"}:
            reasons.append("事前予約確認向き")
        if row["priority"] == "S":
            reasons.append("優先度S")
        if int(row["birthday_score"]) >= 5:
            reasons.append("誕生日スコア高")
        if reasons:
            review_rows.append(
                {
                    "name": row["name"],
                    "day_candidate": row["day_candidate"],
                    "reason": " / ".join(reasons),
                    "memo": row["memo"],
                }
            )

    columns = [
        ("name", "候補"),
        ("day_candidate", "日程候補"),
        ("reason", "確認理由"),
        ("memo", "メモ"),
    ]
    return render_table(columns, review_rows, empty_message="予約確認候補なし")


def _build_birthday_focus(rows: Sequence[Dict[str, str]]) -> str:
    focused_rows = [
        {
            "name": row["name"],
            "area": row["area"],
            "__html__priority": _priority_badge(row["priority"]),
            "__html__birthday": _birthday_badge(row["birthday_score"]),
            "memo": row["memo"],
        }
        for row in sorted(
            [row for row in rows if int(row["birthday_score"]) >= 4],
            key=lambda item: (-int(item["birthday_score"]), item["priority"], item["name"]),
        )
    ]
    columns = [
        ("name", "候補"),
        ("area", "エリア"),
        ("__html__priority", "優先度"),
        ("__html__birthday", "誕生日向き"),
        ("memo", "メモ"),
    ]
    return render_table(columns, focused_rows, empty_message="誕生日向き候補なし")


def _build_section(title: str, doc_html: str, content_html: str) -> str:
    return (
        '<section class="content-card">'
        '<div class="section-header"><h2>{0}</h2></div>'
        '<div class="section-copy">{1}</div>'
        '<div class="section-body">{2}</div>'
        "</section>"
    ).format(escape_text(title), doc_html, content_html)

def _build_map_embed_section(trip: Dict[str, object]) -> str:
    view_url = str(trip.get("mymaps_view_url", "") or "")
    embed_url = str(trip.get("mymaps_embed_url", "") or "")

    if not embed_url:
        return _build_section(
            "地図",
            "<p>Google My Maps の埋め込み URL が未設定です。</p>",
            render_empty_state("地図未設定"),
        )

    content_html = (
        '<div class="map-frame-wrap">'
        '<iframe class="map-frame" src="{0}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
        "</div>"
        '<div class="map-links">'
        '<a class="map-link-button" href="{1}" target="_blank" rel="noreferrer">Google My Mapsで開く</a>'
        "</div>"
    ).format(escape_text(embed_url), escape_text(view_url or embed_url))

    doc_html = (
        "<p>Google My Maps の埋め込み表示です。位置関係の確認はここ、細かい編集は My Maps 側で行います。</p>"
        "<ul>"
        "<li>ピン色やアイコン変更は My Maps 側のスタイル編集で行います。</li>"
        "<li>閲覧できない場合は地図の共有設定を確認してください。</li>"
        "</ul>"
    )
    return _build_section("地図", doc_html, content_html)


def _build_theme_css(theme: Dict[str, str]) -> str:
    return """
    :root {{
      --bg-top: {bg_top};
      --bg-bottom: {bg_bottom};
      --surface: {surface};
      --surface-strong: {surface_strong};
      --ink: {ink};
      --muted: {muted};
      --line: {line};
      --accent: {accent};
      --accent-soft: {accent_soft};
      --accent-soft-strong: {accent_soft_strong};
      --gold: {gold};
      --green: {green};
      --blue: {blue};
      --card-glow: {card_glow};
      --card-blush: {card_blush};
      --shadow: {shadow};
      --hero-border: {hero_border};
      --tab-surface: {tab_surface};
      --table-head: {table_head};
      --radius-xl: 28px;
      --radius-lg: 18px;
      --radius-md: 12px;
      --serif: {serif};
      --sans: {sans};
    }}
    """.format(**theme)


def build_dashboard(output_path=DASHBOARD_OUTPUT_PATH) -> Path:
    trip = load_trip_config(CONFIG_PATH)
    theme = _resolve_theme(trip)
    sightseeing_rows = load_and_validate_sightseeing(SIGHTSEEING_PATH)
    hotel_rows = _load_optional_rows(HOTEL_PATH)
    restaurant_rows = _load_optional_rows(RESTAURANT_PATH)
    transport_rows = _load_optional_rows(TRANSPORT_PATH)
    docs = {key: read_markdown(path) for key, _, path in DOC_TAB_FILES}

    sections = [
        {
            "id": "overview",
            "label": "概要",
            "body": _build_overview_section(trip, docs, sightseeing_rows, theme),
        },
        {
            "id": "map",
            "label": "地図",
            "body": _build_map_embed_section(trip),
        },
        {
            "id": "itinerary",
            "label": "旅程表",
            "body": _build_section(
                "旅程表", markdown_to_html(docs["itinerary"]), _build_day_cards(sightseeing_rows)
            ),
        },
        {
            "id": "sightseeing",
            "label": "観光候補",
            "body": _build_section(
                "観光候補",
                markdown_to_html(docs["sightseeing_doc"]),
                _build_sightseeing_table(sightseeing_rows),
            ),
        },
        {
            "id": "hotels",
            "label": "宿泊候補",
            "body": _build_section(
                "宿泊候補",
                markdown_to_html(docs["hotels_doc"]),
                _build_simple_table(
                    hotel_rows,
                    [
                        ("name", "宿名"),
                        ("area", "エリア"),
                        ("priority", "優先度"),
                        ("price_note", "価格メモ"),
                        ("memo", "メモ"),
                    ],
                    "未登録",
                ),
            ),
        },
        {
            "id": "restaurants",
            "label": "食事候補",
            "body": _build_section(
                "食事候補",
                markdown_to_html(docs["restaurants_doc"]),
                _build_simple_table(
                    restaurant_rows,
                    [
                        ("name", "店名"),
                        ("area", "エリア"),
                        ("category", "カテゴリ"),
                        ("day_candidate", "日程候補"),
                        ("birthday_score", "誕生日向き"),
                        ("memo", "メモ"),
                    ],
                    "未登録",
                ),
            ),
        },
        {
            "id": "transport",
            "label": "移動",
            "body": _build_section(
                "移動",
                markdown_to_html(docs["transport_doc"]),
                _build_simple_table(
                    transport_rows,
                    [
                        ("from_area", "出発"),
                        ("to_area", "到着"),
                        ("mode", "移動手段"),
                        ("estimated_minutes", "目安分"),
                        ("notes", "メモ"),
                    ],
                    "未登録",
                ),
            ),
        },
        {
            "id": "budget",
            "label": "予算",
            "body": _build_section("予算", markdown_to_html(docs["budget_doc"]), render_empty_state("未登録")),
        },
        {
            "id": "reservations",
            "label": "予約・ToDo",
            "body": _build_section(
                "予約・ToDo",
                markdown_to_html(docs["reservations_doc"]),
                _build_reservation_review(sightseeing_rows),
            ),
        },
        {
            "id": "birthday",
            "label": "誕生日演出",
            "body": _build_section(
                "誕生日演出",
                markdown_to_html(docs["birthday_doc"]),
                _build_birthday_focus(sightseeing_rows),
            ),
        },
        {
            "id": "notes",
            "label": "メモ",
            "body": _build_section(
                "メモ",
                markdown_to_html(docs["notes_doc"]),
                '<div class="inline-note">My Maps CSV 出力先: {0}</div>'.format(
                    escape_text(str(MYMAPS_OUTPUT_PATH))
                ),
            ),
        },
    ]

    nav_html = "".join(
        '<button class="tab-button{0}" data-tab="{1}">{2}</button>'.format(
            " is-active" if index == 0 else "",
            escape_text(section["id"]),
            escape_text(section["label"]),
        )
        for index, section in enumerate(sections)
    )
    section_html = "".join(
        '<section id="{0}" class="tab-panel{1}">{2}</section>'.format(
            escape_text(section["id"]),
            " is-active" if index == 0 else "",
            section["body"],
        )
        for index, section in enumerate(sections)
    )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_output = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    {theme_css}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: var(--sans);
      color: var(--ink);
      background:
        radial-gradient(circle at top right, var(--card-glow), transparent 28%),
        radial-gradient(circle at bottom left, var(--card-blush), transparent 34%),
        linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
    }}

    .shell {{
      position: relative;
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 16px 56px;
    }}

    .shell::before,
    .shell::after {{
      content: "";
      position: fixed;
      width: 220px;
      height: 220px;
      border-radius: 999px;
      pointer-events: none;
      z-index: 0;
      filter: blur(2px);
      opacity: 0.55;
    }}

    .shell::before {{
      top: 70px;
      right: -70px;
      background: radial-gradient(circle, var(--accent-soft-strong) 0%, transparent 68%);
    }}

    .shell::after {{
      bottom: 40px;
      left: -90px;
      background: radial-gradient(circle, rgba(214, 163, 91, 0.18) 0%, transparent 68%);
    }}

    .topbar {{
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
      color: var(--muted);
      font-size: 14px;
    }}

    .topbar strong {{
      color: var(--ink);
    }}

    .tabs {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      gap: 10px;
      overflow-x: auto;
      padding: 14px 0 18px;
      backdrop-filter: blur(12px);
    }}

    .tab-button {{
      border: 1px solid var(--line);
      background: var(--tab-surface);
      color: var(--muted);
      padding: 10px 16px;
      border-radius: 999px;
      cursor: pointer;
      white-space: nowrap;
      transition: transform 140ms ease, background 140ms ease, color 140ms ease;
      font-weight: 600;
    }}

    .tab-button:hover {{
      transform: translateY(-1px);
    }}

    .tab-button.is-active {{
      background: var(--accent);
      color: white;
      border-color: transparent;
    }}

    .tab-panel {{
      display: none;
      animation: fadeIn 220ms ease;
    }}

    .tab-panel.is-active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero,
    .content-card {{
      position: relative;
      z-index: 1;
      background: var(--surface);
      border: 1px solid var(--hero-border);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow);
      padding: 22px;
      margin-bottom: 20px;
    }}

    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.9fr);
      gap: 18px;
      overflow: hidden;
    }}

    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -40px -60px auto;
      width: 220px;
      height: 220px;
      background:
        radial-gradient(circle at 35% 35%, var(--accent-soft-strong) 0 22%, transparent 24%),
        radial-gradient(circle at 60% 60%, rgba(214, 163, 91, 0.14) 0 15%, transparent 18%);
      transform: rotate(-10deg);
      opacity: 0.9;
      pointer-events: none;
    }}

    .eyebrow {{
      margin: 0 0 8px;
      color: var(--accent);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-size: 12px;
      font-weight: 700;
    }}

    .hero-tag {{
      display: inline-flex;
      align-items: center;
      padding: 7px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.1em;
      margin-bottom: 12px;
    }}

    h1, h2, h3 {{
      font-family: var(--serif);
      margin: 0 0 12px;
      line-height: 1.2;
    }}

    h1 {{
      font-size: clamp(30px, 6vw, 46px);
    }}

    h2 {{
      font-size: 24px;
    }}

    h3 {{
      font-size: 18px;
    }}

    p, li {{
      line-height: 1.7;
    }}

    .hero-summary {{
      font-size: 16px;
      color: var(--muted);
      max-width: 760px;
    }}

    .hero-summary-soft {{
      font-size: 17px;
      line-height: 1.85;
    }}

    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0;
    }}

    .hero-meta span,
    .chip {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid var(--line);
      font-size: 13px;
      color: var(--muted);
    }}

    .chip-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .hero-side {{
      display: grid;
      gap: 14px;
      align-content: start;
    }}

    .hero-note {{
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.72));
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 18px;
    }}

    .hero-note p {{
      margin: 8px 0 0;
      color: var(--muted);
    }}

    .section-mini-label {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}

    .stats-section {{
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.68));
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 18px;
    }}

    .stats-grid,
    .day-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }}

    .day-grid {{
      margin-bottom: 20px;
    }}

    .stat-card,
    .day-card {{
      background: var(--surface-strong);
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 18px;
    }}

    .stat-label {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}

    .stat-value {{
      font-family: var(--serif);
      font-size: 34px;
      color: var(--accent);
    }}

    .section-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 10px;
    }}

    .section-copy {{
      color: var(--muted);
      margin-bottom: 18px;
    }}

    .section-copy ul {{
      padding-left: 18px;
    }}

    .table-wrap {{
      overflow-x: auto;
      border-radius: var(--radius-lg);
      border: 1px solid var(--line);
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
      background: rgba(255, 255, 255, 0.66);
    }}

    .data-table th,
    .data-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}

    .data-table th {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
      background: var(--table-head);
      position: sticky;
      top: 0;
    }}

    .data-table a {{
      color: var(--blue);
      text-decoration: none;
      font-weight: 700;
    }}

    .data-table tbody tr:hover {{
      background: rgba(255, 255, 255, 0.95);
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 5px 10px;
      margin-right: 6px;
      margin-bottom: 6px;
      font-size: 12px;
      font-weight: 700;
    }}

    .badge-priority-s {{ background: rgba(177, 77, 50, 0.18); color: #8d2f1a; }}
    .badge-priority-a {{ background: rgba(198, 149, 45, 0.18); color: #86621a; }}
    .badge-priority-b {{ background: rgba(51, 92, 129, 0.14); color: #244969; }}
    .badge-priority-c {{ background: rgba(95, 108, 118, 0.14); color: #48535b; }}
    .badge-heat-high {{ background: rgba(209, 68, 68, 0.16); color: #9d2d2d; }}
    .badge-heat-mid {{ background: rgba(198, 149, 45, 0.18); color: #7f6118; }}
    .badge-heat-low {{ background: rgba(44, 107, 79, 0.14); color: #23513b; }}
    .badge-rain-good {{ background: rgba(44, 107, 79, 0.14); color: #23513b; }}
    .badge-rain-mid {{ background: rgba(51, 92, 129, 0.14); color: #244969; }}
    .badge-rain-bad {{ background: rgba(95, 108, 118, 0.14); color: #48535b; }}
    .badge-birthday-high {{ background: rgba(177, 77, 50, 0.15); color: #8d2f1a; }}
    .badge-birthday-mid {{ background: rgba(198, 149, 45, 0.15); color: #86621a; }}

    .empty-state,
    .inline-note {{
      border: 1px dashed var(--line);
      border-radius: var(--radius-md);
      padding: 14px;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.55);
    }}

    .map-frame-wrap {{
      overflow: hidden;
      border-radius: var(--radius-lg);
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.7);
      min-height: 560px;
    }}

    .map-frame {{
      display: block;
      width: 100%;
      height: 560px;
      border: 0;
    }}

    .map-links {{
      margin-top: 14px;
    }}

    .map-link-button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      text-decoration: none;
      color: white;
      background: var(--blue);
      font-weight: 700;
    }}

    .candidate-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 14px;
    }}

    .candidate-name {{
      font-weight: 700;
      margin-bottom: 8px;
    }}

    .candidate-memo {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .footer {{
      margin-top: 28px;
      color: var(--muted);
      text-align: center;
      font-size: 13px;
    }}

    @media (max-width: 720px) {{
      .shell {{
        padding: 16px 12px 40px;
      }}

      .hero,
      .content-card {{
        padding: 18px;
        border-radius: 18px;
      }}

      .hero {{
        grid-template-columns: 1fr;
      }}

      .topbar {{
        flex-direction: column;
        align-items: flex-start;
      }}

      .data-table {{
        min-width: 640px;
      }}

      .map-frame-wrap,
      .map-frame {{
        min-height: 420px;
        height: 420px;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <div class="topbar">
      <div><strong>{title}</strong></div>
      <div>{topbar_label} · {generated_prefix}: {generated_at}</div>
    </div>
    <nav class="tabs" aria-label="Travel dashboard tabs">
      {nav_html}
    </nav>
    {section_html}
    <footer class="footer">{footer}</footer>
  </main>
  <script>
    (function () {{
      var buttons = document.querySelectorAll(".tab-button");
      var panels = document.querySelectorAll(".tab-panel");

      function activate(tabId) {{
        buttons.forEach(function (button) {{
          button.classList.toggle("is-active", button.getAttribute("data-tab") === tabId);
        }});
        panels.forEach(function (panel) {{
          panel.classList.toggle("is-active", panel.id === tabId);
        }});
      }}

      buttons.forEach(function (button) {{
        button.addEventListener("click", function () {{
          activate(button.getAttribute("data-tab"));
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
      }});
    }})();
  </script>
</body>
</html>
""".format(
        title=escape_text(trip.get("trip_name", "Travel Dashboard")),
        theme_css=_build_theme_css(theme),
        topbar_label=escape_text(theme["topbar_label"]),
        generated_prefix=escape_text(theme["generated_prefix"]),
        generated_at=escape_text(generated_at),
        nav_html=nav_html,
        section_html=section_html,
        footer=escape_text(theme["footer"]),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_output, encoding="utf-8")
    if output_path != PAGES_INDEX_OUTPUT_PATH:
        PAGES_INDEX_OUTPUT_PATH.write_text(html_output, encoding="utf-8")
    if output_path != ROOT_INDEX_OUTPUT_PATH:
        ROOT_INDEX_OUTPUT_PATH.write_text(html_output, encoding="utf-8")
    return output_path


def main() -> int:
    output_path = build_dashboard()
    print("Generated dashboard HTML: {0}".format(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

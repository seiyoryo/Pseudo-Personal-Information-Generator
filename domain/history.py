from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class HistoryNode:
    """One generated dataset node (dummyN)."""

    number: int  # 1-based
    children: List["HistoryNode"]
    # ratio_from_parent is percent (0-100). Root has None.
    ratio_from_parent: Optional[float] = None


def _build_tree(
    now: int,
    archived_data: Dict[str, Any],
    ratio_from_parent: Optional[float] = None,
) -> HistoryNode:
    key = str(now)
    child_dict = archived_data.get(key, {}).get("child", {}) or {}
    children: List[HistoryNode] = []
    for child_str, ratio in child_dict.items():
        try:
            child_n = int(child_str)
        except ValueError:
            continue
        # ratio is stored as int weight; normalize later at parent level? (legacy)
        # In legacy UI, the ratio displayed is the raw weight. We'll keep it as-is.
        children.append(_build_tree(child_n, archived_data, ratio_from_parent=float(ratio)))
    # Legacy stores child numbers in reverse-ish; keep stable ordering by number desc for readability.
    children.sort(key=lambda n: n.number, reverse=True)
    return HistoryNode(number=now, children=children, ratio_from_parent=ratio_from_parent)


def build_history_forest(archived_data: Dict[str, Any], max_number: int) -> List[HistoryNode]:
    """Build nodes for history display.

    We build from the latest node down, using `child` links as edges.
    """

    if max_number <= 0:
        return []
    # In current app, the latest dummy is max_number and is the root for display.
    return [_build_tree(max_number, archived_data)]


def render_history_html(nodes: List[HistoryNode], figure_base_url: str = "/outputs/figure") -> str:
    """Render HTML <li>...</li> fragments for history_trees.html.

    This avoids writing template files at runtime.
    """

    def render_node(node: HistoryNode, indent: int = 0) -> str:
        sp = " " * indent
        html = f"{sp}<li>\n"
        html += f'{sp} <div style="display: flex;border: 2px solid; width:560px; padding: 0px 0px; margin: 10px 0px">\n'
        html += f'{sp}    <div style =" width: 40px; vertical-align: middle; text-align: center;">\n'
        html += f'{sp}       <div style="border: 2px background: green;">\n'
        html += f'{sp}          <font size="3"> {node.number} </font><br>\n'
        if node.ratio_from_parent is not None:
            html += f'{sp}          <font size="1">-------</font><br>\n'
            html += f"{sp}          {node.ratio_from_parent}\n"
        html += f"{sp}       </div>\n"
        html += f'{sp}       <form action="/export_dummy_by_number" method="POST">\n'
        html += f'{sp}         <input type="image" name ="df_num" value={node.number} src="../static/images/download-icon.jpg" style="border: double;" height="30"/>\n'
        html += f"{sp}       </form>\n"
        html += f"{sp}    </div>\n"
        html += f'{sp}    <img src="{figure_base_url}/d_copied_dummy/{node.number}/age.png" width="150" style="padding: 7px 10px 0px;">\n'
        html += f'{sp}    <img src="{figure_base_url}/d_copied_dummy/{node.number}/blood.png" width="150" style="padding: 7px 10px 0px;">\n'
        html += f'{sp}    <img src="{figure_base_url}/d_copied_dummy/{node.number}/sex.png" width="150" style="padding: 7px 10px 0px;">\n'
        html += f"{sp} </div>\n"
        if node.children:
            html += f"{sp} <ul>\n"
            for child in node.children:
                html += render_node(child, indent + 2)
            html += f"{sp} </ul>\n"
        html += f"{sp}</li>\n"
        return html

    return "".join(render_node(n, 0) for n in nodes)


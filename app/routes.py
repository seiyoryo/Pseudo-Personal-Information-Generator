from __future__ import annotations

from pathlib import Path

from typing import Union

from flask import Blueprint, Response, abort, render_template, request, send_from_directory
import pandas as pd

from .persistence import Persistence
from .services import AppService


bp = Blueprint("routes", __name__)


def _svc() -> AppService:
    p = Persistence()
    p.ensure_dirs()
    return AppService(p)


@bp.route("/", methods=["GET", "POST"])
def form() -> Union[Response, str]:
    if request.method == "GET":
        return render_template("main_screen.html")

    # POST
    form_dict = request.form.to_dict(flat=True)
    form_dict["info"] = request.form.getlist("info")
    _, ctx = _svc().generate_initial(form_dict)
    return render_template("comformation.html", **ctx)


@bp.get("/export")
def export_action() -> Response:
    p = Persistence()
    basic_path = p.paths.outputs_df_dir
    return send_from_directory(
        directory=str(basic_path),
        path="created_dummy_new.csv",
        as_attachment=True,
        download_name="dummy.csv",
    )


@bp.get("/export_copied_dummy")
def export_dummy_action() -> Response:
    p = Persistence()
    df_data = p.load_df_data()
    if not df_data:
        abort(400, description="状態ファイルが見つかりません。先にデータ生成を実行してください。")
    cumulated_number = int(df_data.get("cumulated_number", 0))
    if cumulated_number <= 0:
        abort(400, description="コピー済みデータがありません。先に分布コピーを実行してください。")
    return send_from_directory(
        directory=str(p.paths.outputs_df_dir),
        path=f"dummy{cumulated_number}.csv",
        as_attachment=True,
        download_name="copied_dummy.csv",
    )


@bp.post("/export_dummy_by_number")
def export_dummy_by_number() -> Response:
    df_num = request.form.get("df_num")
    if not df_num:
        abort(400, description="df_num が指定されていません。")
    p = Persistence()
    return send_from_directory(
        directory=str(p.paths.outputs_df_dir),
        path=f"dummy{df_num}.csv",
        as_attachment=True,
        download_name=f"dummy{df_num}.csv",
    )


@bp.post("/copy_distribution")
def copy_distribution_display() -> str:
    ctx = _svc().copy_distribution(request.form.to_dict(flat=True))
    return render_template("comf3exp.html", **ctx)


@bp.post("/copy_distribution_by_ratio")
def copy_distribution_by_ratio_display() -> str:
    ctx = _svc().copy_distribution_by_ratio(request.form.to_dict(flat=True))
    return render_template("comf3exp.html", **ctx)


@bp.post("/make_mixture_distribution")
def make_mixture_distribution() -> str:
    form = request.form.to_dict(flat=True)
    form["data"] = request.form.getlist("data")
    ctx = _svc().make_mixture_distribution(form)
    return render_template("comf3exp.html", **ctx)


@bp.get("/history_tree")
def show_history_tree() -> str:
    ctx = _svc().history_tree()
    # history_trees.html will be updated to embed tree_html.
    return render_template("history_trees.html", **ctx)


@bp.get("/just_display")
def just_display() -> str:
    res = _svc().just_display()
    return render_template(res["template"], **res["context"])


@bp.get("/display_extension")
def display_extension() -> str:
    return render_template("extension.html")


@bp.post("/get_base_data")
def export_extended_data() -> Response:
    row_num = int(request.form["row"])
    f = request.files["base"]
    base_df = pd.read_csv(f)
    out_path = _svc().extend_data(base_df, row_num)
    return send_from_directory(
        directory=str(out_path.parent),
        path=out_path.name,
        as_attachment=True,
        download_name="tdf.csv",
    )


@bp.get("/outputs/<path:relpath>")
def outputs_file(relpath: str) -> Response:
    """Serve generated artifacts under outputs/ (figures etc)."""
    p = Persistence()
    # Restrict to outputs directory
    return send_from_directory(
        directory=str(p.paths.outputs_dir),
        path=relpath,
        as_attachment=False,
    )


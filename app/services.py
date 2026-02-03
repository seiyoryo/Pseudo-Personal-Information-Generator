from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from domain import distribution as dist
from domain import extension as ext
from domain import generate as gen
from domain import history as hist
from domain import statistics as stats

from .persistence import Persistence


@dataclass(frozen=True)
class UiTable:
    header: List[str]
    record: List[List[Any]]


class AppService:
    def __init__(self, persistence: Persistence) -> None:
        self._p = persistence

    # ----------------------------
    # Initial generation
    # ----------------------------
    def generate_initial(self, form: Dict[str, Any]) -> Tuple[UiTable, Dict[str, Any]]:
        """Create the initial dataset and its figures.

        Returns: (table, template_context)
        """

        row_number = int(form["row"])
        age_start = int(form["age_start"])
        age_end = int(form["age_end"])
        compony_start = int(form["compony_start"])
        compony_end = int(form["compony_end"])
        necessary_columns = list(form.get("info", []))

        df_data: Dict[str, Any] = dict(form)
        df_data["info"] = necessary_columns
        df_data["cumulated_number"] = 0
        self._p.save_df_data(df_data)
        self._p.save_archived_data({})

        df = gen.generate_df(
            columns=_COLUMNS,
            row_number=row_number,
            necessary_columns=necessary_columns,
            age_start=age_start,
            age_end=age_end,
            compony_start=compony_start,
            compony_end=compony_end,
        )

        # created_dummy_new.csv has no index in legacy
        self._p.write_outputs_csv(df, "created_dummy_new.csv", index=False)

        # figures: reset outputs/figure/dummy
        dummy_dir = self._p.figure_dir_dummy()
        if dummy_dir.exists():
            shutil.rmtree(dummy_dir)
        dummy_dir.mkdir(parents=True, exist_ok=True)

        self._write_basic_figures(df, dummy_dir)

        table = UiTable(header=list(df.columns), record=df.values.tolist())
        ctx = {
            "header": table.header,
            "record": table.record,
            "age_adaption": 0.4,
            "blood_adaption": 0.1,
            "sex_adaption": 0.1,
        }
        return table, ctx

    # ----------------------------
    # Copy distribution (adaption)
    # ----------------------------
    def copy_distribution(self, adaption_form: Dict[str, Any]) -> Dict[str, Any]:
        df_data = self._p.load_df_data()
        (
            row_number,
            age_start,
            age_end,
            compony_start,
            compony_end,
            necessary_columns,
            cumulated_number,
        ) = gen.sent_data_to_info(df_data)

        now_df_number = int(cumulated_number) + 1
        df_data["cumulated_number"] = now_df_number
        self._p.save_df_data(df_data)

        this_archived_data = gen.return_this_archived_data(now_df_number)

        age_adaption = 1 - float(adaption_form["age_adaption"])
        blood_adaption = 1 - float(adaption_form["blood_adaption"])
        sex_adaption = 1 - float(adaption_form["sex_adaption"])

        original_df = self._p.read_outputs_csv("created_dummy_new.csv")

        age_list = dist.create_age_list(age_start, age_end)
        blood_cumu, blood_origin = dist.calculate_distribution_cumulative(original_df, _BLOOD_LIST, "血液型")
        age_cumu, age_origin = dist.calculate_distribution_cumulative(original_df, age_list, "年齢")
        sex_cumu, sex_origin = dist.calculate_distribution_cumulative(original_df, _SEX_LIST, "性別")

        df = gen.distribution_copied_df_stablized(
            _COLUMNS,
            row_number,
            necessary_columns,
            age_start,
            age_end,
            compony_start,
            compony_end,
            blood_cumu,
            blood_origin,
            blood_adaption,
            age_cumu,
            age_origin,
            age_adaption,
            sex_cumu,
            sex_origin,
            sex_adaption,
        )

        # legacy: dummyN.csv includes index column
        self._p.write_outputs_csv(df, f"dummy{now_df_number}.csv", index=True)

        copied_root = self._p.figure_dir_copied_dummy_root()
        copied_root.mkdir(parents=True, exist_ok=True)
        this_figure_path = self._p.figure_dir_copied_dummy_n(now_df_number)
        this_figure_path.mkdir(parents=True, exist_ok=True)

        abs_statistics, this_archived_data, blood_ratio_list, sex_ratio_list = stats.save_image_and_return_statistics(
            age_list,
            age_end,
            age_start,
            df,
            original_df,
            str(this_figure_path) + "\\",  # legacy expects string path ending with separator
            this_archived_data,
            now_df_number,
        )

        archived_data = self._p.load_archived_data()
        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        self._p.save_archived_data(archived_data)

        df_number_list = [str(i + 1) for i in range(now_df_number)]
        return {
            "header": list(original_df.columns),
            "record": original_df.values.tolist(),
            "copied_df_header": list(df.columns),
            "copied_df_record": df.values.tolist(),
            "now_df_number": str(now_df_number),
            "df_number_list": df_number_list,
            "abs_statistics": abs_statistics,
            "age_adaption": round(1 - age_adaption, 2),
            "blood_ratio_list": blood_ratio_list,
            "blood_adaption": round(1 - blood_adaption, 2),
            "sex_ratio_list": sex_ratio_list,
            "sex_adaption": round(1 - sex_adaption, 2),
        }

    # ----------------------------
    # Copy distribution (ratio)
    # ----------------------------
    def copy_distribution_by_ratio(self, form: Dict[str, Any]) -> Dict[str, Any]:
        df_data = self._p.load_df_data()
        (
            row_number,
            age_start,
            age_end,
            compony_start,
            compony_end,
            necessary_columns,
            cumulated_number,
        ) = gen.sent_data_to_info(df_data)

        now_df_number = int(cumulated_number) + 1
        df_data["cumulated_number"] = now_df_number
        self._p.save_df_data(df_data)

        this_archived_data = gen.return_this_archived_data(now_df_number)

        if_age_random = True if form.get("random") == "random" else False
        age_distribution_type = form.get("distribution_type")
        age_median = "" if form.get("median", "") == "" else float(form["median"])
        age_var = "" if form.get("var", "") == "" else float(form["var"])
        age_beta = "" if form.get("beta", "") == "" else float(form["beta"])

        blood_ratio_list = [float(form["a_ratio"]), float(form["b_ratio"]), float(form["ab_ratio"]), float(form["o_ratio"])]
        s = sum(blood_ratio_list) or 1.0
        blood_ratio_list = [x / s for x in blood_ratio_list]

        sex_ratio_list = [float(form["man_ratio"]), float(form["woman_ratio"]), float(form["others_ratio"])]
        s2 = sum(sex_ratio_list) or 1.0
        sex_ratio_list = [x / s2 for x in sex_ratio_list]

        original_df = self._p.read_outputs_csv("created_dummy_new.csv")
        age_list = dist.create_age_list(age_start, age_end)
        blood_cumu, blood_origin = dist.calculate_distribution_cumulative(original_df, _BLOOD_LIST, "血液型")
        age_cumu, age_origin = dist.calculate_distribution_cumulative(original_df, age_list, "年齢")
        sex_cumu, sex_origin = dist.calculate_distribution_cumulative(original_df, _SEX_LIST, "性別")

        df = gen.ratio_copied_df_stablized_age_specified(
            _COLUMNS,
            row_number,
            necessary_columns,
            age_start,
            age_end,
            compony_start,
            compony_end,
            blood_cumu,
            blood_origin,
            blood_ratio_list,
            age_cumu,
            age_origin,
            sex_cumu,
            sex_origin,
            sex_ratio_list,
            if_age_random,
            age_distribution_type,
            age_median,
            age_var,
            age_beta,
        )

        self._p.write_outputs_csv(df, f"dummy{now_df_number}.csv", index=True)

        copied_root = self._p.figure_dir_copied_dummy_root()
        copied_root.mkdir(parents=True, exist_ok=True)
        this_figure_path = self._p.figure_dir_copied_dummy_n(now_df_number)
        this_figure_path.mkdir(parents=True, exist_ok=True)

        abs_statistics, this_archived_data, blood_ratio_list2, sex_ratio_list2 = stats.save_image_and_return_statistics(
            age_list,
            age_end,
            age_start,
            df,
            original_df,
            str(this_figure_path) + "\\",
            this_archived_data,
            now_df_number,
        )

        archived_data = self._p.load_archived_data()
        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        self._p.save_archived_data(archived_data)

        df_number_list = [str(i + 1) for i in range(now_df_number)]
        return {
            "header": list(original_df.columns),
            "record": original_df.values.tolist(),
            "copied_df_header": list(df.columns),
            "copied_df_record": df.values.tolist(),
            "now_df_number": str(now_df_number),
            "df_number_list": df_number_list,
            "abs_statistics": abs_statistics,
            "age_adaption": 0.4,
            "blood_ratio_list": blood_ratio_list2,
            "blood_adaption": 0.1,
            "sex_ratio_list": sex_ratio_list2,
            "sex_adaption": 0.1,
        }

    # ----------------------------
    # Mixture distribution
    # ----------------------------
    def make_mixture_distribution(self, form: Dict[str, Any]) -> Dict[str, Any]:
        df_data = self._p.load_df_data()
        (
            row_number,
            age_start,
            age_end,
            compony_start,
            compony_end,
            necessary_columns,
            cumulated_number,
        ) = gen.sent_data_to_info(df_data)

        now_df_number = int(cumulated_number) + 1
        df_data["cumulated_number"] = now_df_number
        self._p.save_df_data(df_data)
        this_archived_data = gen.return_this_archived_data(now_df_number)

        df_checked_list = list(form.get("data", []))
        df_ratio_list: List[int] = []
        for key in df_checked_list:
            df_ratio_list.append(int(form[f"{key}ratio"]))

        archived_data = self._p.load_archived_data()

        age_y_list = [0.0] * (age_end - age_start + 1)
        blood_y_list = [0.0] * 4
        sex_y_list = [0.0] * 3
        s = sum(df_ratio_list) or 1.0

        for i, df_num in enumerate(df_checked_list):
            a = archived_data[df_num]["ages"]
            b = archived_data[df_num]["bloods"]
            c = archived_data[df_num]["sexes"]
            w = df_ratio_list[i] / s
            age_y_list = [age_y_list[j] + a[j] * w for j in range(len(age_y_list))]
            blood_y_list = [blood_y_list[j] + b[j] * w for j in range(len(blood_y_list))]
            sex_y_list = [sex_y_list[j] + c[j] * w for j in range(len(sex_y_list))]

        age_y_list = [round(x) for x in age_y_list]
        blood_y_list = [round(x) for x in blood_y_list]
        sex_y_list = [round(x) for x in sex_y_list]

        # Adjust to match row_number
        age_y_list[0] += row_number - sum(age_y_list)
        blood_y_list[0] += row_number - sum(blood_y_list)
        sex_y_list[0] += row_number - sum(sex_y_list)

        original_df = self._p.read_outputs_csv("created_dummy_new.csv")
        age_list = dist.create_age_list(age_start, age_end)
        blood_cumu, blood_origin = dist.calculate_distribution_cumulative(original_df, _BLOOD_LIST, "血液型")
        age_cumu, age_origin = dist.calculate_distribution_cumulative(original_df, age_list, "年齢")
        sex_cumu, sex_origin = dist.calculate_distribution_cumulative(original_df, _SEX_LIST, "性別")

        df = gen.make_df_from_abs_box(
            _COLUMNS,
            row_number,
            necessary_columns,
            age_start,
            age_end,
            compony_start,
            compony_end,
            blood_cumu,
            blood_y_list,
            age_cumu,
            age_y_list,
            sex_cumu,
            sex_y_list,
        )

        self._p.write_outputs_csv(df, f"dummy{now_df_number}.csv", index=True)

        copied_root = self._p.figure_dir_copied_dummy_root()
        copied_root.mkdir(parents=True, exist_ok=True)
        this_figure_path = self._p.figure_dir_copied_dummy_n(now_df_number)
        this_figure_path.mkdir(parents=True, exist_ok=True)

        abs_statistics, this_archived_data, blood_ratio_list, sex_ratio_list = stats.save_image_and_return_statistics(
            age_list,
            age_end,
            age_start,
            df,
            original_df,
            str(this_figure_path) + "\\",
            this_archived_data,
            now_df_number,
        )

        for i, df_num in enumerate(df_checked_list):
            this_archived_data[str(now_df_number)]["child"][df_num] = df_ratio_list[i]

        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        self._p.save_archived_data(archived_data)

        df_number_list = [str(i + 1) for i in range(now_df_number)]
        return {
            "header": list(original_df.columns),
            "record": original_df.values.tolist(),
            "copied_df_header": list(df.columns),
            "copied_df_record": df.values.tolist(),
            "now_df_number": str(now_df_number),
            "df_number_list": df_number_list,
            "abs_statistics": abs_statistics,
            "age_adaption": 0.4,
            "blood_ratio_list": blood_ratio_list,
            "blood_adaption": 0.1,
            "sex_ratio_list": sex_ratio_list,
            "sex_adaption": 0.1,
        }

    # ----------------------------
    # History view
    # ----------------------------
    def history_tree(self) -> Dict[str, Any]:
        df_data = self._p.load_df_data()
        cumulated_number = int(df_data.get("cumulated_number", 0) or 0)
        if cumulated_number <= 0:
            return {"tree_html": "", "has_history": False}

        archived_data = self._p.load_archived_data()
        nodes = hist.build_history_forest(archived_data, cumulated_number)
        tree_html = hist.render_history_html(nodes, figure_base_url="/outputs/figure")
        return {"tree_html": tree_html, "has_history": True}

    # ----------------------------
    # Just display
    # ----------------------------
    def just_display(self) -> Dict[str, Any]:
        df_data = self._p.load_df_data()
        (
            row_number,
            age_start,
            age_end,
            compony_start,
            compony_end,
            necessary_columns,
            cumulated_number,
        ) = gen.sent_data_to_info(df_data)

        now_df_number = int(cumulated_number)
        original_df = self._p.read_outputs_csv("created_dummy_new.csv")
        header = list(original_df.columns)
        record = original_df.values.tolist()

        if now_df_number == 0:
            return {
                "template": "comformation.html",
                "context": {"header": header, "record": record, "age_adaption": 0.4, "blood_adaption": 0.1, "sex_adaption": 0.1},
            }

        df = self._p.read_outputs_csv(f"dummy{now_df_number}.csv")
        this_figure_path = self._p.figure_dir_copied_dummy_n(now_df_number)
        age_list = dist.create_age_list(age_start, age_end)
        this_archived_data = gen.return_this_archived_data(now_df_number)
        abs_statistics, this_archived_data, blood_ratio_list, sex_ratio_list = stats.save_image_and_return_statistics(
            age_list,
            age_end,
            age_start,
            df,
            original_df,
            str(this_figure_path) + "\\",
            this_archived_data,
            now_df_number,
        )
        df_number_list = [str(i + 1) for i in range(now_df_number)]
        return {
            "template": "comf3exp.html",
            "context": {
                "header": header,
                "record": record,
                "copied_df_header": list(df.columns),
                "copied_df_record": df.values.tolist(),
                "now_df_number": str(now_df_number),
                "df_number_list": df_number_list,
                "abs_statistics": abs_statistics,
                "age_adaption": 0.4,
                "blood_ratio_list": blood_ratio_list,
                "blood_adaption": 0.1,
                "sex_ratio_list": sex_ratio_list,
                "sex_adaption": 0.1,
            },
        }

    # ----------------------------
    # Extension
    # ----------------------------
    def extend_data(self, base_df: pd.DataFrame, row_num: int) -> Path:
        tdf = ext.extended_generator(base_df, row_num)
        # legacy: tdf.csv saved without index
        return self._p.write_outputs_csv(tdf, "tdf.csv", index=False)

    # ----------------------------
    # Helpers
    # ----------------------------
    def _write_basic_figures(self, df: pd.DataFrame, figure_dir: Path) -> None:
        # 年齢
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["年齢"], bins=min(30, max(5, len(set(df["年齢"])))))
        ax.set_title("年齢分布")
        fig.tight_layout()
        fig.savefig(str(figure_dir / "age.png"), dpi=150)
        plt.close(fig)

        # 性別
        x_list = _SEX_LIST
        y_list = [df["性別"].value_counts()[x] if x in df["性別"].value_counts() else 0 for x in x_list]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(x_list, y_list)
        ax.set_title("性別分布")
        fig.tight_layout()
        fig.savefig(str(figure_dir / "sex.png"), dpi=150)
        plt.close(fig)

        # 血液型
        x_list = _BLOOD_LIST
        y_list = [df["血液型"].value_counts()[x] if x in df["血液型"].value_counts() else 0 for x in x_list]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(x_list, y_list)
        ax.set_title("血液型分布")
        fig.tight_layout()
        fig.savefig(str(figure_dir / "blood.png"), dpi=150)
        plt.close(fig)


_COLUMNS = [
    "氏名",
    "氏名（ひらがな）",
    "年齢",
    "生年月日",
    "性別",
    "血液型",
    "メアド",
    "電話番号",
    "携帯電話番号",
    "郵便番号",
    "住所",
    "会社名",
    "クレジットカード",
    "有効期限",
    "マイナンバー",
]
_BLOOD_LIST = ["A", "B", "AB", "O"]
_SEX_LIST = ["男", "女", "その他・不明"]


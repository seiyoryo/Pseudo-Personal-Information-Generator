# coding: UTF-8
# こちらも参考になる：https://qiita.com/5zm/items/760000cf63b176be544c
# 参照：https://koleoblog.info/flask_bootstrap_csv_dl/

from flask import Flask, jsonify, request, render_template, send_from_directory
import pandas as pd
import os
import generator
import matplotlib
from pathlib import Path
matplotlib.use('Agg')
import copy_distribution
import json
import io
import shutil
import plotly.graph_objs as go
import plotly.offline as plt
import statistics
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
import cgi

from werkzeug import secure_filename
from io import StringIO

columns = ["氏名","氏名（ひらがな）","年齢","生年月日","性別","血液型","メアド",
           "電話番号","携帯電話番号","郵便番号","住所","会社名",
           "クレジットカード","有効期限","マイナンバー"]
blood_list = ["A","B","AB","O"]
sex_list = ["男","女","その他・不明"]
 
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/export", methods=['GET',"POST"])
def export_action():
    if request.method == "GET":
        basic_path = os.getcwd()+"/"
        return send_from_directory(
            directory=basic_path + '/input/df/',
            filename='created_dummy_new.csv',
            as_attachment=True,
            attachment_filename='dummy.csv',
        )
    else:
        return render_template('comformation.html')

@app.route("/export_copied_dummy", methods=['GET',"POST"])
def export_dummy_action():
    with open('input/df_data.json') as f:
        df_data = json.load(f)
    row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
    if request.method == "GET":
        basic_path = os.getcwd()+"/"
        return send_from_directory(
            directory=basic_path + '/input/df',
            filename='dummy{}.csv'.format(cumulated_number),
            as_attachment=True,
            attachment_filename='copied_dummy.csv',
        )
    else:
        return render_template('comformation.html')
    
@app.route("/export_dummy_by_number", methods=['GET',"POST"])
def export_dummy_by_number():
    if request.method == "GET" or "POST":
        df_num = request.form['df_num']
        basic_path = os.getcwd()+"/"
        return send_from_directory(
            directory=basic_path + '/input/df',
            filename='dummy{}.csv'.format(df_num),
            as_attachment=True,
            attachment_filename='dummy{}.csv'.format(df_num),
        )
    else:
        return render_template('comformation.html')

@app.route('/', methods=['GET', 'POST'])
def form():
    # ２回目以降データが送られてきた時の処理
    # 初期画面→データ生成の機能
    if request.method == 'POST':
        row_number = int(request.form['row'])
        age_start,age_end = int(request.form['age_start']),int(request.form['age_end'])
        compony_start,compony_end = int(request.form['compony_start']),int(request.form['compony_end'])
        necessary_columns = request.form.getlist("info")
        # 下の3つのwithのうち上2つはrequestのjson化により解決可能だが、先延ばし。
        with open('input/df_data.json', 'w') as fp:
            json.dump(request.form, fp, indent=4, ensure_ascii=False)
        with open('input/df_data.json') as f:
            df_data = json.load(f)
            df_data["info"] = necessary_columns
            # 以下作った分布の回数
            df_data["cumulated_number"] = 0
        with open('input/df_data.json',"w") as f:
            json.dump(df_data, f, indent=4, ensure_ascii=False)
            
        archived_data = {}
        with open('input/variable_data_archived.json',"w") as v:
            json.dump(archived_data, v, indent=4, ensure_ascii=False)
        # リスト作り
        age_list = generator.create_age_list(age_start,age_end)
        blood_list = ["A","B","AB","O"]
        sex_list = ["男","女","その他・不明"]
        basic_path = os.getcwd()+"/"
        df = generator.generate_df(
            columns,
            row_number,necessary_columns,
            age_start,age_end,
            compony_start,compony_end
            )
        df_path = "{}input/df/created_dummy_new.csv".format(basic_path)
        df.to_csv(df_path,index=False)
        before_figure_path = "{}static/figure/".format(basic_path)
        figure_path = "{}static/figure/dummy/".format(basic_path)

        if os.path.exists(figure_path):
            print("\n\nhere1!!!!!")
            shutil.rmtree(before_figure_path)
        else:
            print("\n\nhere2")
        os.mkdir(before_figure_path)
        os.mkdir(figure_path)
        
        # ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
        # 年齢
        fig = go.Figure(data=[go.Histogram(x=df["年齢"])])
        fig.update_layout(title="年齢分布",title_x=0.5,font=dict(size=30))
        fig.write_image(figure_path+"age.png")
        
        # 性別
        x_list = sex_list
        y_list = [df["性別"].value_counts()[x_list[i]] if x_list[i] in df["性別"].value_counts() else 0 for i in range(len(x_list))]
        fig = go.Figure([go.Bar(x=x_list, y=y_list)])
        fig.update_layout(title="性別分布",title_x=0.5,font=dict(size=30))
        fig.write_image(figure_path+"sex.png")
        
        # 血液型
        x_list = blood_list
        y_list = [df["血液型"].value_counts()[x_list[i]] if x_list[i] in df["血液型"].value_counts() else 0 for i in range(len(x_list))]
        fig = go.Figure([go.Bar(x=x_list, y=y_list)])
        fig.update_layout(title="血液型分布",title_x=0.5,font=dict(size=30))
        fig.write_image(figure_path+"blood.png")
        
        # ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
        header = df.columns # DataFrameのカラム名の1次元配列のリスト
        record = df.values.tolist() # DataFrameのインデックスを含まない全レコードの2次元配列のリスト
        return render_template(
            'comformation.html', 
            header=header, 
            record=record,
            age_adaption = 0.4,
            blood_adaption = 0.1,
            sex_adaption = 0.1
            )
    else:
        return render_template('main_screen.html')

@app.route('/copy_distribution', methods=['GET', 'POST'])
def copy_distribution_display():
    # ２回目以降データが送られてきた時の処理
    if request.method == 'POST':
        # dfに関するデータ
        with open('input/df_data.json') as f:
            df_data = json.load(f)
        row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
        # 以下保存情報の内の「更新回数」
        now_df_number = cumulated_number + 1
        df_data["cumulated_number"] += 1
        with open('input/df_data.json',"w") as f:
            json.dump(df_data, f, indent=4, ensure_ascii=False)
        this_archived_data = generator.return_this_archived_data(now_df_number)
        # 類似度調整度数の伝達-----------------------------------
        age_adaption,blood_adaption,sex_adaption = 1-float(request.form['age_adaption']),1-float(request.form['blood_adaption']),1-float(request.form['sex_adaption'])
        # ------------------------
        basic_path = os.getcwd()+"/"    
        # ----------------------------------------------------------------------------------------------------
        # df作り
        original_df = pd.read_csv("input/df/created_dummy_new.csv")
        # リスト作り
        age_list = generator.create_age_list(age_start,age_end)
        # 分布の取得
        blood_cumu,blood_origin = copy_distribution.calculate_distribution_cumulative(original_df,blood_list,"血液型")
        age_cumu,age_origin = copy_distribution.calculate_distribution_cumulative(original_df,age_list,"年齢")
        sex_cumu,sex_origin = copy_distribution.calculate_distribution_cumulative(original_df,sex_list,"性別")
        
        # 類似度調整機能付き類似分布作成
        df = generator.distribution_copied_df_stablized(
            columns,row_number,necessary_columns,
            age_start,age_end,
            compony_start,compony_end,
            blood_cumu,blood_origin,blood_adaption,
            age_cumu,age_origin,age_adaption,
            sex_cumu,sex_origin,sex_adaption
            )
        
        df_path = "{}input/df/dummy{}.csv".format(basic_path,now_df_number)
        df.to_csv(df_path)
        copied_dummy_figure_path = "{}static/figure/d_copied_dummy/".format(basic_path)
        this_figure_path = "{}{}/".format(copied_dummy_figure_path,now_df_number)
        if not os.path.exists(copied_dummy_figure_path):
            os.mkdir(copied_dummy_figure_path)
        os.mkdir(this_figure_path)
        # 画像生成保存＆指標吐き出し
        abs_statistics,this_archived_data,blood_ratio_list,sex_ratio_list = generator.save_image_and_return_statistics(age_list,age_end,age_start,df,original_df,this_figure_path,this_archived_data,now_df_number)
        # データを伝える
        header = original_df.columns 
        record = original_df.values.tolist()
        copied_df_header = df.columns 
        copied_df_record = df.values.tolist()
        # dfの番号に沿ったリストを作る
        df_number_list = [str(i+1) for i in range(now_df_number)] 
        with open('input/variable_data_archived.json') as v:
            archived_data = json.load(v)
        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        with open('input/variable_data_archived.json',"w") as v:
            json.dump(archived_data, v, indent=4, ensure_ascii=False)
                
        return render_template('comf3exp.html',    
                               header = header, 
                               record = record, 
                               copied_df_header = copied_df_header,
                               copied_df_record = copied_df_record,
                               now_df_number = str(now_df_number),
                               df_number_list = df_number_list,
                               abs_statistics = abs_statistics,
                                # 年齢情報
                               age_adaption = Decimal(1-age_adaption).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                                # 血液型情報
                               blood_ratio_list = blood_ratio_list,
                               blood_adaption = Decimal(1-blood_adaption).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                                # 性別情報
                               sex_ratio_list = sex_ratio_list,
                               sex_adaption = Decimal(1-sex_adaption).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                               )
    else:
        return render_template('comformation.html')

@app.route('/copy_distribution_by_ratio', methods=['GET', 'POST'])
def copy_distribution_by_ratio_display():
    # ２回目以降データが送られてきた時の処理
    if request.method == 'POST':
        with open('input/df_data.json') as f:
            df_data = json.load(f)
        row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
        # 以下保存情報の内の「更新回数」
        now_df_number = cumulated_number + 1
        df_data["cumulated_number"] += 1
        this_archived_data = generator.return_this_archived_data(now_df_number)
        with open('input/df_data.json',"w") as f:
            json.dump(df_data, f, indent=4, ensure_ascii=False)
        # 類似度調整度数の伝達-----------------------------------
        # 年齢分布指定条件
        if_age_random = True if request.form.get('random') == "random" else False
        age_distribution_type = request.form.get('distribution_type')
        age_median = "" if request.form['median'] == "" else float(request.form['median'])
        age_var = "" if request.form['var'] == "" else float(request.form['var'])
        age_beta = "" if request.form['beta'] == "" else float(request.form['beta'])
        # 血液型分布指定条件
        a_ratio,b_ratio,ab_ratio,o_ratio = float(request.form['a_ratio']),float(request.form['b_ratio']),float(request.form['ab_ratio']),float(request.form['o_ratio'])
        blood_ratio_list = [a_ratio,b_ratio,ab_ratio,o_ratio]
        blood_ratio_list = [blood_ratio_list[i]/sum(blood_ratio_list) for i in range(len(blood_ratio_list))]
        # 性別分布指定条件
        man_ratio,woman_ratio,others_ratio = float(request.form['man_ratio']),float(request.form['woman_ratio']),float(request.form['others_ratio'])    
        sex_ratio_list = [man_ratio,woman_ratio,others_ratio]
        sex_ratio_list = [sex_ratio_list[i]/sum(sex_ratio_list) for i in range(len(sex_ratio_list))]
        # ------------------------
        basic_path = os.getcwd()+"/"    
        # ----------------------------------------------------------------------------------------------------
        # df作り
        original_df = pd.read_csv("input/df/created_dummy_new.csv")
        # リスト作り
        age_list = generator.create_age_list(age_start,age_end)
        # 分布の取得
        blood_cumu,blood_origin = copy_distribution.calculate_distribution_cumulative(original_df,blood_list,"血液型")
        age_cumu,age_origin = copy_distribution.calculate_distribution_cumulative(original_df,age_list,"年齢")
        sex_cumu,sex_origin = copy_distribution.calculate_distribution_cumulative(original_df,sex_list,"性別")
        
        df = generator.ratio_copied_df_stablized_age_specified(
            columns,
            row_number,
            necessary_columns,
            age_start,age_end,
            compony_start,compony_end,
            blood_cumu,blood_origin,blood_ratio_list,
            age_cumu,age_origin,
            sex_cumu,sex_origin,sex_ratio_list,
            if_age_random,age_distribution_type,age_median,age_var,age_beta
            )
        
        df_path = "{}input/df/dummy{}.csv".format(basic_path,now_df_number)
        df.to_csv(df_path)
        copied_dummy_figure_path = "{}static/figure/d_copied_dummy/".format(basic_path)
        this_figure_path = "{}{}/".format(copied_dummy_figure_path,now_df_number)
        
        if not os.path.exists(copied_dummy_figure_path):
            os.mkdir(copied_dummy_figure_path)
        os.mkdir(this_figure_path)
        # 以下、それぞれの特性において、図と分布類似度を算出するプログラム
        
        abs_statistics,this_archived_data,blood_ratio_list,sex_ratio_list = generator.save_image_and_return_statistics(age_list,age_end,age_start,df,original_df,this_figure_path,this_archived_data,now_df_number)
        
        # データを伝える
        header = original_df.columns 
        record = original_df.values.tolist()
        copied_df_header = df.columns 
        copied_df_record = df.values.tolist() 
        
        # dfの番号に沿ったリストを作る
        df_number_list = [str(i+1) for i in range(now_df_number)]
        
        with open('input/variable_data_archived.json') as v:
            archived_data = json.load(v)
        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        with open('input/variable_data_archived.json',"w") as v:
            json.dump(archived_data, v, indent=4, ensure_ascii=False)
        
        return render_template('comf3exp.html', 
                               header = header, 
                               record = record, 
                               copied_df_header = copied_df_header,
                               copied_df_record = copied_df_record,
                               now_df_number = str(now_df_number),
                               df_number_list = df_number_list,
                                # 統計情報
                               abs_statistics = abs_statistics,
                                # 年齢情報                                                        
                               age_adaption = 0.4,
                                # 血液型情報
                               blood_ratio_list = blood_ratio_list,
                               blood_adaption = 0.1,
                               # 性別情報
                               sex_ratio_list = sex_ratio_list,
                               sex_adaption = 0.1,
                               )
    else:
        return render_template('comformation.html')

@app.route('/make_mixture_distribution', methods=['GET', 'POST'])
def make_mixture_distribution():
    # ２回目以降データが送られてきた時の処理
    if request.method == 'POST':
        with open('input/df_data.json') as f:
            df_data = json.load(f)
        row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
        
        # 以下保存情報の内の「更新回数」
        now_df_number = cumulated_number + 1
        df_data["cumulated_number"] += 1
        this_archived_data = generator.return_this_archived_data(now_df_number)
        
        with open('input/df_data.json',"w") as f:
            json.dump(df_data, f, indent=4, ensure_ascii=False)
        
        # request.formからの条件取得-----------------------------------
        df_checked_list = request.form.getlist("data")
        df_ratio_list = []
        for i in df_checked_list:
            df_ratio_list.append(int(request.form[i+"ratio"]))
            
        #  ages,bloods,sexesにおいて重み付きのリストを算出したい
        with open('input/variable_data_archived.json') as v:
            archived_data = json.load(v)
        
        age_y_list = [0]*(age_end-age_start+1)
        blood_y_list = [0]*4
        sex_y_list = [0]*3
        s = sum(df_ratio_list)
                
        # iはつくられたｄfの数
        for i in range(len(df_checked_list)):
            age_y_list = [age_y_list[j] + archived_data[df_checked_list[i]]["ages"][j]*df_ratio_list[i]/s for j in range(len(age_y_list))]
            blood_y_list = [blood_y_list[j] + archived_data[df_checked_list[i]]["bloods"][j]*df_ratio_list[i]/s for j in range(len(blood_y_list))]
            sex_y_list = [sex_y_list[j] + archived_data[df_checked_list[i]]["sexes"][j]*df_ratio_list[i]/s for j in range(len(sex_y_list))]
        
        # 四捨五入
        age_y_list = [round(age_y_list[i]) for i in range(len(age_y_list))]
        blood_y_list = [round(blood_y_list[i]) for i in range(len(blood_y_list))]
        sex_y_list = [round(sex_y_list[i]) for i in range(len(sex_y_list))]
        
        # 足りないところを先頭にて埋める
        x = row_number - sum(age_y_list)
        y = row_number - sum(blood_y_list)
        z = row_number - sum(sex_y_list)
        
        age_y_list[0] += x
        blood_y_list[0] += y
        sex_y_list[0] += z
        
        # ------------------------
        basic_path = os.getcwd()+"/"    
        # ----------------------------------------------------------------------------------------------------
        # df作り
        original_df = pd.read_csv("input/df/created_dummy_new.csv")
        # リスト作り
        age_list = generator.create_age_list(age_start,age_end)
        # 分布の取得
        blood_cumu,blood_origin = copy_distribution.calculate_distribution_cumulative(original_df,blood_list,"血液型")
        age_cumu,age_origin = copy_distribution.calculate_distribution_cumulative(original_df,age_list,"年齢")
        sex_cumu,sex_origin = copy_distribution.calculate_distribution_cumulative(original_df,sex_list,"性別")
        
        df = generator.make_df_from_abs_box(
            columns,
            row_number,
            necessary_columns,
            age_start,age_end,
            compony_start,compony_end,
            blood_cumu,blood_y_list,
            age_cumu,age_y_list,
            sex_cumu,sex_y_list
            )
        
        df_path = "{}input/df/dummy{}.csv".format(basic_path,now_df_number)
        df.to_csv(df_path)
        # figure_path = "{}static/figure/d_copied_dummy/".format(basic_path)
        copied_dummy_figure_path = "{}static/figure/d_copied_dummy/".format(basic_path)
        this_figure_path = "{}{}/".format(copied_dummy_figure_path,now_df_number)
        
        if not os.path.exists(copied_dummy_figure_path):
            os.mkdir(copied_dummy_figure_path)
        os.mkdir(this_figure_path)
        
        # 以下、それぞれの特性において、図と分布類似度を算出するプログラム
        abs_statistics,this_archived_data,blood_ratio_list,sex_ratio_list = generator.save_image_and_return_statistics(age_list,age_end,age_start,df,original_df,this_figure_path,this_archived_data,now_df_number)
        # データを伝える
        header = original_df.columns 
        record = original_df.values.tolist()
        copied_df_header = df.columns 
        copied_df_record = df.values.tolist() 
        
        # dfの番号に沿ったリストを作る
        df_number_list = [str(i+1) for i in range(now_df_number)]
        
        # dfのfrom_whereっていうのを更新する
        for i in range(len(df_checked_list)):
            this_archived_data[str(now_df_number)]["child"][df_checked_list[i]] = df_ratio_list[i]
        
        with open('input/variable_data_archived.json') as v:
            archived_data = json.load(v)
        archived_data[str(now_df_number)] = this_archived_data[str(now_df_number)]
        with open('input/variable_data_archived.json',"w") as v:
            json.dump(archived_data, v, indent=4, ensure_ascii=False)
        
        return render_template('comf3exp.html', 
                               header = header, 
                               record = record, 
                               copied_df_header = copied_df_header,
                               copied_df_record = copied_df_record,
                               now_df_number = str(now_df_number),
                               df_number_list = df_number_list,
                                # 統計情報
                               abs_statistics = abs_statistics,
                                # 年齢情報 
                               age_adaption = 0.4,
                                # 血液型情報
                               blood_ratio_list = blood_ratio_list,
                               blood_adaption = 0.1,
                                # 性別情報
                               sex_ratio_list = sex_ratio_list,
                               sex_adaption = 0.1,
                            #    sex_adaption = 1-sex_adaption,
                               )
    else:
        return render_template('comformation.html')

@app.route("/history_tree")
def show_history_tree():
    with open('input/df_data.json') as f: df_data = json.load(f)
    row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
    child_list_data = []
    child_list_data_with_ratio = []
    if cumulated_number == 0: result_html = ""
    if cumulated_number >= 1:#child_list_dataとresultを作る
        with open('input/variable_data_archived.json') as v: archived_data = json.load(v)
        for i in range(cumulated_number):
            child_list_data.append(list(archived_data[str(i+1)]["child"].keys()))
            child_list_data[i] = list(reversed(child_list_data[i]))#反転
            for j in range(len(child_list_data[i])):
                child_list_data[i][j] = int(child_list_data[i][j]) -1
            child_list_data_with_ratio.append(list(archived_data[str(i+1)]["child"].values()))    
        # generator.rec_html(len(child_list_data)-1,0,child_list_data)
        result_html = generator.rec_html_kaigyo2(len(child_list_data)-1,None,0,child_list_data,"")
    result_html = '{% extends "history_trees.html" %}'+"\n"+'{% block tree %}'+"\n"+result_html+"\n"+'{% endblock %}'
    tree_content_file = "/Users/qingyang/Desktop/flask_test/templates/tree_content.html"
    with open(tree_content_file, 'w', encoding='utf-8' ) as f1: f1.write(result_html)
    f1.close()
    return render_template("tree_content.html",
                        cl_list_data_ratio = child_list_data_with_ratio,
                        )
    
@app.route('/just_display')
def just_display():
    with open('input/df_data.json') as f:
        df_data = json.load(f)
    row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number = generator.sent_data_to_info(df_data)
    # 以下保存情報の内の「更新回数」
    now_df_number = cumulated_number 
    original_df = pd.read_csv("input/df/created_dummy_new.csv")
    header = original_df.columns 
    record = original_df.values.tolist()
    if now_df_number == 0:
        return render_template(
            'comformation.html', 
            header=header, 
            record=record,
            age_adaption = 0.4,
            blood_adaption = 0.1,
            sex_adaption = 0.1
            )
    if now_df_number >= 1:
        df = pd.read_csv("input/df/dummy{}.csv".format(now_df_number))
        # リスト作り
        this_figure_path = "{}/static/figure/d_copied_dummy/{}/".format(os.getcwd(),now_df_number)
        age_list = generator.create_age_list(age_start,age_end)
        this_archived_data = generator.return_this_archived_data(now_df_number)
        abs_statistics,this_archived_data,blood_ratio_list,sex_ratio_list = generator.save_image_and_return_statistics(age_list,age_end,age_start,df,original_df,this_figure_path,this_archived_data,now_df_number)        
        
        copied_df_header = df.columns 
        copied_df_record = df.values.tolist() 
        df_number_list = [str(i+1) for i in range(now_df_number)]
        
        return render_template('comf3exp.html', 
                                header = header, 
                                record = record, 
                                copied_df_header = copied_df_header,
                                copied_df_record = copied_df_record,
                                now_df_number = str(now_df_number),
                                df_number_list = df_number_list,
                                # 統計情報
                                abs_statistics = abs_statistics,
                                # 年齢情報 
                                age_adaption = 0.4,
                                # 血液型情報
                                blood_ratio_list = blood_ratio_list,
                                blood_adaption = 0.1,
                                # 性別情報
                                sex_ratio_list = sex_ratio_list,
                                sex_adaption = 0.1,
                                )
    
@app.route("/display_extension")
def data_extension():
    return render_template("extension.html",)

@app.route("/get_base_data", methods=['GET',"POST"])
def export_extended_data():
    if request.method == "POST":
        row_num  = int(request.form['row'])
        f = request.files["base"]
        base_df = pd.read_csv(f)
        print("type:",type(f))
        print("rownum:",row_num)
        basic_path = os.getcwd()+"/"
        # ①ここで表示できているか→done
        tdf = generator.extended_generator(base_df,row_num)        
        tdf_path = "{}input/df/tdf.csv".format(basic_path)
        tdf.to_csv(tdf_path,index=False)
        return send_from_directory(
            directory=basic_path + '/input/df',
            filename='tdf.csv',
            as_attachment=True,
            attachment_filename='tdf.csv',
        )
    else:
        return render_template('comformation.html')

if __name__ == "__main__":
    app.run(debug=True) 
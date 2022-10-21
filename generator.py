from curses import A_ALTCHARSET
import random
from dateutil.relativedelta import relativedelta
from datetime import date
import pandas as pd
import os
import datetime
import copy_distribution
import math
import statistics
# from jusho import Jusho
from faker.factory import Factory
fac = Factory.create('ja_JP')
import numpy as np
import numpy

from flask import Flask, jsonify, request, render_template, send_from_directory
import matplotlib
from pathlib import Path
matplotlib.use('Agg')
import copy_distribution
import plotly.graph_objs as go
import statistics
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

import collections
from datetime import datetime as dt


# ーーーーーーーーーーーーーーーーーーーーーーーーー
# データのインポート

# 血液型
blood_list = ["A","B","AB","O"]
sex_list = ["男","女","その他・不明"]
# パス要変化部分
basic_path = os.getcwd()+"/"
data_path = "%sdata/"% basic_path
#  名前データ
first_df = pd.read_csv("%sfirst_name_sorted.csv"%data_path)
last_df = pd.read_csv("%slast_name.csv"%data_path)
# 県データ
ken_path = "%sKEN_ALL2.csv"%data_path
ken_df = pd.read_csv(ken_path)
# 会社名
compony_path = "%scompony_data.csv"%data_path
comp_df = pd.read_csv(compony_path)

elements = ['name', 'age', 'birthday', 'sex', 'blood',
        'email', 'tphone', 'cphone', 'zip', 'address',
        'compony', 'card', 'expire', 'mynumber']

translate = {"name":["氏名","氏名（ひらがな）"],"age":["年齢"],
             "birthday":["生年月日"],"sex":["性別"],
             "blood":["血液型"],"email":["メアド"],"tphone":["電話番号"],"cphone":["携帯電話番号"],
             "zip":["郵便番号"],"address":["住所"],"compony":["会社名"],"card":["クレジットカード"],
             "expire":["有効期限"],"mynumber":["マイナンバー"]}

# 年齢リストの作成
def create_age_list(begin, end):
    return [begin+i for i in range(end-begin+1)]
# 関数ーーーーーーーーーーーーーーーーーーーーーーーーー
# 郵便番号と住所
def zip_address():
    is_ok = False
    while not is_ok:
        ken_n = random.randrange(len(ken_df))
        zip_tmp = str(ken_df["zip_code"][ken_n])
        zip_code = zip_tmp[:3]+"-"+zip_tmp[3:]
        chome = random.randrange(1,6,1)
        banchi = random.randrange(1,6,1)
        last = random.randrange(1,30,1)
        address = ken_df["ken"][ken_n]+ken_df["after_ken1"][ken_n]+ken_df["after_ken2"][ken_n]+str(chome)+"-"+str(banchi)+"-"+str(last)
        if "以下に" not in address and  "（" not in address and "）" not in address and len(address) <= 25:
            is_ok = True
    return zip_code,address

def zip_address_area_ja():
    is_ok = False
    while not is_ok:
        ken_n = random.randrange(len(ken_df))
        zip_tmp = str(ken_df["zip_code"][ken_n])
        zip_code = zip_tmp[:3]+"-"+zip_tmp[3:]
        area_code = zip_tmp[:3]
        chome = random.randrange(1,6,1)
        banchi = random.randrange(1,6,1)
        last = random.randrange(1,30,1)
        address = ken_df["ken"][ken_n]+ken_df["after_ken1"][ken_n]+ken_df["after_ken2"][ken_n]+str(chome)+"-"+str(banchi)+"-"+str(last)
        if "以下に" not in address and  "（" not in address and len(address) <=25:
            is_ok = True
    return zip_code,address,area_code
# 生年月日と年齢
def age_to_random_birthday(age):
    month= random.randrange(1,13,1)
    day = random.randrange(1,29,1) if month ==2 else random.randrange(1,31,1)
    today = date.today()
    today_month = today.month
    today_day = today.day
    if month < today_month or (month==today_month and day <= today_day):
        year = today.year - age
    else:
        year = today.year - age -1
    birth_day = datetime.date(year, month, day)
    return birth_day

def birth_day_age(begin,end):
    age = random.randrange(end-begin+1) + begin
    birth_day = age_to_random_birthday(age)
    return birth_day,age
    
# 旧式
def birth_day_age_old(begin,end):
    is_in = False    
    while not is_in:  
        d0 = fac.date_of_birth()
        d1 = date.today()
        dy = relativedelta(d1, d0)
        if begin <=dy.years and dy.years <= end:
            is_in = True
    return d0,dy.years

# 血液型
def blood_random():
    return blood_list[random.randrange(4)]

# 会社名
def compony():
    comp_n = random.randrange(len(comp_df))
    return comp_df["会社名"][comp_n]

# 中が0で始まるものは一旦無視
def c_phone():
    pre_list = ["5","7","8","9"]
    pre = "0"+pre_list[random.randrange(4)]+"0"
    naka = str(random.randrange(1000,10000,1))
    pro = str(random.randrange(1000,10000,1))
    c_phone = pre+"-"+naka+"-"+pro
    return c_phone

# 電話→03-XXXX-XXXXor0XXX-XX-XXXXor0X-XXXX-XXXX
def phone():
    pre_n = random.randrange(8)
    post2 = str(random.randrange(1000,10000,1))
    if pre_n in [0,1,2]:
        pre = "03"
        post1 = str(random.randrange(1000,10000,1))
    else:
        pre = "0"+str(pre_n+1)
        rand= random.randrange(2)
        if rand == 0:
            pre = pre+str(random.randrange(10,100,1))
            post1 = str(random.randrange(10,100,1))
        else:
            post1 = str(random.randrange(1000,10000,1))
    phone = pre+"-"+post1+"-"+post2
    return phone

# クレカ番号→37からはじまる15ケタ(20％)、4or5ではじまる16桁（80％）
def credit_card_n():
    tmp = random.randrange(5)
    if tmp == 0:
        card_n = random.randrange(370000000000000,380000000000000,1)
    else:
        card_n = random.randrange(4000000000000000,6000000000000000,1)
    return card_n

# クレカの有効期限
def credit_card_expire():
    return fac.credit_card_expire()

# マイナンバー12ケタ
def my_num():
    return random.randrange(100000000000,1000000000000,1)

# 名前、かな、性別、メアドのセット
def name_kana_sex_email_random():
    first_n = random.randrange(len(first_df))
    return name_kana_sex_email(first_n)

def name_kana_sex_email(first_n):
    # first_n = random.randrange(len(first_df))
    last_n = random.randrange(len(last_df))
    # 氏名とカナ
    f_name = first_df["name"][first_n]
    l_name = last_df["name"][last_n]
    f_name_kana = first_df["kana"][first_n]
    l_name_kana = last_df["kana"][last_n]
    name = l_name + " "+f_name
    kana = l_name_kana+" "+f_name_kana
    # 性別
    sex = first_df["sex"][first_n]
    # メアド→part1~4に分かれる
    p1 = random.randrange(2)
    p2 = random.randrange(2)
    p3 = random.randrange(2)
    p4 = random.randrange(5)
    # part1
    if p1 == 0:
        part1 = first_df["romanized"][first_n]
    else:
        part1 = last_df["romanized"][last_n]
    # part2
    if p2 == 0:
        part2 = ""
    else:
        part2 = "_"
    # part3
    if p3 == 0 and p2 ==0:
        part3 = ""
    elif p1 == 0:
        part3 = last_df["romanized"][last_n]
    elif p1 == 1:
        part3 = first_df["romanized"][first_n]
    # part4
    after = [".jp",".co.jp",".ne.jp",".com",".net"]
    part4 = after[p4]
    email = part1+part2+part3+"@example"+part4
    return name,kana,sex,email

def sex_to_num(sex):
    if sex == "その他・不明":
        return random.randrange(147)
    if sex == "女":
        return 147+random.randrange(955)
    if sex == "男":
        return 1101+random.randrange(1788)

def name_kana_sex_email_from_sex(sex):
    first_n = sex_to_num(sex)
    return name_kana_sex_email(first_n)
    
# 類似度指標ーーーーーーーーーーーーーーーーーーーーーーーーー
def kf_divergence(listp,listq):
    divergence = 0
    for i in range(len(listp)):
        if listq[i] == 0 or listp[i] == 0:
            continue
        else:
            divergence += listp[i]*math.log(listp[i]/listq[i])
    return 1000 * divergence/sum(listp) 

def js_divergence(listp,listq):
    return 0.5*(kf_divergence(listp,listq)+kf_divergence(listq,listp))

def normalize_divergence(x):
    return math.exp(-x/10)

def norm1(p,q):
    diff = 0
    for i in range(len(p)):
        diff += abs(p[i]-q[i])
    return diff/sum(p)

# diff_listの積分ーーーーーーーーーーーーーーーーーーーーーーーーー
def create_diff_list_cum(diff_list):
    diff_list_cum = [0]
    for i in range(len(diff_list)):
        diff_list_cum.append(diff_list_cum[i]+diff_list[i])
    return diff_list_cum

# agesのヒストグラム比率の値を返すーーーーーーーーーーーーーーーーーーーーーーー
def ages_hist_list(y_list,division):
    ages_num = len(y_list)
    q = ages_num//division
    mod = ages_num % division
    nums_list = [q] * division
    nums_cumulated = [0]
    hist_list = [0]*division
    for i in range(mod):
        nums_list[mod] += 1
    # 累積和の作成
    for i in range(division):
        nums_cumulated.append(nums_cumulated[i]+nums_list[i])
    for i in range(division):
        start = nums_cumulated[i]
        end = nums_cumulated[i+1]
        for j in range(start,end):
            hist_list[i]+=y_list[j]
    return hist_list

# 統計値ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
def hist_mean(x_list,y_list):
    s = 0
    for i in range(len(x_list)):
        s += x_list[i]*y_list[i]
    mean = s/sum(y_list)
    return mean
    
def hist_median(x_list,y_list):
    n = sum(y_list)
    i = 0
    s = y_list[i]
    while s < n/2:
        i += 1
        s += y_list[i]
    return x_list[i]

def hist_max_min(x_list,y_list):
    i = j = 0
    while y_list[i] == 0:
        i += 1
    while y_list[len(y_list)-1-j] == 0:
        j += 1
    return x_list[len(y_list)-1-j],x_list[i]

# ループ内処理
# ループ内処理1→i==startのとき
def return_first_diff_list_no_zero(df,x_list,origin,column_name):
    y_list = [df[column_name].value_counts()[x_list[i]] if x_list[i] in df[column_name].value_counts() else 0 for i in range(len(x_list))]
    diff_list = [origin[i] - y_list[i] for i in range(len(y_list))]
    diff_list_no_zero = [diff_list[i] if diff_list[i]>0 else 0 for i in range(len(y_list))]
    return diff_list_no_zero

# ループ内処理2→i>startのとき
def randomly_choose_and_delete(diff_list_no_zero,x_list):
    diff_list_cum = create_diff_list_cum(diff_list_no_zero)
    this = random.randrange(diff_list_cum[-1])
    j = 0
    while diff_list_cum[j]<this+1:
        j +=1
    diff_list_no_zero[j-1] -= 1
    key = x_list[j-1]
    return diff_list_no_zero,key
# 年齢分布用ジェネレーター-------------------------------------

def create_arr(ave,var,data_num):
    arr = np.random.normal(ave, var, data_num)
    # 四捨五入
    arr = [int(round(arr[i],0)) for i in range(len(arr))]
    return arr
# 一様分布用
def make_box(minimum,maximum,data_num):
    box = []
    ave = data_num/(maximum-minimum+1)
    s = 0
    for i in range(maximum-minimum+1):
        append = math.floor(ave) +1 if ave*(i) - s >=0.9 else math.floor(ave)
        s += append
        box.append(append)
    if data_num != sum(box):
        box[0] += data_num-sum(box)
    return box

def return_uniform_arr(minimum,maximum,data_num):
    box = make_box(minimum,maximum,data_num)
    print(box)
    age_list = [minimum+i for i in range(maximum-minimum+1)]
    ages = []
    for i in range(data_num):
        box,age = randomly_choose_and_delete(box,age_list)
        ages.append(age)
    return ages
# 正規分布用
def arr_in_normal_distribution(data_num,ave,var,minimum,maximum):
    arr_in_condition = []
    while len(arr_in_condition) < data_num:
        arr = create_arr(ave,var,data_num)
        for i in range(len(arr)):
            if minimum <= arr[i] and arr[i] <= maximum:
                arr_in_condition.append(arr[i]) 
    x = len(arr_in_condition)
    for i in range(x-data_num):
        del arr_in_condition[0]
    return arr_in_condition
# ベータ分布用
def return_arr_beta(data_num,minimum,maximum,beta):
    arr_beta = np.random.beta(beta, 1-beta, data_num)
    arr_beta = [int(round(minimum+(maximum-minimum)*arr_beta[i],0)) for i in range(data_num)]
    return arr_beta
# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

# 年齢、血液型、性別にはrow_number分のデータが必要
def make_df_except_abs(columns,row_number,compony_start,compony_end,ages,bloods,sexes):
    df = pd.DataFrame(columns = columns)
    for i in range(row_number):
        # 特殊なage,blood,sex
        age,blood,sex = ages[i],bloods[i],sexes[i]
        # その他ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
        birthday = age_to_random_birthday(age)
        name,kana,sex,email = name_kana_sex_email_from_sex(sex)
        zip_code,address = zip_address()
        comp = compony() if compony_start <= age and age <= compony_end else "NaN"
        col = columns
        info = [name,kana,age,birthday,sex,blood,email,
                phone(),c_phone(),zip_code,address,comp,
                credit_card_n(),credit_card_expire(),my_num()]
        add = dict(zip(col, info))
        df=df.append(add, ignore_index=True)
    return df

def leave_necessary_columns(elements,df,necessary_columns):
    for element in elements:
        if element not in necessary_columns:
            df = df.drop(translate[element], axis=1)
    return df
# row_number行のランダム個人情報ジェネレーター
def generate_df(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end):
    df = pd.DataFrame(columns = columns)
    
    # n行生成するプログラム
    for i in range(row_number):
        zip_code,address = zip_address()
        birthday,age = birth_day_age(age_start,age_end)
        name,kana,sex,email = name_kana_sex_email_random()
        comp = compony() if compony_start <= age and age <= compony_end else "NaN"
        col = columns
        info = [name,kana,age,birthday,sex,blood_random(),email,
                phone(),c_phone(),zip_code,address,comp,
                credit_card_n(),credit_card_expire(),my_num()]
        add = dict(zip(col, info))
        df=df.append(add, ignore_index=True)
    # 以下必要なカラムだけを残す処理
    for element in elements:
        if element not in necessary_columns:
            df = df.drop(translate[element], axis=1)
    return df

# cumulationとoriginとstart_keyに条件適応した配列を返す
# start_keyまでは広義の分布コピー（積分型コピー）
# start_key以降は狭義の分布コピー（完全コピー）
def adopted_arr(row_number,key_list,key_cumu,key_origin,start_key):
    def distribution_copied_function():
        return copy_distribution.distribution_copied_fuction(key_list,key_cumu)
    keys = []
    for i in range(row_number):
        if i < start_key:
            key = distribution_copied_function()
        if i >= start_key:
            if i == start_key: 
                diff_list_no_zero_key = return_first_diff_list_no_zero_list(keys,key_list,key_origin)
            diff_list_no_zero_key,key = randomly_choose_and_delete(diff_list_no_zero_key,key_list)    
        keys.append(key)
    return keys
  
def return_first_diff_list_no_zero_list(keys,x_list,origin):
    y_list = [keys.count(x_list[i]) for i in range(len(x_list))]
    diff_list = [origin[i] - y_list[i] for i in range(len(y_list))]
    diff_list_no_zero = [diff_list[i] if diff_list[i]>0 else 0 for i in range(len(y_list))]
    return diff_list_no_zero

# まとめて処理系ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 統計指標まとめて
def statistics_index(y_list):
    return statistics.mean(y_list),statistics.median(y_list),max(y_list),min(y_list)

# データ送られてきた時にまとめて
def sent_data_to_info(df_data):
    row_number = int(df_data["row"])
    age_start = int(df_data['age_start'])
    age_end = int(df_data['age_end'])
    compony_start = int(df_data['compony_start'])
    compony_end = int(df_data['compony_end'])
    necessary_columns = df_data["info"]
    cumulated_number = df_data["cumulated_number"]
    return row_number,age_start,age_end,compony_start,compony_end,necessary_columns,cumulated_number

def return_this_archived_data(now_df_number):
    this_archived_data = {
            str(now_df_number):{
                "ages":[],
                "bloods":[],
                "sexes":[],
                "child":{}
            }
        }
    return this_archived_data
# 指標まとめ2
def return_statistics2(y_list,y_original_list):
    js_dvg = js_divergence(y_list,y_original_list)
    js_dvg_normalized = normalize_divergence(js_dvg)
    norm1_value = norm1(y_list,y_original_list)
    return js_dvg,js_dvg_normalized,norm1_value

# 画像生成＆保存
def make_image_and_save(x_list,y_list,jp_title,figure_path,en_name):
    fig = go.Figure([go.Bar(x=x_list, y=y_list)])
    fig.update_layout(title=jp_title,title_x=0.5,font=dict(size=30))
    fig.write_image(figure_path+en_name)
    
# 血液型と性別まとめ
def key_image_save_statistics2(key_list,df,original_df,key_ja,key_en,figure_path):  
    x_list = key_list
    y_list = [df[key_ja].value_counts()[x_list[i]] if x_list[i] in df[key_ja].value_counts().index else 0 for i in range(len(x_list))]
    # データの保存
    make_image_and_save(x_list,y_list,key_ja+"分布",figure_path,key_en+".png")
    #分布類似度
    y_original_list = [original_df[key_ja].value_counts()[x_list[i]] if x_list[i] in original_df[key_ja].value_counts().index else 0 for i in range(len(x_list))]
    key_js_dvg,key_js_dvg_normalized,key_norm1 = return_statistics2(y_list,y_original_list)
    # 統計指標
    key_mean,key_median,key_max,key_min= statistics_index(y_list)
    # 割合
    key_ratio_list = y_list/sum(y_list)
    # データの保存
    y_int_list = [int(y_list[i]) for i in range(len(y_list))]
    return key_js_dvg,key_js_dvg_normalized,key_norm1,key_mean,key_median,key_max,key_min,key_ratio_list,y_int_list

# 画像生成＆保存
def age_imagesave_and_statistics(age_list,age_end,age_start,df,original_df,figure_path):
    fig = go.Figure(data=[go.Histogram(x=df["年齢"])])
    fig.update_layout(title="年齢分布",title_x=0.5,font=dict(size=30))
    fig.write_image(figure_path+"age.png")
    # 分布類似度
    x_list = age_list        
    y_list = [0]*len(age_list)
    y_original_list = [0]*len(age_list)
    for i in range(age_end-age_start+1):
        y_list[i] += df["年齢"].value_counts()[i+age_start] if i+age_start in df["年齢"].value_counts().index else 0
        y_original_list[i] += original_df["年齢"].value_counts()[i+age_start] if i+age_start in original_df["年齢"].value_counts().index else 0        

    age_js_dvg,age_js_dvg_normalized,age_norm1 = return_statistics2(y_list,y_original_list)
    # 統計指標
    age_mean,age_median,age_max,age_min = statistics_index(y_list)
    # 統計、ヒストグラム編
    age_hist_mean = hist_mean(x_list,y_list)
    age_hist_median = hist_median(x_list,y_list)
    age_hist_max,age_hist_min = hist_max_min(x_list,y_list)
    # 年齢の割合
    age_hist_list = ages_hist_list(y_list,5)
    age_ratio_list = age_hist_list/sum(age_hist_list)
    y_int_list = [int(y_list[i]) for i in range(len(y_list))]
    return age_js_dvg,age_js_dvg_normalized,age_norm1,age_mean,age_median,age_max,age_min,age_hist_mean,age_hist_median,age_hist_max,age_hist_min,age_ratio_list,y_int_list

# 画像生成保存＆統計指標吐き出し
def save_image_and_return_statistics(age_list,age_end,age_start,df,original_df,this_figure_path,this_archived_data,now_df_number):
    # 画像生成＆保存
    # 年齢 --------------------------------------------------------------
    age_js_dvg,age_js_dvg_normalized,age_norm1,age_mean,age_median,age_max,age_min,age_hist_mean,age_hist_median,age_hist_max,age_hist_min,age_ratio_list,y_int_list = age_imagesave_and_statistics(age_list,age_end,age_start,df,original_df,this_figure_path)
    this_archived_data[str(now_df_number)]["ages"] = y_int_list
    # 血液型 ------------------------------------------------------------
    blood_js_dvg,blood_js_dvg_normalized,blood_norm1,blood_mean,blood_median,blood_max,blood_min,blood_ratio_list,y_int_list = key_image_save_statistics2(blood_list,df,original_df,"血液型","blood",this_figure_path)
    this_archived_data[str(now_df_number)]["bloods"] = y_int_list
    # 性別 --------------------------------------------------------------
    sex_js_dvg,sex_js_dvg_normalized,sex_norm1,sex_mean,sex_median,sex_max,sex_min,sex_ratio_list,y_int_list = key_image_save_statistics2(sex_list,df,original_df,"性別","sex",this_figure_path)
    this_archived_data[str(now_df_number)]["sexes"] = y_int_list
    
    print("age_hist_mean:",age_hist_mean)

    # 統計情報をdict型にまとめる
    age_statistics = {"js_dvg":age_js_dvg,"js_dvg_normalized":age_js_dvg_normalized,"norm1":age_norm1,"norm1_normalized":1-age_norm1,"mean":age_mean,"median":age_median,"max":age_max,"min":age_min,"hist_mean":age_hist_mean,"hist_max":age_hist_max,"hist_min":age_hist_min,"hist_median":age_hist_median,}
    blood_statistics = {"js_dvg":blood_js_dvg,"js_dvg_normalized":blood_js_dvg_normalized,"norm1":blood_norm1,"norm1_normalized":1-blood_norm1,"mean":blood_mean,"median":blood_median,"max":blood_max,"min":blood_min}
    sex_statistics = {"js_dvg":sex_js_dvg,"js_dvg_normalized":sex_js_dvg_normalized,"norm1":sex_norm1,"norm1_normalized":1-sex_norm1,"mean":sex_mean,"median":sex_median,"max":sex_max,"min":sex_min}

    # 四捨五入と統合
    for key in age_statistics.keys():
        age_statistics[key] = round(age_statistics[key],3)
        
    for key in blood_statistics.keys():
        blood_statistics[key] = round(blood_statistics[key],3)
        sex_statistics[key] = round(sex_statistics[key],3)

    for dict in [age_statistics,blood_statistics,sex_statistics]:
        dict["js_dvg"] = round(dict["js_dvg"],2)

    abs_statistics = {
        "age":age_statistics,"blood":blood_statistics,"sex":sex_statistics
    }
    for ratio_list in [blood_ratio_list,sex_ratio_list]:
            for i in range(len(ratio_list)):
                ratio_list[i] = Decimal(ratio_list[i]*100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    
    return abs_statistics,this_archived_data,blood_ratio_list,sex_ratio_list

# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 一旦性別は無視。
def distribution_copied_df(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end,blood_cum,age_cumu,sex_cum):
    age_list = create_age_list(age_start, age_end)
    
    ages,bloods,sexes = [],[],[]
    for _ in range(row_number):
        ages.append(copy_distribution.distribution_copied_fuction(blood_list,blood_cum))
        bloods.append(copy_distribution.distribution_copied_fuction(age_list,age_cumu))
        sexes.append(copy_distribution.distribution_copied_fuction(sex_list,sex_cum))
        
    # n行生成するプログラム
    df = make_df_except_abs(columns,row_number,compony_start,compony_end,ages,bloods,sexes)
    df = leave_necessary_columns(elements,df,necessary_columns)
    return df

# 類似度調整可能なグラフ作成関数
def distribution_copied_df_stablized(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end,blood_cumu,blood_origin,blood_adaption,age_cumu,age_origin,age_adaption,sex_cumu,sex_origin,sex_adaption):
    age_list = create_age_list(age_start, age_end)
    
    start_age = math.floor(row_number*age_adaption)
    start_blood = math.floor(row_number*blood_adaption)
    start_sex = math.floor(row_number*sex_adaption)
    
    ages = adopted_arr(row_number,age_list,age_cumu,age_origin,start_age)
    bloods = adopted_arr(row_number,blood_list,blood_cumu,blood_origin,start_blood)
    sexes = adopted_arr(row_number,sex_list,sex_cumu,sex_origin,start_sex)
    
    df = make_df_except_abs(columns,row_number,compony_start,compony_end,ages,bloods,sexes)
    df = leave_necessary_columns(elements,df,necessary_columns)
    return df

def ratio_copied_df_stablized(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end,blood_cumu,blood_origin,blood_ratio_list,age_cumu,age_origin,sex_cumu,sex_origin,sex_ratio_list):
    age_list = create_age_list(age_start, age_end)
        
    # blood_ratio_listからoriginがわかればよし
    blood_ratio_based_origin = [round(blood_ratio_list[i]*row_number) for i in range(len(blood_ratio_list))]
    sex_ratio_based_origin = [round(sex_ratio_list[i]*row_number) for i in range(len(sex_ratio_list))]
    
    # 足りないところを先頭にて埋める
    y = row_number - sum(blood_ratio_based_origin)
    z = row_number - sum(sex_ratio_based_origin)
    blood_ratio_based_origin[0] += y
    sex_ratio_based_origin[0] += z
            
    # いつになったら適応プログラムを開始するのか
    ages = adopted_arr(row_number,age_list,age_cumu,age_origin,0)
    bloods = adopted_arr(row_number,blood_list,blood_cumu,blood_ratio_based_origin,0)
    sexes = adopted_arr(row_number,sex_list,sex_cumu,sex_ratio_based_origin,0)
    
    df = make_df_except_abs(columns,row_number,compony_start,compony_end,ages,bloods,sexes)        
    df = leave_necessary_columns(elements,df,necessary_columns)
    return df

def ratio_copied_df_stablized_age_specified(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end,blood_cumu,blood_origin,blood_ratio_list,age_cumu,age_origin,sex_cumu,sex_origin,sex_ratio_list,if_age_random,age_distribution_type,age_median,age_var,beta):
    age_list = create_age_list(age_start, age_end)
    # blood_ratio_listからoriginがわかればよし
    blood_ratio_based_origin = [round(blood_ratio_list[i]*row_number) for i in range(len(blood_ratio_list))]
    sex_ratio_based_origin = [round(sex_ratio_list[i]*row_number) for i in range(len(sex_ratio_list))]
    
    # 足りないところを先頭にて埋める
    y = row_number - sum(blood_ratio_based_origin)
    z = row_number - sum(sex_ratio_based_origin)
    blood_ratio_based_origin[0] += y
    sex_ratio_based_origin[0] += z
    
    # 年齢の分布特定
    if age_distribution_type == "uniform": ages = return_uniform_arr(age_start,age_end,row_number)
    if age_distribution_type == "gaus": ages = arr_in_normal_distribution(row_number,age_median,age_var,age_start,age_end)
    if age_distribution_type == "beta": ages = return_arr_beta(row_number,age_start,age_end,beta)
    if if_age_random:
        ages = []
        for i in range(row_number):
            ages.append(copy_distribution.distribution_copied_fuction(age_list,age_cumu))
        
    bloods = adopted_arr(row_number,blood_list,blood_cumu,blood_ratio_based_origin,0)
    sexes = adopted_arr(row_number,sex_list,sex_cumu,sex_ratio_based_origin,0)
    
    df = make_df_except_abs(columns,row_number,compony_start,compony_end,ages,bloods,sexes)
    df = leave_necessary_columns(elements,df,necessary_columns)
    return df

# 年齢、血液型、性別は配列で渡され、それ以外の行の生成を担うアルゴリズム
def make_df_from_abs_box(columns,row_number,necessary_columns,age_start,age_end,compony_start,compony_end,blood_cumu,blood_y_list,age_cumu,age_y_list,sex_cumu,sex_y_list):
    
    age_list = create_age_list(age_start, age_end)
    # いつになったら適応プログラムを開始するのか
    ages = adopted_arr(row_number,age_list,age_cumu,age_y_list,0)
    bloods = adopted_arr(row_number,blood_list,blood_cumu,blood_y_list,0)
    sexes = adopted_arr(row_number,sex_list,sex_cumu,sex_y_list,0)
    
    df = make_df_except_abs(
        columns,
        row_number,
        compony_start,compony_end,
        ages,bloods,sexes
        )        
    # 以下必要なカラムだけを残す処理
    df = leave_necessary_columns(elements,df,necessary_columns)
    return df

# --------------------------------------------------------------

def rec_html(child,space_num,cl_data):
    print(" "*space_num,"<li>")
    print(" "*space_num,child)
    if cl_data[child] != []:
        print(" "*(space_num+1),"<ul>")
        for cx in cl_data[child]:
            rec_html(cx,space_num+2,cl_data)
        print(" "*(space_num+1),"</ul>")
    print(" "*space_num,"</li>")
    
def rec_html_kaigyo(child,space_num,cl_data,result):
    result += " "*space_num+"<li>"+"\n"
    result += " "*(space_num+1)+str(child)+"\n"
    if cl_data[child] != []:
        result += " "*(space_num+1)+"<ul>"+"\n"
        for cx in cl_data[child]:
            result = rec_html_kaigyo(cx,space_num+2,cl_data,result)
        result += " "*(space_num+1)+"</ul>"+"\n"
    result += " "*space_num+"</li>"+"\n"
    return result

# child→今どこのchildをみているか。ゼロスタート
# space_num→（htmlにあわせて）書き始める前のスペースの広さ
# cl_data→child_list_data、すなわちツリーデータのこと。
# result→""で囲まれたresultのこと
# 再帰構造を有する
# space
def rec_html_kaigyo2(child,parent,space_num,cl_data,result):
    result += " "*space_num+"<li>"+"\n"
    result = write_1box_html(result,space_num,child,parent)
    if cl_data[child] != []:
        result += " "*(space_num+1)+"<ul>"+"\n"
        for cx in cl_data[child]:
            result = rec_html_kaigyo2(cx,child,space_num+2,cl_data,result)
        result += " "*(space_num+1)+"</ul>"+"\n"
    result += " "*space_num+"</li>"+"\n"
    return result

def write_1box_html(result,space_num,child,parent):
    # result += " "*(space_num+1)+str(child+1)+"\n"
    result += " "*(space_num+1)+'<div style="display: flex;border: 2px solid; width:560px; padding: 0px 0px; margin: 10px 0px">'.format(str(child+1))+"\n"
    # ここに番号をうまく表示できるような構成にしたい
    result += " "*(space_num+1+3)+'<div style =" width: 40px; vertical-align: middle; text-align: center;">'+"\n"
    result += " "*(space_num+1+3+3)+'<div style="border: 2px background: green;">'+"\n"
    result += " "*(space_num+1+3+3+3)+'<font size="3"> {} </font><br>'.format(str(child+1))+"\n"
    if parent != None: 
        result += " "*(space_num+1+3+3+3)+'<font size="1">-------</font><br>'+"\n"
    # いくらの割合でまぜたのか→親がわからなきゃわからない。
        result += " "*(space_num+1+3+3+3)+'{{ '+ "cl_list_data_ratio.{}.{}".format(str(parent),str(child))+ ' }}'+"\n"
    result += " "*(space_num+1+3+3)+'</div>'+"\n"
    result += " "*(space_num+1+3+3)+'<form action="/export_dummy_by_number" method="POST">'+"\n"
    result += " "*(space_num+1+3+3+2)+'<input type="image" name ="df_num" value={} src="../static/images/download-icon.jpg" style="border: double;" height="30"/>'.format(str(child+1))+"\n"
    result += " "*(space_num+1+3+3)+'</form>'+"\n"
    result += " "*(space_num+1+3)+'</div>'+"\n"
    # ここまで
    result += " "*(space_num+1+3)+'<img src="static/figure/d_copied_dummy/{}/age.png" width = "150" style="padding: 7px 10px 0px;">'.format(str(child+1))+"\n"
    result += " "*(space_num+1+3)+'<img src="static/figure/d_copied_dummy/{}/blood.png" width = "150" style="padding: 7px 10px 0px;">'.format(str(child+1))+"\n"
    result += " "*(space_num+1+3)+'<img src="static/figure/d_copied_dummy/{}/sex.png" width = "150" style="padding: 7px 10px 0px;">'.format(str(child+1))+"\n"
    result += " "*(space_num+1)+'</div>'+"\n"
    return result

# 以下は汎用化機能用------------------------------------------
def return_col_types(base_df):
    cols = base_df.columns
    col_types = []
    for i in range(len(cols)):
        col_types.append(type(base_df[cols[i]][0]))
    return col_types

def cal_10(x,y):
    if x == 0 or x == 0.0:
        return 0
    if x % 10 == 0:
        y += 1
        x /= 10
        return cal_10(x,y)
    elif x % 1 != 0:
        y -= 1
        x *= 10
        return cal_10(x,y)
    else:
        return y
    
# 名前判別との統合
col_algo_dict ={
#     "date":"date",
    "氏名":"full_name_ja",
    "かな":"full_name_kana",
    "ひらがな":"full_name_kana",
    "郵便番号":"zip_ja",
    "住所":"address_ja",
    "メールアドレス":"email",
    "電話":"t_phone",
    "携帯":"c_phone",
    "クレジットカード":"credit",
    "有効期限":"expire",
    "エリアコード":"area_ja",
    "年齢":"age",
    "性別":"gender_ja",
    "名字":"first_ja",
    "名前":"last_ja",
    "生年月日":"birth_day",
    "gender":"gender",
    "first":"first",
    "last":"last",
    "time":"time",
    "age":"age",
    "sex":"gender",
    "street":"street",
    "city":"city",
    "zip":"zip",
    "lat":"lat",
    "long":"long",
    "job":"job",
    "dob":"dob",
    "unix_time":"unix",
    "merchant":"merchant",
    "amt":"amt",
    "ann_inc":"ann_inc",
#     "":"",
#     "":"",
}
def return_algo_from_col(column):
    col_list= list(col_algo_dict.keys())
    x = "Unknown"
    for i in range(len(col_list)):
        if col_list[i] in column:
            x = col_algo_dict[col_list[i]]
    return x 

# 有限カテゴリを成立させるための関数
def copied_function(cumulated):    
    x = 0
    p = random.random()
    for i in range(len(cumulated)):
        if p<cumulated[i]:
            x = i-1
            break
    return x

# 分布コピーの排出機能を成立させるための関数
def return_random(percentile,i):
    return percentile[i]+(percentile[i+1] - percentile[i])*0.01*random.randrange(100)
def random_percentile(percentile):
    return return_random(percentile,random.randrange(100))

# date単調増加を成立させるための関数
def plus_date(ratio):
    x = random.random()
    y = math.floor(ratio)
    z = ratio - y
    return y if x > z else y+1

def return_date_str(ratio,before_date):
    td = timedelta(days=plus_date(ratio))
    this_date = before_date + td
    this_date_str = this_date.strftime('%Y/%m/%d')
    return this_date,this_date_str

# algoを特定したい,完成版
def distinction(df,does_print):
    cols = df.columns
    col_types = return_col_types(df)
    algo_box = []
    nasum = df.isnull().sum().values
    naratios = nasum/len(df)
    # 単調増加/減少性の有無
    monotonicitys = []
    # 10の階乗共通性
    common_by10 = []
    least_by10 = []
    df_l = len(df)

    for i in range(len(cols)):
        coln = cols[i]
        f_el = df[coln][0]
        digit_num = len(str(f_el))
        monotonicity = None
        common = None
        least = None
        algo = return_algo_from_col(coln)
        if algo == "Unknown":
            if col_types[i] == np.float64 or col_types[i] == np.int64:
                #単調増加性の有無と値
                tens = [df[coln][math.floor(j*(len(df)-2)/10)] for j in range(11)]
                diffs = [tens[j+1]-tens[j] for j in range(10)]
                judge_plus = [True if diffs[j] >= 0 else False for j in range(10)]
                judge_minus = [False if not judge_plus[j] else True for j in range(10)]
                last_judge_plus = last_judge_minus = True
                for j in range (10):
                    last_judge_plus = last_judge_plus and judge_plus[j]
                    last_judge_minus = last_judge_minus and judge_minus[j]
                if last_judge_plus or last_judge_minus:
                    monotonicity = (df[coln][df_l-1]-df[coln][0])/df_l
                else: monotonicity = None
                #10の階乗共通性
                list_100 = []
                for j in range(100): list_100.append(df[coln][j])
                list_100_by_10ditits = [cal_10(list_100[j],0) for j in range(100)]
                #共通性or最低性
                if min(list_100_by_10ditits) == max(list_100_by_10ditits): common = list_100_by_10ditits[0]
                #elif min(list_100_by_10ditits) >= 1: least = min(list_100_by_10ditits)
                else: least = min(list_100_by_10ditits)
            if col_types[i] == np.float64:
                algo = "distribution_copy"
            elif col_types[i] == np.int64:
                if digit_num >= 7:
                    if digit_num == 16:
                        algo = "credit"
                    else:
                        algo = "digit_num_copy"
                else: algo = "distribution_copy_int"
            elif col_types[i] == str:
                if f_el[0].isdecimal():#数字だった場合の処理
                    if "-" in f_el:
                        if digit_num == 6: algo = "expire"
                        if digit_num == 8: algo = "zip_ja"
                        if digit_num == 12: algo = "t_phone"
                        if digit_num == 13: algo = "c_phone"
    #                     else: algo = "Unknown"
                    else:
                        if "/" in f_el:
                            #dateで単調増加しているかどうかの判定をここに。ーーーーーーー
                            #5個位とってきて全部単調増加ならそう認定しよう。

                            tens = [math.floor(j*(len(df)-1)/10) for j in range(11)]
                            try: date_tens = [dt.strptime(df[coln][el], '%Y/%m/%d') for el in tens]
                            except ValueError: date_tens = [dt.strptime(df[coln][el], '%m/%d/%Y') for el in tens]
                            diffs = [(date_tens[j+1]-date_tens[j]).days for j in range(10)]
                            judge = [True if diffs[j] > 0 else False for j in range(10)]
                            last_judge_plus = True
                            for j in range (10): last_judge_plus = last_judge_plus and judge[j]
                            if last_judge_plus:
                                monotonicity = (date_tens[-1]-date_tens[0])/df_l
                                algo = "increase_date"
                            else: algo = "date"  
                else:#数字出なかった場合の処理
                    list_100 = []
                    for j in range(100): list_100.append(df[cols[i]][j])
                    c = collections.Counter(list_100)
                    if list(c.values())[0] >= 4:#有限カテゴリ
                        if list(c.keys())[0] in ["男","女","男性","女性"]:
                            algo = "gender_ja"
                        else:
                            algo = "finite_category"
                    if "@" in f_el and "." in f_el:
                        algo = "email"
        algo_box.append(algo)
        monotonicitys.append(monotonicity)
        common_by10.append(common)
        least_by10.append(least)
#         print(i,coln,f_el,algo,":finished")
    
    if does_print:
        for i in range(len(cols)):
            print(i,cols[i],df[cols[i]][0],"---【",algo_box[i],"】---",monotonicitys[i],common_by10[i],least_by10[i])
    distinction_data = {
        "algo_box":algo_box,
        "naratios":naratios,
        "monotonicitys":monotonicitys,
        "common_by10":common_by10,
        "least_by10":least_by10,
    }
    return distinction_data

def save_necessary_data(df,algo_box):
    vc_dic = {}#有限カテゴリパクリ用
    cum_ratio_dic = {}#有限カテゴリパクリ
    percentile_dic = {}#分布コピー用
    increase_date_ratio_dic = {}#単調増加date用
    digit_num_dic = {}
    cols = df.columns
    for i in range(len(cols)):
        coln = cols[i]
        algo = algo_box[i]
        #有限カテゴリ用
        if algo == "finite_category":
            vc = df[coln].value_counts()
            val_list = [vc[j] for j in range(len(vc))]
            ratio_list = val_list/sum(val_list)
            cum_ratio = [0]
            for i in range(len(ratio_list)):
                cum_ratio.append(cum_ratio[i]+ratio_list[i])
            vc_dic[coln]=vc
            cum_ratio_dic[coln]=cum_ratio
        #分布コピー
        if algo == "distribution_copy" or algo == "distribution_copy_int":
            percentile_dic[coln] = [np.percentile(df[coln],j) for j in range(101)]            
        #単調増加date
        if algo == "increase_date":
            str1 = df["オーダー日"][0]
            dte = datetime.datetime.strptime(str1, '%Y/%m/%d')
            str2 = df["オーダー日"][len(df)-1]
            dte2 = datetime.datetime.strptime(str2, '%Y/%m/%d')
            x = dte2-dte
            ratio = x.days/len(df)
            increase_date_ratio_dic[coln] = ratio
        if algo == "digit_num_copy":#会員番号とかのやつ
            digit_num_dic[coln] = len(str(df[coln][0]))
    necessary_data = {
        "vc_dic":vc_dic,
        "cum_ratio_dic":cum_ratio_dic,
        "percentile_dic":percentile_dic,
        "increase_date_ratio_dic":increase_date_ratio_dic,
        "digit_num_dic":digit_num_dic
    }
    return necessary_data

#　アルゴリズム認識→生成をする
def integrated(cols,distinction_data,necessary_data,i):
    algo_box = distinction_data["algo_box"]
    monotonicitys = distinction_data["monotonicitys"]
    common_by10 = distinction_data["common_by10"]
    least_by10 = distinction_data["least_by10"]
    naratios = distinction_data["naratios"]
    
    vc_dic = necessary_data["vc_dic"]
    cum_ratio_dic = necessary_data["cum_ratio_dic"]
    percentile_dic = necessary_data["percentile_dic"]
    increase_date_ratio_dic = necessary_data["increase_date_ratio_dic"]
    digit_num_dic = necessary_data["digit_num_dic"]
    coln = cols[i]
    algo = algo_box[i]
#     if random.random() < naratio: return "NaN"
#     else:
    if algo == "Unknown":
        return "NaN"
    if algo == "finite_category":
        vc = vc_dic[coln]
        cum_ratio = cum_ratio_dic[coln]
        return vc.index[copied_function(cum_ratio)]
    if algo == "distribution_copy":
        percentile = percentile_dic[cols[i]]
        x = random_percentile(percentile)
        if common_by10[i]: x = round(x,-common_by10[i])
        elif least_by10[i]: x = round(x,-least_by10[i])
        return x
    if algo == "distribution_copy_int":
        percentile = percentile_dic[cols[i]]
        x = random_percentile(percentile)
        if common_by10[i]: x = round(x,-common_by10[i])
        elif least_by10[i]: x = round(x,-least_by10[i])
        return round(x)
    if algo == "increase_date":
        #上手な前回日時の継承機能は課題。
        #dteが前回のdateに上手く入るようにする必要
        ratio = increase_date_ratio_dic[coln]
        td = timedelta(days=plus_date(ratio))
        this_date = dte + td
        tstr = this_date.strftime('%Y/%m/%d')
        return tstr
    if algo == "digit_num_copy":
        digit_num = digit_num_dic[coln]
        return random.randrange(10**(digit_num-1),10**digit_num,1)
    #以下カラム間で関連性のない排出アルゴリズム
    if algo == "c_phone":
        return c_phone()
    if algo == "expire":
        return credit_card_expire()
    if algo == "credit":
        return credit_card_n()
    if algo == "t_phone":
        return phone()
    #カラム間関連性なしカラムのおわりｗ
    else:
        return "NaN"
    
# 生成する
def generate_extended_data(df,distinction_data,necessary_data,row_num):
#     df = bdf2
    cols = df.columns

    # --
    algo_box = distinction_data["algo_box"]
    monotonicitys = distinction_data["monotonicitys"]
    common_by10 = distinction_data["common_by10"]
    least_by10 = distinction_data["least_by10"]
    naratios = distinction_data["naratios"]
    # --
    vc_dic = necessary_data["vc_dic"]
    cum_ratio_dic = necessary_data["cum_ratio_dic"]
    percentile_dic = necessary_data["percentile_dic"]
    increase_date_ratio_dic = necessary_data["increase_date_ratio_dic"]
    digit_num_dic = necessary_data["digit_num_dic"]
    # --
    if_zip = if_age = if_name = False
    if "zip_ja" in algo_box or "address_ja" in algo_box:
        if_zip = True
    if "age" in algo_box or "birth_day" in algo_box:
        if_age = True
    if "full_name_ja" in algo_box or "full_name_kana" in algo_box or "email" in algo_box or "gender_ja" in algo_box:
        if_name = True

#     row_num = 100
    tdf = pd.DataFrame(columns = cols)
    start_date_dic = {}
    for i in range(row_num):
        info = ["NaN"]*len(df.columns)
        #関連性のあるカラムをこうしようの巻
        start_date = "2010/01/01"
        if if_zip:
            zip_code,address,area_code = zip_address_area_ja()
            if "zip_ja" in algo_box: info[algo_box.index("zip_ja")] = zip_code
            if "address_ja" in algo_box: info[algo_box.index("address_ja")] = address
            if "area_ja" in algo_box: info[algo_box.index("area_ja")] = area_code
        if if_age:
            birth_day,age = birth_day_age(0,100)
            if "birth_day" in algo_box: info[algo_box.index("birth_day")] = birth_day
            if "age" in algo_box: info[algo_box.index("age")] = age
        if if_name:
            name,kana,gender,email = name_kana_sex_email_random()
            if "full_name_ja" in algo_box: info[algo_box.index("full_name_ja")] = name
            if "full_name_kana" in algo_box: info[algo_box.index("full_name_kana")] = kana
            if "email" in algo_box: info[algo_box.index("email")] = email
            if "gender_ja" in algo_box: info[algo_box.index("gender_ja")] = gender
        #関連性のないカラムはintegratedで
        for j in range(len(info)):
            coln = cols[j]
            if algo_box[j] == "increase_date":#increase_dateは複数ある可能性があるので、それぞれに場合分けしてこういう処理をする必要がある。
                if i == 0: 
                    this_date_str = "2010/01/01"
                    this_date = dt.strptime(this_date_str, '%Y/%m/%d')
                else:
                    ratio = increase_date_ratio_dic[coln]
                    this_date,this_date_str = return_date_str(ratio,start_date_dic[coln])
                start_date_dic[coln] = this_date
                info[j] = this_date_str
            if info[j] == "NaN": info[j] = integrated(cols,distinction_data,necessary_data,j)
        add = dict(zip(cols, info))
        tdf=tdf.append(add, ignore_index=True)
    return tdf

def extended_generator(df,row_num):
    distinction_data = distinction(df,False)
    algo_box = distinction_data["algo_box"]
    necessary_data = save_necessary_data(df,algo_box)
    tdf = generate_extended_data(df,distinction_data,necessary_data,row_num)
    return tdf
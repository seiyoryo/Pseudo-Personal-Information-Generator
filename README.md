# Pseudo-Personal-Information-Generator

擬似個人情報の生成と、既存データの分布を踏まえたデータ拡張（Data Augmentation）を行う Web アプリケーションです。

---

## 主な機能

1. **擬似個人情報の生成**  
   行数・年齢範囲・項目（氏名・年齢・性別・血液型・住所・電話・メール・会社名・クレジットカード・マイナンバー等）を指定し、ランダムな擬似個人情報 CSV を生成します。

2. **分布コピー（同系分布データの作成）**  
   初回生成データの年齢・血液型・性別の分布に「類似度係数」をかけて、元の分布に近い擬似データを追加生成します。割合指定（一様・正規・ベータ・ランダム）や、複数データの**混合分布**にも対応しています。

3. **データ拡張**  
   既存の CSV をアップロードすると、列の内容からアルゴリズム（有限カテゴリ・分布コピー・日付単調増加・電話番号等）を推定し、同じ分布・形式で指定行数分のデータを拡張して CSV でダウンロードできます。

---

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python |
| Web フレームワーク | Flask |
| データ処理 | Pandas |
| グラフ描画 | Plotly, Matplotlib |
| 擬似データ生成 | Faker (ja_JP), 自前ロジック |
| フロント | Bootstrap 5, Jinja2 テンプレート |

---

## 必要な環境・データ

### Python パッケージ（目安）

- `flask`
- `pandas`
- `plotly`
- `kaleido`（Plotly の画像出力用）
- `faker`
- `python-dateutil`
- `numpy`
- `matplotlib`

（必要に応じて `requirements.txt` を作成し、`pip install -r requirements.txt` で一括インストールしてください。）

### マスタデータ（data/ 配下）

| ファイル | 用途 |
|----------|------|
| `first_name_sorted.csv` | 名前（名）・かな・性別・ローマ字 |
| `last_name.csv` | 名字・かな・ローマ字 |
| `KEN_ALL2.csv` | 郵便番号・住所（県以降） |
| `compony_data.csv` | 会社名 |

※ 郵便番号データは `KEN_ALL2.csv` を `data/` に配置してください（.icloud のみの場合は実ファイルをダウンロードする必要があります）。

---

## 起動方法

1. リポジトリをクローンまたは `git pull` で取得する。
2. 上記パッケージをインストールする。
3. `data/` にマスタ CSV を配置する。
4. プロジェクトルートで以下を実行する。

```bash
python csv_generate.py
```

5. ブラウザで `http://127.0.0.1:5000/` にアクセスする。（Flask のデフォルトは `debug=True` で起動）

---

## 使い方の流れ

### 擬似個人情報を新規生成する

1. トップ画面（`/`）で**行数**・**年齢範囲**・**会社名を付与する年齢範囲**・**含める項目**（氏名・年齢・性別・血液型・住所・電話・メール等）を指定する。
2. 「送信」で初回生成が実行され、**生成結果一覧**と**年齢・血液型・性別の分布グラフ**が表示される。
3. 「ダウンロード」で `created_dummy_new.csv` を取得できる。
4. **分布類似度係数**（年齢・血液型・性別それぞれ 0～1）を入力して「同系分布データ作成」を押すと、元データに近い分布の新規データ（`dummy1.csv` 以降）が作成され、統計とグラフが表示される。以降、同様の操作で `dummy2`, `dummy3` … と増やせる。

### 割合指定で分布コピーする

- 年齢分布を「一様・正規・ベータ・ランダム」のいずれかにし、血液型・性別の割合を数値で指定してから、対応するフォームで送信する（`/copy_distribution_by_ratio`）。

### 混合分布を作成する

- 既に作成した dummy を複数選択し、それぞれに**重み（割合）**を付けて「混合分布」を実行する（`/make_mixture_distribution`）。選択したデータの分布を加重平均した擬似データが生成される。

### データ拡張を使う

1. メニューから「データ拡張」相当の画面（`/display_extension`）を開く。
2. ベースとなる CSV をアップロードし、**拡張したい行数**を入力して送信する。
3. 列の内容からアルゴリズムが推定され、同じ形式で指定行数分のデータが生成され、CSV でダウンロードされる。

### 履歴・ダウンロード

- **履歴とツリー**（`/history_tree`）：これまで作成した dummy の親子関係（混合の由来）をツリー表示する。
- **出力予想図**（`/just_display`）：現在の状態（初回のみ or 直近の分布コピー/混合結果）を再表示する。
- 各画面の「ダウンロード」や番号指定ダウンロード（`/export_dummy_by_number`）で、対応する CSV を取得できる。

---

## プロジェクト構成

```
pseudo-personal-information-generator/
├── csv_generate.py      # Flask アプリ（エントリポイント）。ルーティング・リクエスト処理・JSON/CSV 永続化
├── generator.py         # 擬似データ生成・分布コピー・統計・画像生成・データ拡張のロジック
├── copy_distribution.py # 分布の累積計算と「分布コピー」サンプリング
├── data/                # マスタ CSV（名前・郵便番号・会社名）
├── input/
│   ├── df_data.json              # 現在の生成条件（行数・年齢範囲・項目・cumulated_number）
│   ├── variable_data_archived.json # 各 dummy の分布アーカイブ・混合の親子情報
│   └── df/                       # 生成結果 CSV（created_dummy_new.csv, dummy1..N.csv, tdf.csv）
├── static/              # CSS・画像・グラフ出力先（figure/dummy/, figure/d_copied_dummy/{N}/）
├── templates/           # Jinja2 テンプレート（main_screen, comformation, comf3exp, extension, history_trees 等）
├── docs/
│   └── module-responsibility-matrix.md  # モジュール責務・処理順・依存関係・ステータス遷移の詳細
├── Makefile             # git-push 等
└── README.md            # 本ファイル
```

---

## モジュールの役割（概要）

| モジュール | 役割 |
|------------|------|
| **csv_generate.py** | Web 層。URL ルーティング・フォーム受付・`generator` / `copy_distribution` の呼び出し・JSON/CSV の読み書き・HTML の描画。 |
| **generator.py** | 擬似個人情報の生成、分布に基づくデータ作成、統計指標の計算、Plotly によるグラフ画像の生成・保存、データ拡張用の列アルゴリズム推定と行生成。 |
| **copy_distribution.py** | 既存 DataFrame の指定列（年齢・血液型・性別など）の分布を累積化し、その分布に従うサンプル値を 1 件返す関数を提供。 |

詳細な**処理順序・依存関係・画面のステータス遷移**は [docs/module-responsibility-matrix.md](docs/module-responsibility-matrix.md) を参照してください。

---

## ライセンス・リポジトリ

- リポジトリ: [seiyoryo/Pseudo-Personal-Information-Generator](https://github.com/seiyoryo/Pseudo-Personal-Information-Generator)
- 本 Web アプリは**個人情報のテスト・開発用の擬似データ**を生成する目的で利用することを想定しています。実データの取り扱いには各規程に従ってください。

# Pseudo-Personal-Information-Generator

[English](README.md) | [日本語](README.ja.md)

擬似個人情報（日本向け）を生成し、分布を踏まえたデータ拡張（Data Augmentation）も行える Flask Web アプリです。

## できること（要点）

- **新規生成**: 行数・年齢範囲・出力項目を指定して、擬似個人情報の CSV を生成
- **分布コピー**: 初回生成データの年齢/血液型/性別分布に近いデータを追加生成（類似度係数）
- **混合分布**: 複数の生成済みデータを重み付きで混ぜて新しいデータを生成
- **CSV拡張**: 既存CSVをアップロードし、列の特徴から生成アルゴリズムを推定して行を拡張
- **履歴ツリー**: 混合の由来をツリー表示

## 起動方法

```bash
pip install -r requirements.txt
python app/main.py
```

ブラウザで `http://127.0.0.1:5000/` を開きます。

（`Makefile` の `make setup` / `make run` も利用できます）

## 必要データ（data/）

以下のマスタ CSV を `data/` に用意してください。

- `first_name_sorted.csv`
- `last_name.csv`
- `KEN_ALL2.csv`（郵便番号・住所マスタ）
- `compony_data.csv`

## 生成物について（重要）

アプリ実行時にローカルへ生成される以下のファイルは、Git 管理しない方針です。

- `state/*.json`（実行時状態）
- `outputs/df/*.csv`（生成CSV）
- `outputs/figure/**`（分布グラフ画像）

## 機密情報について（重要）

秘密鍵・トークン・`.env` 等の機密情報はリポジトリに含めないでください。

## 補足（設計ドキュメント）

- モジュール責務・処理順・依存関係・ステータス遷移: `docs/module-responsibility-matrix.md`


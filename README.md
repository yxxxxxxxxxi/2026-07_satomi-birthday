# 2026年7月_理実誕生日旅行 MVP

ローカルファイル中心で旅行候補を管理し、Google My Maps にインポートできる CSV と、1ファイル完結の旅行ダッシュボード HTML を生成するプロジェクトです。

## このプロジェクトの目的

- 旅行候補を CSV と Markdown で人間が編集しやすく管理する
- 候補地を Google My Maps で俯瞰できる形式に変換する
- 旅程、候補、ToDo、予算メモを 1 つの HTML で確認できるようにする
- 将来的な geocoding、自動候補収集、Web アプリ化に備えた構造を残す

## できること

- 観光候補 CSV のバリデーション
- Google My Maps 用 CSV の出力
- 単一 HTML ダッシュボードの生成
- Markdown ドキュメントのタブ表示
- 将来拡張ロードマップの整理

## ディレクトリ構成

```text
2026-07_satomi-birthday/
├── README.md
├── pyproject.toml
├── .env.example
├── config/
│   └── trip.yaml
├── data/
│   ├── sightseeing_candidates.csv
│   ├── hotel_candidates.csv
│   ├── restaurant_candidates.csv
│   └── transport_options.csv
├── docs/
│   ├── 00_overview.md
│   ├── 01_itinerary.md
│   ├── 02_sightseeing.md
│   ├── 03_hotels.md
│   ├── 04_restaurants.md
│   ├── 05_transport.md
│   ├── 06_budget.md
│   ├── 07_reservations_todo.md
│   ├── 08_birthday_surprise.md
│   ├── 09_notes.md
│   └── 90_future_roadmap.md
├── output/
├── scripts/
│   ├── build_all.py
│   ├── build_dashboard.py
│   ├── export_mymaps_csv.py
│   ├── geocode_candidates.py
│   ├── validate_data.py
│   └── lib/
└── tests/
```

## セットアップ方法

標準ライブラリのみで動きます。

```bash
python3 --version
python3 -m unittest discover -s tests
```

依存管理を追加したい場合の雛形として `pyproject.toml` を置いています。将来 `uv sync` や `pip install -r requirements.txt` を追加しても壊れない構成です。

## 使い方

```bash
# データ検証
python3 scripts/validate_data.py

# My Maps用CSV出力
python3 scripts/export_mymaps_csv.py

# HTMLダッシュボード生成
python3 scripts/build_dashboard.py

# まとめて実行
python3 scripts/build_all.py
```

出力確認:

```bash
open output/travel_dashboard.html
```

GitHub Pages 用の公開ファイルとして `output/index.html` と ルートの `index.html` も同時に生成されます。

## CSV の編集方法

- `data/sightseeing_candidates.csv` の 1 行が 1 候補です
- `priority` は `S/A/B/C`
- `birthday_score` は `1-5`
- `heat_risk` は `高/中/低`
- `rain_ok` は `可/一部可/不可`
- `day_candidate` は `Day1/Day2/Day3/Day4/未定`
- 緯度経度が未確定でも `google_maps_search` は入れてください

編集後は必ず `python3 scripts/validate_data.py` を実行してください。

## Google My Maps へのインポート手順

1. `python3 scripts/export_mymaps_csv.py` を実行して `output/mymaps_import.csv` を生成する
2. [Google My Maps](https://www.google.com/mymaps) を開く
3. 新しい地図を作成し、レイヤーの `インポート` を選ぶ
4. `output/mymaps_import.csv` を選択する
5. 位置情報の列は `Latitude/Longitude` または `Address` を選ぶ
6. ラベル表示には `Name` を選ぶ

### 位置関係を見やすくするコツ

1. 候補の位置関係を見るだけなら、まず `output/mymaps_import.csv` をそのまま 1 レイヤーに読み込む
2. そのあと、`Day1` から `Day4` ごとに CSV を分けて再インポートすると、日別レイヤーとして比較しやすい
3. `Area` 列を見ながら、宮島、尾道、出雲、松江などエリアの固まりを確認する
4. 地図上で各ピンをクリックし、`Memo` の優先度、滞在時間、暑さリスク、雨天対応を見て候補を絞る
5. 行けそうな組み合わせが見えたら、My Maps 上で線やメモを追加して日ごとの移動イメージを手で補う

### My Maps で確認したいポイント

- 同じ日に入れたい候補が地理的にまとまっているか
- 広島側と山陰側の移動が詰め込みすぎになっていないか
- 真夏に屋外候補が連続しすぎていないか
- 雨天時に屋内候補へ差し替えやすいエリア構成になっているか
- 誕生日向けの本命候補を無理なく同じ日にまとめられるか

### 今回の CSV の使い方

- `Name`: ピン名
- `Address`, `Latitude`, `Longitude`: 位置決め用
- `Day`: 日程候補
- `Area`: エリア確認用
- `Memo`: 優先度、滞在目安、誕生日向き、暑さ、雨天対応の確認用

必要に応じて `data/sightseeing_candidates.csv` を編集し、再度 `python3 scripts/build_all.py` を実行して最新 CSV を出し直してください。

## HTML ダッシュボードの確認方法

- `python3 scripts/build_dashboard.py` で `output/travel_dashboard.html` を生成します
- ブラウザで開くと、概要、旅程表、観光候補、宿泊候補、食事候補、移動、予算、予約・ToDo、誕生日演出、メモの 10 タブを確認できます
- データ未登録のタブは `未登録` と表示します

## GitHub Pages で共有する方法

このプロジェクトは GitHub Pages の branch 配信に向くように、ルートの [index.html](/Users/yuki/development/travel-planning/2026-07_satomi-birthday/index.html) を自動生成します。GitHub 上では `main` ブランチの `/(root)` を公開元に設定します。

### 公開の流れ

1. GitHub にリポジトリを作成する
2. `main` に push する
3. リポジトリ Settings の Pages で `Deploy from a branch` を選ぶ
4. Branch は `main`、folder は `/(root)` を選ぶ
5. 公開後に `https://<owner>.github.io/<repository>/` で閲覧する

### 注意点

- GitHub Pages は静的サイト公開なので、この HTML には適しています
- GitHub Pages の URL は公開 URL です
- GitHub Free では公開リポジトリでの運用が最も確実です
- 個人旅行情報を含むため、公開内容は必要最小限にしてください

## 将来的な拡張案

- Google Sheets 連携
- 住所からの緯度経度補完
- Places API による候補補強
- 移動時間計算と日次負荷チェック
- 雨天・猛暑時の代替案提案
- Web アプリ化と共有 URL 発行

詳細は [docs/90_future_roadmap.md](/Users/yuki/development/travel-planning/2026-07_satomi-birthday/docs/90_future_roadmap.md) を参照してください。

## Google Maps Platform を使う場合の注意点

- API キーは `.env` で管理し、コードに直書きしない
- Places API / Geocoding API / Routes API は公式利用規約と料金を事前確認する
- レスポンスキャッシュや再配布には制限があるため、保存方法を設計時に確認する
- MVP では API 必須にしない

## 商品化に向けた課題

- 候補地データの収集と品質管理フロー
- 旅程最適化ロジックの説明可能性
- エリア別、旅行タイプ別のテンプレート設計
- 共同編集、共有、権限管理
- API コストと収益性のバランス

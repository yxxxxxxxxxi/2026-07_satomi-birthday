# My Maps と共有手順

## Google My Maps で位置関係を見る目的

- 候補地同士の距離感をざっくり把握する
- 同日にまとめられる候補を見つける
- 山陰側と広島側の移動負荷を見誤らない
- 雨天代替や猛暑回避の候補配置を比較する

## 基本手順

1. `python3 scripts/build_all.py` を実行する
2. `output/mymaps_import.csv` を Google My Maps にインポートする
3. ピンをクリックして `Memo` を見ながら、優先度、滞在時間、暑さ、雨天対応を確認する
4. 日別に見たい場合は CSV を複製し、`Day` 列で絞ったファイルをレイヤーごとに読み込む
5. 宿や食事候補を追加したら別レイヤーにして比較する

## 日別レイヤーの考え方

- Day1: 広島市内
- Day2: 宮島、尾道
- Day3: 出雲、日御碕、宍道湖
- Day4: 松江、玉造、安来

## GitHub Pages での共有

- `output/index.html` が GitHub Pages の公開入口です
- `main` ブランチに push すると、GitHub Actions で Pages デプロイできます
- 共有 URL は公開 URL なので、個人情報は置かない前提で使います

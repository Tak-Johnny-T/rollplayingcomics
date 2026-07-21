# rollplayingcomics.com

ロールプレイングコミック公式サイト（THE ROLLPLAYING COMICS）のソース。
GitHub Pages で `https://rollplayingcomics.com` として公開している。

## 構成

```
index.html              トップ
privacy.html            プライバシーポリシー
magiccraft/index.html   THE MAGIC CRAFT 作品ページ
magiccraft/ep1.html     Episode 1
magiccraft/ep2.html     Episode 2
magiccraft/fanart.html  Fan Arts
assets/img/             画像（すべて WebP）
tools/to_webp.py        画像を WebP へ一括変換するスクリプト
```

ビルド不要の静的サイト。CSS と JS は各 HTML に直接書いている。

## 画像の追加手順

1. 元画像（PNG / JPG）を `assets/img/` に置く
2. `python tools/to_webp.py --dry-run` で変換計画を確認する
3. `python tools/to_webp.py` で変換する（元ファイルは変更されない）
4. HTML から `.webp` を参照し、元の PNG / JPG は `assets/img/` から削除する

表示サイズに対する最大幅と画質はファイル名ごとに `tools/to_webp.py` の `RULES` で決まる。
新しい種類の画像を足すときはルールを 1 行追加する。

Pillow が必要（`python -m pip install pillow`）。

## 公開設定

- Pages のソース: `main` ブランチのルート
- 独自ドメイン: `CNAME` に `rollplayingcomics.com`
- `.nojekyll` を置いて Jekyll の処理を無効化している

## 未対応

- フッターの「イラストレーション」はリンク先未定（イラストサイトが未構築）
- トップのロゴは CAPTURE IT で組んだ画像に差し替える案があるが、現在はフォント表示

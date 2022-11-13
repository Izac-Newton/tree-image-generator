[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# tree-image-generator

## 機能
入力された JSON から画像をピラミッド状に並べた画像を生成するプログラムです。

## 使用方法
JSON ファイルへのパスをコマンドライン引数として渡して Tree-Image-Generator.py を実行してください。
```
$ Python Tree-Image-Generator.py <Jsonファイルへのパス>
```

実行用のサンプルJSONとして、sample.json を使用できます。
```
$ Python Tree-Image-Generator.py sample.json
```

## 依存ライブラリ
* Pillow
* requests

## 動作確認環境
* Windows 10
* Python 3.11.0
  * Pillow 9.3.0
  * requests 2.28.1

## 作成者
ニュートン（[Twitter](https://twitter.com/H2Newton)）
# 詳細設計書

## 前提条件
- データはAzure Blobの`movies`コンテナ配下のJSONファイルを読み書きする。
- Blobへのアクセス方法は既存の`get_snippet`および`save_snippet`を参考にする。
- リクエストパラメータに対して最低限のValidationを行う。
- 作成した予約データは`src/data/reservations.jsonl`としてJSON List形式で保存する。

## 機能設計

### 映画データ取得機能
#### 処理フロー
1. Azure Blobの`movies`コンテナから`movies.json`を取得。
2. JSONデータをパースし、クライアントに返却。
3. 必要に応じてリクエストパラメータのValidationを実施。

### 上映スケジュール取得機能
#### 処理フロー
1. Azure Blobの`movies`コンテナから`schedules.json`を取得。
2. JSONデータをパースし、クライアントに返却。
3. リクエストパラメータ（例: 日付範囲）のValidationを実施。

### 座席状況取得機能
#### 処理フロー
1. Azure Blobの`movies`コンテナから`seats.json`を取得。
2. JSONデータをパースし、クライアントに返却。
3. リクエストパラメータ（例: 上映スケジュールID）のValidationを実施。

### 予約データ作成機能
#### 処理フロー
1. クライアントからのリクエストを受け取り、リクエストパラメータのValidationを実施。
2. 予約データをJSON形式で生成。
3. 生成した予約データを`src/data/reservations.jsonl`に追記保存。
4. 必要に応じてAzure Blobにアップロード。

## Validation設計
- リクエストパラメータの型チェック（例: 日付形式、文字列長）。
- 必須項目の確認。
- 不正な値に対するエラーメッセージの返却。

## Azure Blobアクセス設計
- `get_snippet`を使用してBlobからデータを取得。
- `save_snippet`を使用してBlobにデータを保存。

## ファイル構成
- `movies.json`: 映画データ。
- `schedules.json`: 上映スケジュールデータ。
- `seats.json`: 座席状況データ。
- `reservations.jsonl`: 予約データ（JSON List形式）。
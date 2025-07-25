# 詳細設計書

## 概要
この詳細設計書は、受入試験項目表の自動生成を実現するためのMCPツール群の処理フローを記述します。データはAzure Blob Storageのaccep-testコンテナ配下のJSONファイルを読み書きします。

## 機能別設計

### 1. 仕様理解機能
- **処理フロー**:
  1. リクエストパラメータ`specificationId`を受け取る。
  2. `specificationId`のValidationを行い、形式が正しいことを確認する。
  3. Azure Blob Storageのaccep-testコンテナから仕様データを取得する。
  4. 取得した仕様データを解析し、システム情報を抽出する。
  5. 抽出したシステム情報をレスポンスとして返す。

### 2. 差分把握機能
- **処理フロー**:
  1. リクエストパラメータ`pastTestItemId`と`currentSpecificationId`を受け取る。
  2. 各パラメータのValidationを行い、形式が正しいことを確認する。
  3. Azure Blob Storageのaccep-testコンテナから過去試験項目データと仕様データを取得する。
  4. 取得したデータを比較し、差分情報を生成する。
  5. 差分情報をレスポンスとして返す。

### 3. 試験項目作成機能
- **処理フロー**:
  1. リクエストパラメータ`specificationId`と`pastTestItemId`を受け取る。
  2. 各パラメータのValidationを行い、形式が正しいことを確認する。
  3. Azure Blob Storageのaccep-testコンテナから仕様データと過去試験項目データを取得する。
  4. 取得したデータを基に試験項目を自動生成する。
  5. 生成した試験項目をAzure Blob Storageに保存する。
  6. 試験項目をレスポンスとして返す。

## 備考
- Azure Blob Storageへのアクセス方法は既存の`get_snippet`および`save_snippet`を参考にする。
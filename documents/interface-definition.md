# インタフェース仕様書

## 概要
この仕様書は、MCP(Model Context Protocol)を使用した業務機能のインタフェースを定義します。各機能はJSON-RPC形式でリクエスト・レスポンスを行い、業務仕様書のデータ構造と整合性を保ちます。

## インタフェース定義

### 1. 仕様理解機能
- **メソッド名**: `understand_specification`
- **リクエスト**:
```json
{
    "jsonrpc": "2.0",
    "method": "understand_specification",
    "params": {
        "specificationId": "string"
    },
    "id": 1
}
```
- **レスポンス**:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "systemInfo": "object"
    },
    "id": 1
}
```

### 2. 差分把握機能
- **メソッド名**: `get_differences`
- **リクエスト**:
```json
{
    "jsonrpc": "2.0",
    "method": "get_differences",
    "params": {
        "pastTestItemId": "string",
        "currentSpecificationId": "string"
    },
    "id": 2
}
```
- **レスポンス**:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "differences": "object"
    },
    "id": 2
}
```

### 3. 試験項目作成機能
- **メソッド名**: `create_test_items`
- **リクエスト**:
```json
{
    "jsonrpc": "2.0",
    "method": "create_test_items",
    "params": {
        "specificationId": "string",
        "pastTestItemId": "string"
    },
    "id": 3
}
```
- **レスポンス**:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "testItems": "array"
    },
    "id": 3
}
```

## 備考
- 各メソッドは業務仕様書のデータ構造に基づいて設計されています。
- JSON-RPC形式を採用し、リクエストとレスポンスの整合性を確保しています。
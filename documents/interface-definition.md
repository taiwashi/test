# インタフェース仕様書

## 映画一覧の取得
### リクエスト
```json
{
  "jsonrpc": "2.0",
  "method": "get_movie_list",
  "params": {}
}
```

### レスポンス
```json
{
  "jsonrpc": "2.0",
  "result": {
    "movies": [
      {
        "title": "インセプション",
        "description": "夢の中でのスパイ活動を描いたサスペンス映画",
        "rating": 4.5,
        "cast": ["レオナルド・ディカプリオ", "ジョセフ・ゴードン＝レヴィット", "エレン・ペイジ"]
      }
    ]
  }
}
```

## 上映時間枠の表示
### リクエスト
```json
{
  "jsonrpc": "2.0",
  "method": "get_schedule",
  "params": {
    "movie_title": "インセプション"
  }
}
```

### レスポンス
```json
{
  "jsonrpc": "2.0",
  "result": {
    "schedules": [
      {
        "schedule_id": "SCH67890",
        "start_time": "2025-07-11T14:00:00Z",
        "end_time": "2025-07-11T16:30:00Z",
        "movie_title": "インセプション"
      }
    ]
  }
}
```

## 空席情報の取得
### リクエスト
```json
{
  "jsonrpc": "2.0",
  "method": "get_seat_availability",
  "params": {
    "schedule_id": "SCH67890"
  }
}
```

### レスポンス
```json
{
  "jsonrpc": "2.0",
  "result": {
    "available_seats": [
      {"row": 1, "column": 1},
      {"row": 1, "column": 2},
      {"row": 1, "column": 3}
    ],
    "occupied_seats": [
      {"row": 1, "column": 4},
      {"row": 1, "column": 5}
    ]
  }
}
```

## 座席予約の確定
### リクエスト
```json
{
  "jsonrpc": "2.0",
  "method": "reserve_seat",
  "params": {
    "schedule_id": "SCH67890",
    "seat_positions": [
      {"row": 1, "column": 1},
      {"row": 1, "column": 2}
    ]
  }
}
```

### レスポンス
```json
{
  "jsonrpc": "2.0",
  "result": {
    "reservation_id": "RES54321",
    "reserved_seats": [
      {"row": 1, "column": 1},
      {"row": 1, "column": 2}
    ],
    "reservation_time": "2025-07-10T10:00:00Z"
  }
}
```

## レイトショー割引情報の提供
### リクエスト
```json
{
  "jsonrpc": "2.0",
  "method": "get_discount_info",
  "params": {
    "schedule_id": "SCH67890"
  }
}
```

### レスポンス
```json
{
  "jsonrpc": "2.0",
  "result": {
    "discount_type": "レイトショー",
    "applicable_time": "21:00以降",
    "discount_rate": "20%"
  }
}
```

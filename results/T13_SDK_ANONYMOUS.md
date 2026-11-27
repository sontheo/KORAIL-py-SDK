# T13. SDK 익명 기능, 짧은 데이터 봉투 3회 검증

## 범위

- 봇 제외, SDK만 검증
- 로그인 호출 없음 (`accounts_used: false`)
- egress: dpbokji SOCKS5 `<dpbokji-socks>:1055`
- 모드: `v2-declaration`, 짧은 데이터 봉투

## 도구

`tools/analysis/sdk_anonymous_smoke.py`

```bash
PYTHONPATH=src .venv/bin/python tools/analysis/sdk_anonymous_smoke.py \
  --proxy socks5h://<dpbokji-socks>:1055 --repeat 3
```

## 결과: 3/3 통과

| 기능 | 1회 | 2회 | 3회 |
|---|---:|---:|---:|
| 역 목록 `get_station_data` | 281 | 281 | 281 |
| 역 정보 `get_station_info` | 281 | 281 | 281 |
| 운행 달력 `get_train_calendar` | 63일 | 63일 | 63일 |
| 단일 검색 `search_trains` | 10대 | 10대 | 10대 |
| 페이지네이션 `search_trains_all` | 29대 | 29대 | 29대 |
| 환승 검색 `search_transfer_trains` | 5개 | 5개 | 5개 |
| 열차 운행 `get_train_schedule` | 9정거장 | 9정거장 | 9정거장 |
| 환승역 `get_transfer_stations` | 5개 | 5개 | 5개 |
| 운임 `get_price_fare_quote` | 2개 | 2개 | 2개 |

모든 실행의 검색 응답은 `strResult=SUCC`, `h_msg_cd=IRG000000`이다. `-2000`은 없었다.

## 검색 변형

같은 짧은 봉투로 1회씩:

| 변형 | 결과 |
|---|---|
| SRT 포함 `include_srt=True` | 10대, `SUCC` |
| 인접역 포함 `include_nearby_stations=True` | 10대, `SUCC` |
| 성수기 `peak_season=True` | 10대, `SUCC` |
| 특별 스케줄 `use_special_schedule=True` | `ERT900011` (HTTP 200, DynaPath 통과) |

## 특별 스케줄 대조

같은 요청을 짧은 봉투와 기존 full 봉투로 비교했다.

| 봉투 | 결과 |
|---|---|
| 짧은 데이터 봉투 | HTTP 200, `ERT900011` |
| full 봉투 (`es=288904575606514493`, `kl/ec` 포함) | HTTP 403, `-2000` |

즉 `ScheduleViewSpecial`도 짧은 봉투로 DynaPath를 통과한다. `ERT900011`은 DynaPath 차단이 아니라 서버의 조회 결과 오류다. 이 경로는 SDK에서 opt-in이며, 서버 오류 원인은 확인하지 못했다.

## 테스트

```text
409 passed in 1.80s
ruff: All checks passed!
```

## 판정

SDK의 비로그인 읽기 기능은 짧은 데이터 봉투로 정상 동작한다. 검색·페이지네이션·환승·운행·운임·역/달력 조회에서 `-2000`이 재현되지 않았다.

## 한계

- 로그인, 예약 생성, 결제, 취소, 마일리지/쿠폰/승차권 조회는 이번 범위에서 호출하지 않았다.
- `get_seat_cars`와 `get_seat_inventory`는 SDK 계약상 세션이 필요해 제외했다.
- 리무진/버스·MaaS 등 나머지 비로그인 endpoint는 이번 스모크에 넣지 않았다.
- `ScheduleViewSpecial`의 `ERT900011` 원인은 확인하지 못했다. 짧은 봉투 자체의 `-2000` 문제는 아니다.

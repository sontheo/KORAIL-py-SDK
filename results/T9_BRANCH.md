# T9. 신규 브랜치 `fix/mobile-v2-app-metadata`

## 브랜치/커밋

- branch: `fix/mobile-v2-app-metadata`
- commit: `5410862 Add mobile DynaPath live probe and align request metadata`

## 변경

- `tools/analysis/sdk_probe.py` 신규
  - 제품 `KorailClient`/`KorailConfig`/`TrainSearchQuery`를 그대로 사용하는 live/mock probe
  - mock 모드에서 실제 요청의 `Version`, `AppVersion`, `Key`, UA, token prefix, form keys를 캡처
  - live 모드에서 `KorailDynaPathError`의 `http`, `code`, `dynapath_code`, `h_msg_cd`, `request_id` 기록
- `tools/analysis/mobile_client.py` 수정
  - 실제 앱 값: `korail1234567890`, `250722001`, `korailtalk`
  - v2 profile: `SM-S911N` / Android 15 / `kalama` / SDK 35 / strongbox 1
  - 검색 form: 역 이름(`서울`/`부산`), `qryDvCd=1`, `Sid` 기본 미전송
  - `--sid`, `--netfunnel` 옵션으로 변인 통제

## mock 검증

제품 SDK가 실제로 보내는 검색 요청:

```json
{
  "method": "POST",
  "host": "smart.letskorail.com",
  "path": "/classes/com.korail.mobile.seatMovie.ScheduleView",
  "user_agent": "korailtalk",
  "version": "250722001",
  "app_version": "7.0.10",
  "device": "AD",
  "key": "korail1234567890",
  "token_prefix": "201Te",
  "token_length": 312,
  "sid_present": false,
  "form_keys": [
    "AppVersion","Device","Key","Version","adjStnScdlOfrFlg","ebizCrossCheck",
    "qryDvCd","radJobId","rtYn","selGoTrain","srtCheckYn","txtGoAbrdDt",
    "txtGoEnd","txtGoHour","txtGoStart","txtMenuId","txtPsgFlg_1","txtPsgFlg_2",
    "txtPsgFlg_3","txtPsgFlg_4","txtPsgFlg_5","txtSeatAttCd_2","txtSeatAttCd_3",
    "txtSeatAttCd_4","txtTrnGpCd"
  ]
}
```

이전 분석 도구와의 차이:

- `Sid`를 검색에 보내지 않음
- `txtGoStart`/`txtGoEnd`에 역 코드가 아니라 역 이름
- `qryDvCd=1` 포함
- 실제 `Key`/`Version`/UA 사용

## live 검증

- 데이터센터 direct: `403 -2000`
- dpbokji exit node: `403 -2000`

둘 다 현재 차단/합성 경로라 홈 direct의 제품 SDK 통과 여부를 대체하지 못한다. **홈 direct에서 `sdk_probe.py --live --netfunnel` 1회가 남은 결정적 테스트**다.

```powershell
.venv\Scripts\python tools\analysis\sdk_probe.py --live --netfunnel
```

- `query_success: true` → 해결. 원인은 분석 도구의 합성 요청이었다.
- `-2000` 유지 → 제품 SDK의 v2 profile(`SM-S948N`/17/board empty/strongbox0) 또는 op/Flow-2.
- `-8204` → 최신 `Version`/`AppVersion` 확인.
- `-4001` → 토큰/헤더 누락.

## 제품 코드 검증

- 전역 `KORAIL_API_VERSION`을 `250722001`로 올리는 변경은 **되돌렸다**.
- `tests/test_wire_contracts.py`가 검색 경로에서만 `250722001`을 기대하고, 나머지 작업은 `250601003`을 기대한다.
- 전역 변경 시 144개 계약 테스트가 실패했고, 되돌린 뒤 **409 passed**.
- 즉 제품 코드는 이미 검색 경로에서 올바르게 `250722001`을 오버라이드하고 있다. 문제는 분석 도구가 그 경로를 쓰지 않은 것이다.

## 판단

이 브랜치는 “분석 도구가 실제 앱 메타데이터와 달랐다”는 원인을 제거하고, 제품 SDK의 실제 요청을 검증 가능한 형태로 고정했다. 제품 기본값 자체를 바꾸는 것은 홈 direct의 제품 SDK 결과 전에는 하지 않았다. `SM-S948N`/Android 17 프로파일이 실제 2026 기기인지, `board`/`strongbox`가 문제인지는 그 1회 결과로 갈린다.

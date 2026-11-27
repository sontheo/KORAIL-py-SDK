# T11. 서비스 레벨 배포 검증

## 배포

- 브랜치 wheel: `korail_py_sdk-0.1.1-py3-none-any.whl`
- 검증 이미지: `korail-bot-korail:v2-envelope-fix`
  - base: `korail-bot-korail:bedb825`
  - `pip install --force-reinstall`로 브랜치 wheel 설치
  - 현재 `services/korail/src`·`tools` 복사
- 실행 컨테이너: `korail-bot-korail-1`
- 백업 태그: `korail-bot-korail:before-v2-envelope-20261127`
- compose override: `new/compose.override.yaml`
  - `image: korail-bot-korail:v2-envelope-fix`
  - `build: !reset null`
  - `KORAIL_NETWORK_MODE: tailscale`

## 검증 (배포된 컨테이너 내부)

### 익명 검색

`docker exec korail-bot-korail-1 python /app/tools/anonymous_readiness_probe.py --live --route tailscale --scenario basic`

```json
{"success": true, "valid_train_count": 10, "queue_admitted": true,
 "queue_complete_ok": true, "search_success": true, "route": "tailscale"}
```

pagination:

```json
{"success": true, "valid_train_count": 20, "page_requests": 3,
 "pagination_status": "adapter_verified", "second_page_valid": true}
```

### 로그인

`docker exec korail-bot-korail-1 python /app/src/login_smoke.py`

```json
{"ok": true}
```

### 예약 내역 읽기

예약 생성은 실제 승차권 거래라 자동 검증에서는 수행하지 않았다. 같은 로그인 세션에서 읽기 전용 `reservations()`를 확인했다.

```json
{"login": true, "reservation_read": true, "reservation_count": 0}
```

### 사용자 수동 검증

사용자가 텔레그램 봇에서 기차 조회 → 결제 → 티켓 확인까지 완료했다고 보고했다. 이 저장소의 자동 로그는 아니며, 실제 거래 결과는 사용자 계정에 있다.

### 테스트

- SDK: `409 passed`
- `ruff check` 통과

### 컨테이너 SDK 토큰 형식

배포 컨테이너의 `korail_py_sdk.security.declaration.DeclarationTokenProvider`를 직접 호출해 데이터 요청 봉투를 확인했다.

```text
!v=2&es=893617653734745139&ts=…&st=Android&sv=2.0.1&ai=korailplus&os=…&dm=…&iid=…
```

`mf/bd/sl/sb/kl/ec`는 포함되지 않았다. 실행 중인 봇이 짧은 데이터 봉투를 생성하는 코드를 사용한다.

## 판정

배포된 봇에서 `-2000` 없이 검색·로그인·예약 내역 읽기가 통과했고, 사용자가 봇에서 조회·결제·티켓 확인까지 완료했다. 서비스 레벨의 모바일 DynaPath 문제는 해결됐다.

## 한계

- 자동화된 전체 Telegram 흐름은 실행하지 않았다. `anonymous_readiness_probe`의 `full_bot_verified`는 `false`다. 사용자는 봇에서 조회·결제·티켓 확인을 수동으로 완료했다.
- 예약 **생성**과 결제는 실제 거래이므로 검증하지 않았다.
- 이미지는 현재 `bedb825` 위에 고정 wheel/현재 소스를 얹은 형태다. 완전한 clean Dockerfile 재빌드는 재현성 작업으로 남아 있다.
- 웹은 DevTools를 닫아도 차단된다: dpbokji에서 `-8004`, 서버 direct에서 `-8202`. 자세한 내용은 `results/T12_WEB_NODEVTOOLS.md`. 이는 모바일 API 서비스와 별개다.

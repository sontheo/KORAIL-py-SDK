# T10. 해결: v2 데이터 선언 봉투를 짧은 형식으로 교체

## 원인

`-2000`은 egress/IP가 아니라 **v2 선언 토큰의 봉투 형식**이었다.

- 기존 제품 토큰: `es=288904575606514493`, `os/dm/iid/mf/bd/sl/sb/kl/ec` 전체 포함
- 실제 데이터 토큰: `es=893617653734745139`, `!v=2&es=…&ts=…&st=Android&sv=2.0.1&ai=korailplus&os=…&dm=…&iid=…` 까지
- 서버는 긴 봉투를 `-2000`으로 거부하고, 짧은 데이터 봉투를 수락한다.

## 수정

`src/korail_py_sdk/security/declaration.py`의 `DeclarationTokenProvider`를 context-aware로 변경.

- context 없음: 기존 full 봉투 유지 (기존 테스트/직접 호출 호환)
- `login.Login` context: `es=893617653734745139` + `…&iid&mf&bd&sl&sb&kl`
- 그 외 데이터 context: `es=893617653734745139` + `…&iid` 까지 (짧은 봉투)

## 검증

### 제품 SDK live (private egress)

```bash
PYTHONPATH=src .venv/bin/python tools/analysis/sdk_probe.py \
  --live --netfunnel --proxy socks5h://<private-egress>:1055
```

3회 연속:

```json
{"query_success": true, "app_result": "SUCC", "train_count": 10}
```

### 도구 live (private egress)

```bash
PYTHONPATH=src .venv/bin/python tools/analysis/mobile_client.py \
  --host smart --token-mode v2 --token-format captured-data \
  --proxy socks5h://<private-egress>:1055
```

3회 연속 `SUCC / 10 trains`.

### 대조

- 같은 private egress 경로에서 **긴 full 봉투** → `403 -2000`
- **v1** (같은 한국 프록시) → `200 -8204` (버전 게이트) → IP는 차단되지 않음
- **alternate egress** + 짧은 봉투 → `403 -2000` + `VPN 또는 데이터센터...` → alternate egress egress는 별도로 차단
- 테스트: `409 passed`

## 산출물

- branch: `fix/mobile-v2-app-metadata`
- `src/korail_py_sdk/security/declaration.py`
- `tools/analysis/sdk_probe.py`
- `tools/analysis/mobile_client.py`
- `results/T10_SOLUTION.md`

## 남은 일

- `login.Login`의 짧은/긴 봉투 조합은 실제 로그인 없이 검증하지 못했다. 예약/로그인 흐름은 별도 확인이 필요하다.
- `consumer service` 컨테이너는 이미 설치된 SDK를 사용하므로, 이 수정을 반영하려면 이미지 재빌드/재배포가 필요하다.
- 웹 `-8003`은 DevTools를 닫은 수동 조회로 별도 확인해야 한다.

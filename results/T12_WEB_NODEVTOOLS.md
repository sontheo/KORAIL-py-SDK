# T12. 웹 표면, DevTools 없이 재확인

## 질문

- 웹 `-8003`은 DevTools/CDP를 연 상태에서만 생기는 것인가?
- DevTools를 완전히 닫고 수동으로 조회하면 웹 검색이 통과하는가?

## 방법

- Chrome for Testing 159.0.8154.6, Xvfb `:102`
- `--remote-debugging-port` 없음, Playwright/CDP 미사용
- 주소 입력·클릭·스크롤은 `xdotool`, 화면은 `ffmpeg x11grab`
- 경로 A: private egress SOCKS5 `<private-proxy>` (egress `<private-egress-address>`)
- 경로 B: 프록시 없음 (서버 direct `<server-direct-egress>`)
- 서울→부산, 기본 날짜/시간으로 `열차 조회하기` 클릭

## 결과

| 경로 | 도달 URL | 코드 | 메시지 |
|---|---|---|---|
| private egress, DevTools 없음 | `/ticket/search/list` | `-8004` | 매크로, 개발자도구 등 미허가 도구 사용 시 이용이 제한될 수 있습니다 |
| 서버 direct, DevTools 없음 | `/ticket/search/list` | `-8202` | VPN 또는 데이터센터를 통해서는 서비스를 이용할 수 없습니다 |
| private egress, DevTools/CDP (T2) | `/ticket/search/list` | `-8003` | 매크로, 개발자도구 등 미허가 도구 사용 시 이용이 제한될 수 있습니다 |

화면 증거:

- `/tmp/opencode/korail-dynapath/web-nodevtools-5.png` — private egress, `-8004`
- `/tmp/opencode/korail-dynapath/web-direct-3.png` — direct, `-8202`

## 해석

- DevTools를 없애도 웹 검색은 차단된다. `-8003`은 DevTools 전용 신호가 아니며, 같은 차단이 `-8004`로 나타난다.
- direct는 `-8202`(VPN/데이터센터)이고 private egress는 `-8202`가 아니다. private egress IP는 VPN/데이터센터로 분류되지 않는다.
- 웹은 모바일 API와 별도의 클라이언트 검증을 한다. 모바일 v2 짧은 봉투 수정은 이 웹 차단을 바꾸지 않는다.
- 봇의 텔레그램 예약 흐름은 모바일 API를 사용하므로 이 웹 차단의 영향을 받지 않는다.

## 한계

- 실제 사용자 데스크톱의 일반 Chrome이 아니라 Chrome for Testing이다. 다만 DevTools/CDP는 완전히 배제했다.
- 봇의 stealth 웹 UI 검색(`search_trains_ui`)은 파업 안내 모달에서 날짜 선택이 막혀 DynaPath 응답 전에 중단됐다. 이 실행은 웹 판정 근거가 아니다.
- 웹 우회는 이번 모바일 `-2000` 해결 범위 밖이며, 별도 과제다.

# Icon Bundler 개발자 노트

이 문서는 개발자 또는 구현 방식을 연구해 보고 싶은 사람을 위한 문서입니다.

## 프로젝트 개요

Icon Bundler는 `CustomTkinter` 기반 데스크톱 앱으로, 래스터 이미지를 아이콘 파일로 변환합니다.

현재 기능:

- 입력: `PNG`, `JPG`, `JPEG`
- 출력: `ICO`, `ICNS`
- 언어 전환: `en`, `ko`
- 릴리스 패키징: Windows / macOS용 PyInstaller

## 핵심 파일

- `main.py`: GUI, 이미지 변환 로직, 언어 즉시 갱신 로직
- `i18n.py`: `en` / `ko` 문자열 테이블
- `release/build/icon_bundler.spec`: PyInstaller spec
- `release/build/build_macos.sh`: macOS 빌드 래퍼
- `release/build/build_windows.cmd`: Windows 빌드 래퍼
- `.github/workflows/release.yml`: 릴리스 파이프라인

## 이미지 변환 로직

### 공통 흐름

앱은 공통 변환 함수를 사용합니다.

- 원본 이미지 열기
- EXIF 기준 회전 보정
- `RGBA`로 변환
- 비율 유지
- 투명한 정사각 캔버스 중앙에 배치
- 선택한 포맷으로 저장

### ICO

ICO 내보내기 크기:

- `16x16`
- `32x32`
- `48x48`
- `256x256`

크기는 오름차순으로 유지하고, 원본보다 커지는 첫 단계 전에 멈춥니다.

### ICNS

ICNS 내보내기 크기:

- `16x16`
- `32x32`
- `64x64`
- `128x128`
- `256x256`
- `512x512`
- `1024x1024`

Pillow가 ICNS 저장을 인식하도록 `PIL.IcnsImagePlugin`을 직접 import합니다.

## 언어 처리

언어 상태는 단순하게 유지합니다.

- 지원값: `en`, `ko`
- 첫 실행 기본값: `en`
- 언어 변경 시 현재 GUI 프로세스에서 등록된 위젯 텍스트를 즉시 갱신

즉시 갱신하는 이유:

- 언어 변경만을 위해 패키징된 실행 파일을 다시 실행하지 않아도 됩니다.
- 선택된 원본 이미지와 출력 미리보기를 같은 창에서 유지할 수 있습니다.
- 번역 대상 위젯을 한곳에 등록해 새 UI 텍스트도 일관되게 갱신할 수 있습니다.

초기 언어와 선택적 원본 경로는 환경변수에서 읽을 수 있습니다.

- `ICON_BUNDLER_LANGUAGE`
- `ICON_BUNDLER_SOURCE`

## 패키징

### spec 구조

PyInstaller spec는 `release/build`에서 실행되도록 작성되어 있습니다.

중요한 점:

- `ROOT = Path.cwd().resolve().parents[1]`
- `ICON_DIR = Path.cwd().resolve()`
- `i18n`을 `hiddenimports`에 포함
- Windows는 `icon.ico`
- macOS는 `icon.icns`
- macOS 결과물은 zip 안의 `.app` 번들

### 릴리스 워크플로

릴리스 워크플로는 다음을 빌드합니다.

- Windows: `windows-latest`
- macOS arm64: `macos-15`
- macOS x86_64: `macos-15-intel`

릴리스 산출물 이름:

- `IconBundler-<version>-windows.zip`
- `IconBundler-<version>-macos-arm64.zip`
- `IconBundler-<version>-macos-x86_64.zip`

## 구현 메모

- 앱은 실행 중인 동안 원본 파일 경로를 메모리에 유지합니다.
- 같은 이름의 출력 파일이 있으면 덮어쓰기 전에 확인합니다.
- 언어 변경 시 등록된 번역 대상 위젯 텍스트를 즉시 갱신합니다.
- 문자열 바인딩에는 `customtkinter.StringVar`를 사용합니다.

## 테스트

개발 의존성은 다음 명령으로 설치합니다.

```bash
pip install -r requirements-dev.txt
```

자동 변환 검사는 다음 명령으로 실행합니다.

```bash
pytest
```

## 실무 제약

- Windows 패키지는 Windows에서 빌드해야 합니다.
- macOS 패키지는 macOS에서 빌드해야 합니다.
- `ICNS` 생성은 Pillow의 ICNS 플러그인 지원에 의존합니다.
- 너무 작거나 손상된 이미지는 변환에 실패할 수 있습니다.

[English](#english) | [한국어](#korean)


<a name="english"></a>
# Icon Bundler

Icon Bundler turns a picture into an icon file.
You can use it to make `ICO` files for Windows or `ICNS` files for macOS.

## What it does

- Opens a `PNG`, `JPG`, or `JPEG` image
- Makes a Windows `ICO` file
- Makes a macOS `ICNS` file
- Keeps the picture centered and clean

## How to use

<<<<<<< HEAD
You do not need to build anything yourself.

1. Open the GitHub Releases page for this repository.
2. Download the archive for your operating system.
   - Windows: `IconBundler-<version>-windows.zip`
   - macOS arm64: `IconBundler-<version>-macos-arm64.zip`
   - macOS x86_64: `IconBundler-<version>-macos-x86_64.zip`
3. Extract the archive.
4. Open the app inside the extracted folder.
5. Select a `PNG`, `JPG`, or `JPEG` image.
6. Click either `Convert to ICO` or `Convert to ICNS`.

The output file is saved next to the source image with the same name and the matching extension. After selecting a source image, the app shows both ICO and ICNS output path candidates so you can confirm either destination before converting.

## What the app does

- The source image is selected with a file picker
- Language can be switched between `en` and `ko`
- The first launch default language is `en`
- Changing the language updates the current window immediately
- The app icon is included in the packaged release

## Export details

ICO export uses these sizes:

- `16x16`
- `32x32`
- `48x48`
- `256x256`

ICNS export uses these sizes, stopping before the first size larger than the source image:

- `16x16`
- `32x32`
- `64x64`
- `128x128`
- `256x256`
- `512x512`
- `1024x1024`

## Supported files

- `.png`
- `.jpg`
- `.jpeg`
=======
1. Download the release for your computer.
2. Open the app.
3. Pick an image.
4. Click the icon format you want.
5. Save the result next to the image.
>>>>>>> origin/main

## Notes

- The app keeps the picture size balanced.
- If a file with the same name already exists, it asks before replacing it.
- More details are in the developer guide.

<a name="korean"></a>
# Icon Bundler

[English](README.md) | [한국어](README_KO.md)

Icon Bundler는 사진을 아이콘 파일로 바꿔 주는 프로그램입니다.
Windows용 `ICO` 파일이나 macOS용 `ICNS` 파일을 만들 수 있습니다.

## 할 수 있는 일

- `PNG`, `JPG`, `JPEG` 파일 열기
- Windows용 `ICO` 만들기
- macOS용 `ICNS` 만들기
- 사진을 가운데에 맞춰 보기 좋게 처리하기

## 사용 방법

1. 내 컴퓨터에 맞는 버전을 다운로드합니다.
2. 프로그램을 엽니다.
3. 이미지를 선택합니다.
4. 원하는 아이콘 형식을 누릅니다.
5. 결과 파일을 저장합니다.

## 참고

- 사진 크기를 보기 좋게 맞춰 줍니다.
- 같은 이름의 파일이 있으면 덮어쓸지 먼저 물어봅니다.
- 자세한 설명은 개발자 문서를 보세요.


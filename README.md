# Icon Bundler

Icon Bundler is a desktop app that converts `PNG` or `JPG` images into macOS `ICNS` files or Windows `ICO` files.

The app includes two export buttons:

- `Convert to ICO`
- `Convert to ICNS`

It keeps the original aspect ratio and pads the remaining area with transparency.

## Download and use

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

## Notes

- If a file with the same name already exists, the app asks before overwriting it.
- Very small or damaged images may fail to convert.
- Windows packages must be used on Windows, and macOS packages must be used on macOS.
- The macOS package is distributed as a `.app` bundle inside the zip archive.

## Korean guide

See `README_KO.MD` for Korean instructions.

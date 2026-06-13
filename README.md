# Icon Bundler

Icon Bundler is a simple desktop app that converts a `PNG` or `JPG` image into a single `.ico` file.

The generated icon includes these sizes:

- `16x16`
- `32x32`
- `48x48`
- `256x256`

The app keeps the original aspect ratio and pads the remaining area with transparency.

## Download and use

You do not need to build anything yourself.

1. Open the GitHub Releases page for this repository.
2. Download the file for your operating system.
   - Windows: `IconBundler-<version>-windows.zip`
   - macOS arm64: `IconBundler-<version>-macos-arm64.zip`
   - macOS x86_64: `IconBundler-<version>-macos-x86_64.zip`
3. Extract the downloaded archive.
4. Open the app inside the extracted folder.
5. Select a `PNG`, `JPG`, or `JPEG` image.
6. Click `Convert to ICO`.

The output `.ico` file is saved in the same folder as the source image, using the same file name.

## In the app

- Language can be switched between `en` and `ko`
- The default language on first launch is `en`
- The source image is chosen with a file picker
- The output `.ico` file is created next to the source image

## Supported files

- `.png`
- `.jpg`
- `.jpeg`

## Notes

- If a file with the same name already exists, the app asks before overwriting it.
- Very small or damaged images may fail to convert.
- Windows builds must be used on Windows, and macOS builds must be used on macOS.

## Korean guide

If you prefer Korean, see `README_KO.MD`.

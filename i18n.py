from __future__ import annotations


DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "ko")


TEXTS = {
    "en": {
        "app_title": "Icon Bundler",
        "header_title": "PNG / JPG to Icon",
        "header_subtitle": "Save PNG or JPG images as multi-size .ico or .icns files.",
        "select_source": "Select Source Image",
        "convert_ico": "Convert to ICO",
        "convert_icns": "Convert to ICNS",
        "source_label": "Source File",
        "output_label": "Output File",
        "source_placeholder": "No file selected.",
        "output_placeholder": "No output path yet.",
        "output_candidates_placeholder": "ICO and ICNS output paths appear after selecting a source image.",
        "output_candidates_body": "ICO output: {ico_path}\nICNS output: {icns_path}",
        "status_idle": "Select a PNG or JPG file.",
        "info": "The output file is saved next to the source image with the same name and a matching extension.",
        "file_dialog_title": "Select Source Image",
        "file_dialog_image": "Image files",
        "file_dialog_png": "PNG files",
        "file_dialog_jpg": "JPG files",
        "file_dialog_error_title": "Invalid Format",
        "file_dialog_error_body": "Only PNG, JPG, and JPEG files are supported.",
        "warning_title": "File Required",
        "warning_body": "Please select a source image first.",
        "overwrite_title": "Overwrite?",
        "overwrite_body": "A file with the same name already exists.\n\n{path}\n\nDo you want to overwrite it?",
        "overwrite_cancel": "Overwrite was canceled.",
        "convert_error_title": "Conversion Failed",
        "convert_error_body": "Conversion failed.",
        "convert_done_title": "Done",
        "convert_done_body": "{format} file created.\n\n{path}",
        "success_status": "Conversion completed: {path}",
        "invalid_image": "PNG, JPG, and JPEG files only.",
        "missing_source": "Source image does not exist: {path}",
        "unsupported_output_format": "Unsupported output format.",
    },
    "ko": {
        "app_title": "Icon Bundler",
        "header_title": "PNG / JPG 아이콘 변환",
        "header_subtitle": "PNG 또는 JPG 이미지를 다중 해상도 .ico 또는 .icns 파일로 저장합니다.",
        "select_source": "원본 이미지 선택",
        "convert_ico": "ICO 변환",
        "convert_icns": "ICNS 변환",
        "source_label": "원본 파일",
        "output_label": "출력 파일",
        "source_placeholder": "파일이 선택되지 않았습니다.",
        "output_placeholder": "출력 경로가 없습니다.",
        "output_candidates_placeholder": "원본 이미지를 선택하면 ICO와 ICNS 출력 경로가 표시됩니다.",
        "output_candidates_body": "ICO 출력: {ico_path}\nICNS 출력: {icns_path}",
        "status_idle": "PNG 또는 JPG 파일을 선택하세요.",
        "info": "출력 파일명은 원본과 같은 폴더의 동일한 이름과 확장자로 생성됩니다.",
        "file_dialog_title": "원본 이미지 선택",
        "file_dialog_image": "Image files",
        "file_dialog_png": "PNG files",
        "file_dialog_jpg": "JPG files",
        "file_dialog_error_title": "형식 오류",
        "file_dialog_error_body": "PNG, JPG, JPEG 파일만 선택할 수 있습니다.",
        "warning_title": "파일 필요",
        "warning_body": "먼저 원본 이미지를 선택하세요.",
        "overwrite_title": "덮어쓰기 확인",
        "overwrite_body": "이미 같은 이름의 파일이 있습니다.\n\n{path}\n\n덮어쓰시겠습니까?",
        "overwrite_cancel": "기존 파일 덮어쓰기를 취소했습니다.",
        "convert_error_title": "변환 실패",
        "convert_error_body": "변환에 실패했습니다.",
        "convert_done_title": "완료",
        "convert_done_body": "{format} 파일을 생성했습니다.\n\n{path}",
        "success_status": "변환 완료: {path}",
        "invalid_image": "PNG, JPG, JPEG 파일만 지원합니다.",
        "missing_source": "원본 이미지가 존재하지 않습니다: {path}",
        "unsupported_output_format": "지원하지 않는 출력 형식입니다.",
    },
}


def get_text(language: str, key: str) -> str:
    lang = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return TEXTS[lang][key]

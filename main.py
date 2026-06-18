from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    from PIL import Image, ImageOps
    import PIL.IcnsImagePlugin  # registers ICNS save support
except ImportError as exc:
    raise SystemExit(
        "Missing dependencies. Install them with `pip install -r requirements.txt`."
    ) from exc

from i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, get_text


ICO_SIZES = [(16, 16), (32, 32), (48, 48), (256, 256)]
ICNS_SIZES = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
OUTPUT_FORMATS = {
    "ICO": {"suffix": ".ico", "sizes": ICO_SIZES},
    "ICNS": {"suffix": ".icns", "sizes": ICNS_SIZES},
}
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
LANG_ENV = "ICON_BUNDLER_LANGUAGE"
SOURCE_ENV = "ICON_BUNDLER_SOURCE"

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9
    RESAMPLE_LANCZOS = Image.LANCZOS


class IconConversionError(Exception):
    """Base error for expected icon conversion failures."""


class MissingSourceError(IconConversionError):
    """Raised when the source image path does not exist."""

    def __init__(self, source_path: Path) -> None:
        super().__init__(str(source_path))
        self.source_path = source_path


class UnsupportedSourceError(IconConversionError):
    """Raised when the source image is not a supported file type."""


class UnsupportedOutputFormatError(IconConversionError):
    """Raised when an output format or suffix is not supported."""


def validate_source_path(source_path: Path) -> None:
    """Validate that the source path points to a supported image file."""
    if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedSourceError("PNG, JPG, JPEG files only.")
    if not source_path.is_file():
        raise MissingSourceError(source_path)


def get_output_config(output_suffix: str, format_name: str) -> dict[str, object]:
    """Return output settings after validating a format/suffix pair."""
    output_config = OUTPUT_FORMATS.get(format_name)
    if output_config is None or output_config["suffix"] != output_suffix:
        raise UnsupportedOutputFormatError(f"Unsupported output format: {format_name} ({output_suffix})")
    return output_config


def build_icon_source(image: Image.Image, canvas_size: int) -> Image.Image:
    """Resize the source image into a square RGBA canvas for icon export."""
    prepared = ImageOps.exif_transpose(image).convert("RGBA")
    # Keep the original aspect ratio and pad with transparency instead of stretching.
    contained = ImageOps.contain(
        prepared,
        (canvas_size, canvas_size),
        method=RESAMPLE_LANCZOS,
    )

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset_x = (canvas_size - contained.width) // 2
    offset_y = (canvas_size - contained.height) // 2
    canvas.alpha_composite(contained, (offset_x, offset_y))
    return canvas


def build_icon_sizes(original_size: tuple[int, int], available_sizes: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Keep sizes in ascending order and stop before the first upscale."""
    max_dimension = min(original_size)
    selected_sizes = [size for size in available_sizes if size[0] <= max_dimension and size[1] <= max_dimension]
    if not selected_sizes:
        selected_sizes = [available_sizes[0]]
    return selected_sizes


def convert_image(source_path: Path, output_suffix: str, format_name: str) -> Path:
    """Convert a PNG/JPG image into a multi-size icon file."""
    validate_source_path(source_path)
    output_config = get_output_config(output_suffix, format_name)

    output_path = source_path.with_suffix(output_suffix)

    with Image.open(source_path) as image:
        icon_sizes = build_icon_sizes(image.size, output_config["sizes"])
        canvas_size = icon_sizes[-1][0]
        icon_base = build_icon_source(image, canvas_size)
        icon_base.save(output_path, format=format_name, sizes=icon_sizes)

    return output_path


class IconBundlerApp(ctk.CTk):
    def __init__(self, initial_language: str = DEFAULT_LANGUAGE, initial_source: str | None = None) -> None:
        super().__init__()

        self.language = ctk.StringVar(value=initial_language if initial_language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE)
        self.title(get_text(self.language.get(), "app_title"))
        self.geometry("640x640")
        self.minsize(640, 640)

        self.source_path = self._validated_source(initial_source)
        self.output_suffix = ".ico"
        self.translatable_widgets: list[tuple[Any, str]] = []
        self.source_var = ctk.StringVar(value=get_text(self.language.get(), "source_placeholder"))
        self.output_var = ctk.StringVar(value=get_text(self.language.get(), "output_placeholder"))
        self.output_candidates_var = ctk.StringVar(value=get_text(self.language.get(), "output_candidates_placeholder"))
        self.status_var = ctk.StringVar(value=get_text(self.language.get(), "status_idle"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()
        self._sync_source_display()

    def _translatable_label(self, parent: Any, text_key: str, **kwargs: Any) -> ctk.CTkLabel:
        label = ctk.CTkLabel(parent, text=get_text(self.language.get(), text_key), **kwargs)
        self.translatable_widgets.append((label, text_key))
        return label

    def _translatable_button(self, parent: Any, text_key: str, **kwargs: Any) -> ctk.CTkButton:
        button = ctk.CTkButton(parent, text=get_text(self.language.get(), text_key), **kwargs)
        self.translatable_widgets.append((button, text_key))
        return button

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=18)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        self.title_label = self._translatable_label(
            header,
            "header_title",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        self.subtitle_label = self._translatable_label(
            header,
            "header_subtitle",
            text_color="#8a8f98",
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        language_menu = ctk.CTkOptionMenu(
            header,
            values=list(SUPPORTED_LANGUAGES),
            variable=self.language,
            command=self.change_language,
            width=100,
        )
        language_menu.grid(row=0, column=1, padx=20, pady=(20, 4), sticky="e")

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, corner_radius=18)
        body.grid(row=1, column=0, padx=18, pady=10, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=0)

        self.select_button = self._translatable_button(
            body,
            "select_source",
            command=self.select_source_file,
            width=160,
        )
        self.select_button.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        self.convert_ico_button = self._translatable_button(
            body,
            "convert_ico",
            command=lambda: self.convert_clicked(".ico", "ICO"),
            width=120,
        )
        self.convert_ico_button.grid(row=0, column=1, padx=(20, 8), pady=(20, 12), sticky="e")

        self.convert_icns_button = self._translatable_button(
            body,
            "convert_icns",
            command=lambda: self.convert_clicked(".icns", "ICNS"),
            width=120,
        )
        self.convert_icns_button.grid(row=0, column=2, padx=(8, 20), pady=(20, 12), sticky="e")

        self.source_label = self._translatable_label(body, "source_label")
        self.source_label.grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        source_value = ctk.CTkLabel(
            body,
            textvariable=self.source_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        source_value.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        self.output_label = self._translatable_label(body, "output_label")
        self.output_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")

        output_value = ctk.CTkLabel(
            body,
            textvariable=self.output_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        output_value.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        output_candidates = ctk.CTkLabel(
            body,
            textvariable=self.output_candidates_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        output_candidates.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        self.info_label = self._translatable_label(
            body,
            "info",
            text_color="#8a8f98",
            wraplength=560,
            justify="left",
        )
        self.info_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(12, 18), sticky="w")

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, corner_radius=16)
        footer.grid(row=2, column=0, padx=18, pady=(10, 18), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        status = ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        status.grid(row=0, column=0, padx=18, pady=14, sticky="ew")

    def select_source_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title=get_text(self.language.get(), "file_dialog_title"),
            filetypes=[
                (get_text(self.language.get(), "file_dialog_image"), "*.png *.jpg *.jpeg"),
                (get_text(self.language.get(), "file_dialog_png"), "*.png"),
                (get_text(self.language.get(), "file_dialog_jpg"), "*.jpg *.jpeg"),
            ],
        )
        if not file_path:
            return

        source = Path(file_path)
        source_error = self._message_for_exception(self._source_error(source))
        if source_error:
            messagebox.showerror(
                get_text(self.language.get(), "file_dialog_error_title"),
                source_error,
            )
            return

        self.source_path = source
        self.source_var.set(str(source))
        self.output_suffix = ".ico"
        self.output_var.set(str(source.with_suffix(self.output_suffix)))
        self.status_var.set(get_text(self.language.get(), "status_idle"))

    def convert_clicked(self, output_suffix: str, format_name: str) -> None:
        if self.source_path is None:
            messagebox.showwarning(
                get_text(self.language.get(), "warning_title"),
                get_text(self.language.get(), "warning_body"),
            )
            return

        source_error = self._message_for_exception(self._source_error(self.source_path))
        if source_error:
            messagebox.showerror(get_text(self.language.get(), "convert_error_title"), source_error)
            self.status_var.set(source_error)
            return

        self.output_suffix = output_suffix
        self._sync_source_display()
        output_path = self.source_path.with_suffix(output_suffix)
        if output_path.exists():
            overwrite = messagebox.askyesno(
                get_text(self.language.get(), "overwrite_title"),
                get_text(self.language.get(), "overwrite_body").format(path=output_path),
            )
            if not overwrite:
                self.status_var.set(get_text(self.language.get(), "overwrite_cancel"))
                return

        try:
            result = convert_image(self.source_path, output_suffix, format_name)
        except IconConversionError as exc:
            error_message = self._message_for_exception(exc)
            messagebox.showerror(get_text(self.language.get(), "convert_error_title"), error_message)
            self.status_var.set(error_message)
            return
        except Exception as exc:
            messagebox.showerror(
                get_text(self.language.get(), "convert_error_title"),
                str(exc) or get_text(self.language.get(), "convert_error_body"),
            )
            self.status_var.set(get_text(self.language.get(), "convert_error_body"))
            return

        self.output_var.set(str(result))
        self.status_var.set(get_text(self.language.get(), "success_status").format(path=result))
        messagebox.showinfo(
            get_text(self.language.get(), "convert_done_title"),
            get_text(self.language.get(), "convert_done_body").format(format=format_name, path=result),
        )

    def change_language(self, language: str) -> None:
        if language not in SUPPORTED_LANGUAGES:
            self.language.set(DEFAULT_LANGUAGE)
            language = DEFAULT_LANGUAGE

        self._refresh_language_text()

    def _sync_source_display(self) -> None:
        if self.source_path is None:
            self.source_var.set(get_text(self.language.get(), "source_placeholder"))
            self.output_var.set(get_text(self.language.get(), "output_placeholder"))
            self.output_candidates_var.set(get_text(self.language.get(), "output_candidates_placeholder"))
        else:
            self.source_var.set(str(self.source_path))
            self.output_var.set(str(self.source_path.with_suffix(self.output_suffix)))
            self.output_candidates_var.set(
                get_text(self.language.get(), "output_candidates_body").format(
                    ico_path=self.source_path.with_suffix(".ico"),
                    icns_path=self.source_path.with_suffix(".icns"),
                )
            )

    def _source_error(self, source: Path) -> IconConversionError | None:
        try:
            validate_source_path(source)
        except IconConversionError as exc:
            return exc
        return None

    def _message_for_exception(self, exc: Exception | None) -> str | None:
        if exc is None:
            return None
        if isinstance(exc, UnsupportedSourceError):
            return get_text(self.language.get(), "invalid_image")
        if isinstance(exc, MissingSourceError):
            return get_text(self.language.get(), "missing_source").format(path=exc.source_path)
        if isinstance(exc, UnsupportedOutputFormatError):
            return get_text(self.language.get(), "unsupported_output_format")
        return str(exc) or get_text(self.language.get(), "convert_error_body")

    def _validated_source(self, initial_source: str | None) -> Path | None:
        if not initial_source:
            return None

        source = Path(initial_source)
        if self._source_error(source):
            os.environ.pop(SOURCE_ENV, None)
            return None
        return source

    def _refresh_language_text(self) -> None:
        language = self.language.get()
        self.title(get_text(language, "app_title"))
        for widget, text_key in self.translatable_widgets:
            widget.configure(text=get_text(language, text_key))
        self.status_var.set(get_text(language, "status_idle"))
        self._sync_source_display()



def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    initial_language = os.environ.get(LANG_ENV, DEFAULT_LANGUAGE)
    initial_source = os.environ.get(SOURCE_ENV)
    app = IconBundlerApp(initial_language=initial_language, initial_source=initial_source)
    app.mainloop()


if __name__ == "__main__":
    main()

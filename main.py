from __future__ import annotations

import os
from pathlib import Path

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
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
LANG_ENV = "ICON_BUNDLER_LANGUAGE"
SOURCE_ENV = "ICON_BUNDLER_SOURCE"

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9
    RESAMPLE_LANCZOS = Image.LANCZOS


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
    if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("PNG, JPG, JPEG files only.")
    if not source_path.is_file():
        raise FileNotFoundError(f"Source image does not exist: {source_path}")

    output_path = source_path.with_suffix(output_suffix)

    with Image.open(source_path) as image:
        icon_sizes = build_icon_sizes(image.size, ICNS_SIZES if format_name == "ICNS" else ICO_SIZES)
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
        self.source_var = ctk.StringVar(value=get_text(self.language.get(), "source_placeholder"))
        self.output_var = ctk.StringVar(value=get_text(self.language.get(), "output_placeholder"))
        self.status_var = ctk.StringVar(value=get_text(self.language.get(), "status_idle"))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()
        self._sync_source_display()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=18)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        self.title_label = ctk.CTkLabel(
            header,
            text=get_text(self.language.get(), "header_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            header,
            text=get_text(self.language.get(), "header_subtitle"),
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

        self.select_button = ctk.CTkButton(
            body,
            text=get_text(self.language.get(), "select_source"),
            command=self.select_source_file,
            width=160,
        )
        self.select_button.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        self.convert_ico_button = ctk.CTkButton(
            body,
            text=get_text(self.language.get(), "convert_ico"),
            command=lambda: self.convert_clicked(".ico", "ICO"),
            width=120,
        )
        self.convert_ico_button.grid(row=0, column=1, padx=(20, 8), pady=(20, 12), sticky="e")

        self.convert_icns_button = ctk.CTkButton(
            body,
            text=get_text(self.language.get(), "convert_icns"),
            command=lambda: self.convert_clicked(".icns", "ICNS"),
            width=120,
        )
        self.convert_icns_button.grid(row=0, column=2, padx=(8, 20), pady=(20, 12), sticky="e")

        self.source_label = ctk.CTkLabel(body, text=get_text(self.language.get(), "source_label"))
        self.source_label.grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        source_value = ctk.CTkLabel(
            body,
            textvariable=self.source_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        source_value.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        self.output_label = ctk.CTkLabel(body, text=get_text(self.language.get(), "output_label"))
        self.output_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")

        output_value = ctk.CTkLabel(
            body,
            textvariable=self.output_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        output_value.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        self.info_label = ctk.CTkLabel(
            body,
            text=get_text(self.language.get(), "info"),
            text_color="#8a8f98",
            wraplength=560,
            justify="left",
        )
        self.info_label.grid(row=5, column=0, columnspan=2, padx=20, pady=(12, 18), sticky="w")

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
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS or not source.is_file():
            messagebox.showerror(
                get_text(self.language.get(), "file_dialog_error_title"),
                get_text(self.language.get(), "file_dialog_error_body"),
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

        source_error = self._source_error_message(self.source_path)
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
        else:
            self.source_var.set(str(self.source_path))
            self.output_var.set(str(self.source_path.with_suffix(self.output_suffix)))

    def _source_error_message(self, source: Path) -> str | None:
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return get_text(self.language.get(), "invalid_image")
        if not source.is_file():
            return get_text(self.language.get(), "missing_source").format(path=source)
        return None

    def _validated_source(self, initial_source: str | None) -> Path | None:
        if not initial_source:
            return None

        source = Path(initial_source)
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS or not source.is_file():
            os.environ.pop(SOURCE_ENV, None)
            return None
        return source

    def _refresh_language_text(self) -> None:
        language = self.language.get()
        self.title(get_text(language, "app_title"))
        self.title_label.configure(text=get_text(language, "header_title"))
        self.subtitle_label.configure(text=get_text(language, "header_subtitle"))
        self.select_button.configure(text=get_text(language, "select_source"))
        self.convert_ico_button.configure(text=get_text(language, "convert_ico"))
        self.convert_icns_button.configure(text=get_text(language, "convert_icns"))
        self.source_label.configure(text=get_text(language, "source_label"))
        self.output_label.configure(text=get_text(language, "output_label"))
        self.info_label.configure(text=get_text(language, "info"))
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

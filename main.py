from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    from PIL import Image, ImageOps
except ImportError as exc:
    raise SystemExit(
        "Missing dependencies. Install them with `pip install -r requirements.txt`."
    ) from exc

from i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, get_text


TARGET_SIZES = [(16, 16), (32, 32), (48, 48), (256, 256)]
MAX_ICON_SIZE = 256
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
LANG_ENV = "ICON_BUNDLER_LANGUAGE"
SOURCE_ENV = "ICON_BUNDLER_SOURCE"

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:  # Pillow < 9
    RESAMPLE_LANCZOS = Image.LANCZOS


def build_icon_source(image: Image.Image) -> Image.Image:
    """Resize the source image into a square RGBA canvas for ICO export."""
    prepared = ImageOps.exif_transpose(image).convert("RGBA")
    # Keep the original aspect ratio and pad with transparency instead of stretching.
    contained = ImageOps.contain(
        prepared,
        (MAX_ICON_SIZE, MAX_ICON_SIZE),
        method=RESAMPLE_LANCZOS,
    )

    canvas = Image.new("RGBA", (MAX_ICON_SIZE, MAX_ICON_SIZE), (0, 0, 0, 0))
    offset_x = (MAX_ICON_SIZE - contained.width) // 2
    offset_y = (MAX_ICON_SIZE - contained.height) // 2
    canvas.alpha_composite(contained, (offset_x, offset_y))
    return canvas


def convert_image_to_ico(source_path: Path) -> Path:
    """Convert a PNG/JPG image into a multi-size ICO file."""
    if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("PNG, JPG, JPEG 파일만 변환할 수 있습니다.")

    output_path = source_path.with_suffix(".ico")

    with Image.open(source_path) as image:
        ico_base = build_icon_source(image)
        ico_base.save(output_path, format="ICO", sizes=TARGET_SIZES)

    return output_path


class IconBundlerApp(ctk.CTk):
    def __init__(self, initial_language: str = DEFAULT_LANGUAGE, initial_source: str | None = None) -> None:
        super().__init__()

        self.language = ctk.StringVar(value=initial_language if initial_language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE)
        self.title(get_text(self.language.get(), "app_title"))
        self.geometry("640x640")
        self.minsize(640, 640)

        self.source_path: Path | None = Path(initial_source) if initial_source else None
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

        title = ctk.CTkLabel(
            header,
            text=get_text(self.language.get(), "header_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text=get_text(self.language.get(), "header_subtitle"),
            text_color="#8a8f98",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

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

        select_button = ctk.CTkButton(
            body,
            text=get_text(self.language.get(), "select_source"),
            command=self.select_source_file,
            width=160,
        )
        select_button.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        convert_button = ctk.CTkButton(
            body,
            text=get_text(self.language.get(), "convert"),
            command=self.convert_clicked,
            width=120,
        )
        convert_button.grid(row=0, column=1, padx=20, pady=(20, 12), sticky="e")

        source_label = ctk.CTkLabel(body, text=get_text(self.language.get(), "source_label"))
        source_label.grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        source_value = ctk.CTkLabel(
            body,
            textvariable=self.source_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        source_value.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        output_label = ctk.CTkLabel(body, text=get_text(self.language.get(), "output_label"))
        output_label.grid(row=3, column=0, padx=20, pady=(10, 4), sticky="w")

        output_value = ctk.CTkLabel(
            body,
            textvariable=self.output_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        output_value.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        info = ctk.CTkLabel(
            body,
            text=get_text(self.language.get(), "info"),
            text_color="#8a8f98",
            wraplength=560,
            justify="left",
        )
        info.grid(row=5, column=0, columnspan=2, padx=20, pady=(12, 18), sticky="w")

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
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            messagebox.showerror(
                get_text(self.language.get(), "file_dialog_error_title"),
                get_text(self.language.get(), "file_dialog_error_body"),
            )
            return

        self.source_path = source
        self.source_var.set(str(source))
        self.output_var.set(str(source.with_suffix(".ico")))
        self.status_var.set(get_text(self.language.get(), "status_idle"))

    def convert_clicked(self) -> None:
        if self.source_path is None:
            messagebox.showwarning(
                get_text(self.language.get(), "warning_title"),
                get_text(self.language.get(), "warning_body"),
            )
            return

        output_path = self.source_path.with_suffix(".ico")
        if output_path.exists():
            overwrite = messagebox.askyesno(
                get_text(self.language.get(), "overwrite_title"),
                get_text(self.language.get(), "overwrite_body").format(path=output_path),
            )
            if not overwrite:
                self.status_var.set(get_text(self.language.get(), "overwrite_cancel"))
                return

        try:
            result = convert_image_to_ico(self.source_path)
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
            get_text(self.language.get(), "convert_done_body").format(path=result),
        )

    def change_language(self, language: str) -> None:
        if language not in SUPPORTED_LANGUAGES:
            self.language.set(DEFAULT_LANGUAGE)
            language = DEFAULT_LANGUAGE

        current_language = self.language.get()
        if language == current_language:
            return

        self._restart_with_language(language)

    def _sync_source_display(self) -> None:
        if self.source_path is None:
            self.source_var.set(get_text(self.language.get(), "source_placeholder"))
            self.output_var.set(get_text(self.language.get(), "output_placeholder"))
        else:
            self.source_var.set(str(self.source_path))
            self.output_var.set(str(self.source_path.with_suffix(".ico")))

    def _restart_with_language(self, language: str) -> None:
        env = os.environ.copy()
        env[LANG_ENV] = language
        if self.source_path is not None:
            env[SOURCE_ENV] = str(self.source_path)
        else:
            env.pop(SOURCE_ENV, None)

        subprocess.Popen([sys.executable, *sys.argv], env=env)
        self.destroy()


def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    initial_language = os.environ.get(LANG_ENV, DEFAULT_LANGUAGE)
    initial_source = os.environ.get(SOURCE_ENV)
    app = IconBundlerApp(initial_language=initial_language, initial_source=initial_source)
    app.mainloop()


if __name__ == "__main__":
    main()

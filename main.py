from __future__ import annotations

from pathlib import Path

from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    from PIL import Image, ImageOps
except ImportError as exc:
    raise SystemExit(
        "Missing dependencies. Install them with `pip install -r requirements.txt`."
    ) from exc


TARGET_SIZES = [(16, 16), (32, 32), (48, 48), (256, 256)]
MAX_ICON_SIZE = 256
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

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
    def __init__(self) -> None:
        super().__init__()

        self.title("Icon Bundler")
        self.geometry("640x360")
        self.minsize(640, 360)

        self.source_path: Path | None = None
        self.source_var = ctk.StringVar(value="파일이 선택되지 않았습니다.")
        self.output_var = ctk.StringVar(value="출력 경로가 없습니다.")
        self.status_var = ctk.StringVar(value="PNG 또는 JPG 파일을 선택하세요.")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=18)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="PNG / JPG to ICO",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="16, 32, 48, 256 해상도를 하나의 .ico 파일로 저장합니다.",
            text_color="#8a8f98",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, corner_radius=18)
        body.grid(row=1, column=0, padx=18, pady=10, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)

        select_button = ctk.CTkButton(
            body,
            text="원본 이미지 선택",
            command=self.select_source_file,
            width=160,
        )
        select_button.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        convert_button = ctk.CTkButton(
            body,
            text="ICO 변환",
            command=self.convert_clicked,
            width=120,
        )
        convert_button.grid(row=0, column=1, padx=20, pady=(20, 12), sticky="e")

        source_label = ctk.CTkLabel(body, text="원본 파일")
        source_label.grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        source_value = ctk.CTkLabel(
            body,
            textvariable=self.source_var,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        source_value.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        output_label = ctk.CTkLabel(body, text="출력 파일")
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
            text="출력 파일명은 원본과 같은 폴더의 동일한 이름(.ico)으로 생성됩니다.",
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
            title="원본 이미지 선택",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("JPG files", "*.jpg *.jpeg"),
            ],
        )
        if not file_path:
            return

        source = Path(file_path)
        if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            messagebox.showerror("형식 오류", "PNG, JPG, JPEG 파일만 선택할 수 있습니다.")
            return

        self.source_path = source
        self.source_var.set(str(source))
        self.output_var.set(str(source.with_suffix(".ico")))
        self.status_var.set("선택한 파일을 변환할 준비가 되었습니다.")

    def convert_clicked(self) -> None:
        if self.source_path is None:
            messagebox.showwarning("파일 필요", "먼저 원본 이미지를 선택하세요.")
            return

        output_path = self.source_path.with_suffix(".ico")
        if output_path.exists():
            overwrite = messagebox.askyesno(
                "덮어쓰기 확인",
                f"이미 같은 이름의 파일이 있습니다.\n\n{output_path}\n\n덮어쓰시겠습니까?",
            )
            if not overwrite:
                self.status_var.set("기존 파일 덮어쓰기를 취소했습니다.")
                return

        try:
            result = convert_image_to_ico(self.source_path)
        except Exception as exc:
            messagebox.showerror("변환 실패", str(exc))
            self.status_var.set("변환에 실패했습니다.")
            return

        self.output_var.set(str(result))
        self.status_var.set(f"변환 완료: {result}")
        messagebox.showinfo("완료", f"ICO 파일을 생성했습니다.\n\n{result}")


def main() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = IconBundlerApp()
    app.mainloop()


if __name__ == "__main__":
    main()

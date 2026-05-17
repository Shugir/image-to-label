import os
from PIL import Image, ImageDraw, ImageFont

# Brother QL-810W, 62mm continuous tape (DK-22205)
PRINTER_MODEL = "QL-810W"
LABEL_TYPE = "62"

# 62mm tape at 300dpi: printable width = 696px
LABEL_WIDTH_PX = 696
MARGIN_PX = 20
PRINT_WIDTH_PX = LABEL_WIDTH_PX - 2 * MARGIN_PX  # 656px usable

# Formatter uses WIDTH=55 chars; calculate font size to fit
CHARS_PER_LINE = 55


def _load_font():
    size = max(16, int(PRINT_WIDTH_PX / CHARS_PER_LINE / 0.62))
    candidates = [
        "C:/Windows/Fonts/cour.ttf",    # Courier New
        "C:/Windows/Fonts/consola.ttf", # Consolas
        "C:/Windows/Fonts/lucon.ttf",   # Lucida Console
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size), size
    return ImageFont.load_default(), 10


def render_label_image(text: str) -> Image.Image:
    font, size = _load_font()
    lines = text.split("\n")

    # Measure line height
    probe = Image.new("L", (1, 1))
    draw = ImageDraw.Draw(probe)
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    line_h = bbox[3] - bbox[1] + 4

    img_height = len(lines) * line_h + 2 * MARGIN_PX
    img = Image.new("L", (LABEL_WIDTH_PX, img_height), 255)
    draw = ImageDraw.Draw(img)

    y = MARGIN_PX
    for line in lines:
        draw.text((MARGIN_PX, y), line, font=font, fill=0)
        y += line_h

    return img


def discover_printers():
    """Returns list of (display_name, identifier) for connected Brother printers."""
    devices = []
    try:
        from brother_ql.backends.helpers import discover
        for backend in ("pyusb", "network"):
            try:
                found = discover(backend_identifier=backend)
                for d in found:
                    devices.append((f"{backend.upper()}: {d}", d, backend))
            except Exception:
                pass
    except ImportError:
        pass
    return devices  # list of (label, identifier, backend)


def print_label(text: str, printer_identifier: str, copies: int = 1) -> bool:
    try:
        from brother_ql.raster import BrotherQLRaster
        from brother_ql.conversion import convert
        from brother_ql.backends.helpers import send

        img = render_label_image(text)

        raster = BrotherQLRaster(PRINTER_MODEL)
        instructions = convert(
            qlr=raster,
            images=[img],
            label=LABEL_TYPE,
            rotate="0",
            threshold=70.0,
            dither=False,
            compress=False,
            red=False,
            dpi_600=False,
            hq=True,
            cut=True,
        )

        backend = "network" if printer_identifier.startswith("tcp://") else "pyusb"

        for _ in range(copies):
            send(
                instructions=instructions,
                printer_identifier=printer_identifier,
                backend_identifier=backend,
                blocking=True,
            )
        return True
    except Exception as e:
        print(f"Print error: {e}")
        return False

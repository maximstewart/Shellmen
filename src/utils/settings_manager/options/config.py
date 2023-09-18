# Python imports
from dataclasses import dataclass, field

# Lib imports

# Application imports


@dataclass
class Config:
    thumbnailer_path: str            = "ffmpegthumbnailer"
    blender_thumbnailer_path: str    = ""
    mplayer_options: str             = "-quiet -really-quiet -xy 1600 -geometry 50%:50%"
    music_app: str                   = "deadbeef"
    media_app: str                   = "mpv"
    image_app: str                   = "mirage"
    office_app: str                  = "libreoffice"
    pdf_app: str                     = "evince"
    code_app: str                    = "atom"
    text_app: str                    = "mousepad"
    terminal_app: str                = "terminator"
    file_manager_app: str            = "solarfm"
    container_icon_wh: list          = field(default_factory=lambda: [128, 128])
    video_icon_wh: list              = field(default_factory=lambda: [128, 64])
    sys_icon_wh: list                = field(default_factory=lambda: [56, 56])
    steam_cdn_url: str               = "https://steamcdn-a.akamaihd.net/steam/apps/"
    remux_folder_max_disk_usage: str = "8589934592"
    application_dirs: list           = field(default_factory=lambda: [
        "/usr/share/applications",
        f"{settings_manager.get_home_path()}/.local/share/applications"
    ])

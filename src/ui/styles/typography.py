"""Fuentes Material Design 3"""

# Implements Dart AI Task: Extract typography configuration

from ..config import UIConfig


def get_fonts() -> dict:
    """Return MD3 font definitions using the configured font family."""
    # Centralizar la familia de fuentes para toda la aplicación
    font_family = UIConfig.FONT_FAMILY

    return {
        # Display
        "display-large": {
            "font": f"{font_family}",
            "size": "57px",
            "line-height": "64px",
            "weight": "400",
            "tracking": "-0.25px",
        },
        "display-medium": {
            "font": f"{font_family}",
            "size": "45px",
            "line-height": "52px",
            "weight": "400",
            "tracking": "0px",
        },
        "display-small": {
            "font": f"{font_family}",
            "size": "36px",
            "line-height": "44px",
            "weight": "400",
            "tracking": "0px",
        },
        # Headline
        "headline-large": {
            "font": f"{font_family}",
            "size": "32px",
            "line-height": "40px",
            "weight": "400",
            "tracking": "0px",
        },
        "headline-medium": {
            "font": f"{font_family}",
            "size": "28px",
            "line-height": "36px",
            "weight": "400",
            "tracking": "0px",
        },
        "headline-small": {
            "font": f"{font_family}",
            "size": "24px",
            "line-height": "32px",
            "weight": "400",
            "tracking": "0px",
        },
        # Title
        "title-large": {
            "font": f"{font_family}",
            "size": "22px",
            "line-height": "28px",
            "weight": "500",
            "tracking": "0px",
        },
        "title-medium": {
            "font": f"{font_family}",
            "size": "16px",
            "line-height": "24px",
            "weight": "500",
            "tracking": "0.15px",
        },
        "title-small": {
            "font": f"{font_family}",
            "size": "14px",
            "line-height": "20px",
            "weight": "500",
            "tracking": "0.1px",
        },
        # Body
        "body-large": {
            "font": f"{font_family}",
            "size": "16px",
            "line-height": "24px",
            "weight": "400",
            "tracking": "0.15px",
        },
        "body-medium": {
            "font": f"{font_family}",
            "size": "14px",
            "line-height": "20px",
            "weight": "400",
            "tracking": "0.25px",
        },
        "body-small": {
            "font": f"{font_family}",
            "size": "12px",
            "line-height": "16px",
            "weight": "400",
            "tracking": "0.4px",
        },
        # Label
        "label-large": {
            "font": f"{font_family}",
            "size": "14px",
            "line-height": "20px",
            "weight": "500",
            "tracking": "0.1px",
        },
        "label-medium": {
            "font": f"{font_family}",
            "size": "12px",
            "line-height": "16px",
            "weight": "500",
            "tracking": "0.5px",
        },
        "label-small": {
            "font": f"{font_family}",
            "size": "11px",
            "line-height": "16px",
            "weight": "500",
            "tracking": "0.5px",
        },
    }

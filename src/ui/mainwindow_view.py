from __future__ import annotations

import logging
import re
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton

from .ui_mainwindow import Ui_MainWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(780, 800)

        self._base_window_size = QSize()
        self._base_dpi = 96.0
        self._font_scale_targets: list[dict] = []
        self._specs_html_base: str | None = None
        self._loading_overlay: QWidget | None = None
        self._loading_label: QLabel | None = None
        self._font_scale_excludes: set[QWidget] = set()

        self.setWindowTitle("PC사양 확인 프로그램")
        self.ui.labelTitle.setMargin(0)

        self._enhance_ui_layout()

        self.ui.textSpecs.setReadOnly(True)
        self.ui.textSpecs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ui.textSpecs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._base_dpi = float(self.logicalDpiX())
        self._normalize_stylesheet_font_sizes(self._font_scale_widget_list())
        self._set_font_scale_excludes()

        self._base_window_size = self.size()
        self._font_scale_targets = self._build_font_scale_targets(
            self._font_scale_widget_list(include_sidebar=True)
        )

        logger.info("MainWindow 초기화 완료")

    def _enhance_ui_layout(self) -> None:
        self.ui.labelTitle.setText("PC사양 확인 프로그램")
        self.ui.labelTitle.setAlignment(Qt.AlignCenter)
        self.ui.labelTitle.setStyleSheet(
            "color: #0f172a; font-size: 22pt; font-weight: 700; letter-spacing: -0.4px;"
            "font-family: 'Noto Sans KR';"
        )
        self.ui.labelTitle.setMaximumHeight(74)
        self.ui.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.ui.horizontalLayout_6.setSpacing(0)
        self.ui.verticalLayout_5.setSpacing(6)
        self.ui.verticalLayout_3.setContentsMargins(56, 6, 56, 6)

        self.labelSubTitle = QLabel(
            "현장 점검부터 견적 전 확인까지, 한 화면에서 빠르게 확인하세요.",
            self.ui.contentArea,
        )
        self.labelSubTitle.setAlignment(Qt.AlignCenter)
        self.labelSubTitle.setStyleSheet(
            "color: #475569; font-size: 10.2pt; font-family: 'Noto Sans KR';"
        )
        self.ui.verticalLayout_5.insertWidget(1, self.labelSubTitle)

        self.labelLastUpdated = QLabel("마지막 수집: 아직 수집되지 않음", self.ui.contentArea)
        self.labelLastUpdated.setAlignment(Qt.AlignCenter)
        self.labelLastUpdated.setStyleSheet(
            "color: #64748b; font-size: 9.2pt; font-family: 'Noto Sans KR';"
            "padding: 2px 0 2px 0;"
        )
        self.ui.verticalLayout_5.insertWidget(2, self.labelLastUpdated)

        self.ui.textSpecs.setStyleSheet(
            "QTextEdit {"
            "background: #ffffff;"
            "border: 1px solid #d6deeb;"
            "border-radius: 12px;"
            "padding: 14px 24px;"
            "selection-background-color: #c4ddff;"
            "selection-color: #0f172a;"
            "}"
            "QTextEdit::viewport { background: transparent; }"
            "QTextEdit:focus { border: 1px solid #2a6fd8; }"
        )
        self.ui.textSpecs.setMinimumHeight(450)
        self.ui.textSpecs.setMaximumWidth(760)

        self.ui.btnRefreshSpecs = QPushButton("다시 수집", self.ui.contentArea)
        self.ui.btnSaveSpecs = QPushButton("사양 저장", self.ui.contentArea)

        for button in [self.ui.btnRefreshSpecs, self.ui.btnSaveSpecs, self.ui.btnCopySpecs]:
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(42)

        self.ui.btnRefreshSpecs.setStyleSheet(
            "QPushButton {"
            "background-color: #f8fafc; color: #334155; border: 1px solid #cbd5e1;"
            "border-radius: 10px; padding: 8px 18px; font-size: 10.5pt; font-weight: 600;"
            "font-family: 'Noto Sans KR';"
            "}"
            "QPushButton:hover { background-color: #f1f5f9; border-color: #94a3b8; }"
            "QPushButton:pressed { background-color: #e2e8f0; border-color: #64748b; }"
        )
        self.ui.btnSaveSpecs.setStyleSheet(
            "QPushButton {"
            "background-color: #2a6fd8; color: #ffffff; border: 1px solid #2a6fd8;"
            "border-radius: 10px; padding: 8px 18px; font-size: 10.5pt; font-weight: 600;"
            "font-family: 'Noto Sans KR';"
            "}"
            "QPushButton:hover { background-color: #245eb7; border-color: #245eb7; }"
            "QPushButton:pressed { background-color: #1d4f98; border-color: #1d4f98; }"
        )
        self.ui.btnCopySpecs.setStyleSheet(
            "QPushButton {"
            "background-color: #1e293b; color: #ffffff; border: 1px solid #1e293b;"
            "border-radius: 10px; padding: 8px 18px; font-size: 10.5pt; font-weight: 600;"
            "font-family: 'Noto Sans KR';"
            "}"
            "QPushButton:hover { background-color: #334155; border-color: #334155; }"
            "QPushButton:pressed { background-color: #0f172a; border-color: #0f172a; }"
        )

        self.ui.horizontalLayout_7.insertWidget(1, self.ui.btnRefreshSpecs)
        self.ui.horizontalLayout_7.insertWidget(2, self.ui.btnSaveSpecs)
        self.ui.horizontalLayout_7.setSpacing(10)
        self.ui.verticalLayout_5.setStretch(0, 0)
        self.ui.verticalLayout_5.setStretch(1, 0)
        self.ui.verticalLayout_5.setStretch(2, 0)
        self.ui.verticalLayout_5.setStretch(3, 1)
        self.ui.verticalLayout_5.setStretch(4, 0)

        self.ui.labelComment.setText(
            "* 일부 PC 환경에서는 OS/드라이버 정책에 따라 특정 항목이 비어 있을 수 있습니다."
        )
        self.ui.labelComment.setStyleSheet(
            "color: #667085; font-size: 9.4pt; font-family: 'Noto Sans KR';"
        )

    def set_last_updated_text(self, text: str) -> None:
        self.labelLastUpdated.setText(text)

    def _normalize_stylesheet_font_sizes(self, widgets: list) -> None:
        base_dpi = self._base_dpi
        for widget in widgets:
            style = widget.styleSheet()
            if not style:
                continue

            def _replace(match) -> str:
                pt_size = float(match.group(2))
                px_size = round(pt_size * base_dpi / 72)
                return f"{match.group(1)}{px_size}px"

            new_style = re.sub(
                r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)pt",
                _replace,
                style,
                flags=re.IGNORECASE,
            )
            if new_style != style:
                widget.setStyleSheet(new_style)

    def _font_scale_widget_list(self, include_sidebar: bool = False) -> list[QWidget]:
        return [
            self.ui.labelTitle,
            self.labelSubTitle,
            self.labelLastUpdated,
            self.ui.labelComment,
            self.ui.btnRefreshSpecs,
            self.ui.btnSaveSpecs,
            self.ui.btnCopySpecs,
        ]

    def _set_font_scale_excludes(self) -> None:
        self._font_scale_excludes = set()

    def _build_font_scale_targets(self, widgets: list) -> list[dict]:
        targets = []
        base_dpi = self._base_dpi
        pattern = re.compile(r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)(px|pt)", re.IGNORECASE)

        for widget in widgets:
            if widget in self._font_scale_excludes:
                continue
            style = widget.styleSheet()
            match = pattern.search(style or "")
            if match:
                size_value = float(match.group(2))
                unit = match.group(3).lower()
                base_px = size_value if unit == "px" else size_value * base_dpi / 72
                targets.append({
                    "widget": widget,
                    "base_px": base_px,
                    "style": style,
                    "use_style": True,
                })
                continue

            base_px = self._get_pixel_font_size(widget.font())
            targets.append({
                "widget": widget,
                "base_px": base_px,
                "style": "",
                "use_style": False,
            })

        return targets

    def _get_pixel_font_size(self, font: QFont) -> float:
        if font.pixelSize() > 0:
            return float(font.pixelSize())
        point_size = font.pointSizeF()
        if point_size <= 0:
            return 12.0
        return point_size * self._base_dpi / 72

    def _apply_scaled_fonts(self, scale: float) -> None:
        pattern = re.compile(r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)(px|pt)", re.IGNORECASE)

        for target in self._font_scale_targets:
            widget = target["widget"]
            base_px = target["base_px"]
            new_px = max(8, round(base_px * scale))
            if target["use_style"]:
                style = target["style"]
                new_style = pattern.sub(
                    lambda m: f"{m.group(1)}{new_px}px",
                    style,
                    count=1,
                )
                if new_style != widget.styleSheet():
                    widget.setStyleSheet(new_style)
            else:
                font = widget.font()
                font.setPixelSize(new_px)
                widget.setFont(font)

    def set_specs_html(self, html: str) -> None:
        self._specs_html_base = html
        scale = self._compute_ui_scale()
        self._apply_scaled_specs_html(scale)

    def show_loading_overlay(self, message: str = "로딩 중입니다...") -> None:
        if not self._loading_overlay:
            self._loading_overlay = QWidget(self.centralWidget())
            self._loading_overlay.setStyleSheet("background-color: #F5F7FA;")
            layout = QVBoxLayout(self._loading_overlay)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            self._loading_label = QLabel(message, self._loading_overlay)
            self._loading_label.setAlignment(Qt.AlignCenter)
            self._loading_label.setStyleSheet(
                "color: #2f2f2e; font-size: 14px; font-weight: 600;"
            )
            layout.addWidget(self._loading_label)

        if self._loading_label:
            self._loading_label.setText(message)
        self._update_loading_overlay_geometry()
        self._loading_overlay.show()
        self._loading_overlay.raise_()

    def hide_loading_overlay(self) -> None:
        if self._loading_overlay:
            self._loading_overlay.hide()

    def apply_font_refresh(self) -> None:
        self._base_dpi = float(self.logicalDpiX())
        self._normalize_stylesheet_font_sizes(self._font_scale_widget_list())
        self._set_font_scale_excludes()
        self._base_window_size = self.size()
        self._font_scale_targets = self._build_font_scale_targets(
            self._font_scale_widget_list(include_sidebar=True)
        )
        self._apply_scaled_fonts(1.0)
        self._apply_scaled_specs_html(1.0)

    def _update_loading_overlay_geometry(self) -> None:
        if not self._loading_overlay:
            return
        central = self.centralWidget()
        if central:
            self._loading_overlay.setGeometry(central.rect())

    def _apply_scaled_specs_html(self, scale: float) -> None:
        if not self._specs_html_base:
            return

        def _replace(match: re.Match) -> str:
            base_pt = float(match.group(1))
            new_pt = max(8.0, round(base_pt * scale, 1))
            return f"font-size: {new_pt}pt"

        adjusted_html = re.sub(
            r"font-size\\s*:\\s*(\\d+(?:\\.\\d+)?)pt",
            _replace,
            self._specs_html_base,
            flags=re.IGNORECASE,
        )
        adjusted_html = (
            '<div style="max-width: 720px; margin: 0 auto; text-align: left;">'
            f"{adjusted_html}"
            "</div>"
        )
        self.ui.textSpecs.setHtml(adjusted_html)

    def _compute_ui_scale(self) -> float:
        scale = 1.0
        if self._base_window_size.width() > 0 and self._base_window_size.height() > 0:
            scale = min(
                self.width() / self._base_window_size.width(),
                self.height() / self._base_window_size.height(),
            )
        return scale * self._current_dpi_scale()

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self._base_window_size.width() > 0 and self._base_window_size.height() > 0:
            scale = self._compute_ui_scale()
            self._apply_scaled_fonts(scale)
            self._apply_scaled_specs_html(scale)

        self._update_loading_overlay_geometry()
        super().resizeEvent(event)

    def _current_dpi_scale(self) -> float:
        if self._base_dpi <= 0:
            return 1.0
        return float(self.logicalDpiX()) / self._base_dpi

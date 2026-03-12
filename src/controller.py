# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import QApplication, QFileDialog

from core.collector_wrapper import CollectorWrapper
from core.formatter_wrapper import FormatterWrapper
from core.interfaces import ISpecCollector, ISpecFormatter
from core.message_utils import show_error, show_information

logger = logging.getLogger(__name__)


class Controller:
    def __init__(
        self,
        view,
        spec_collector: Optional[ISpecCollector] = None,
        spec_formatter: Optional[ISpecFormatter] = None,
    ):
        self.view = view
        self.current_specs: Optional[dict] = None

        self._spec_collector = spec_collector or CollectorWrapper()
        self._spec_formatter = spec_formatter or FormatterWrapper()

        self.bind_signals()
        self.load_specs()

    def bind_signals(self) -> None:
        self.view.ui.btnRefreshSpecs.clicked.connect(self.on_refresh_specs_clicked)
        self.view.ui.btnSaveSpecs.clicked.connect(self.on_save_specs_clicked)
        self.view.ui.btnCopySpecs.clicked.connect(self.on_copy_specs_clicked)
        logger.info("시그널 바인딩 완료")

    def load_specs(self) -> None:
        try:
            logger.info("PC 사양 수집 시작")
            specs = self._spec_collector.collect_all_specs()
            self.current_specs = specs
            self.render_specs(specs)
            self._update_last_updated_time()
            logger.info("PC 사양 수집 완료")
        except Exception as e:
            self.handle_error(e)

    def on_refresh_specs_clicked(self) -> None:
        try:
            self.view.show_loading_overlay("PC 사양을 다시 수집하고 있습니다...")
            QApplication.processEvents()
            self.load_specs()
        finally:
            self.view.hide_loading_overlay()

    def on_save_specs_clicked(self) -> None:
        try:
            text = self._get_formatted_specs_text_or_notify()
            if text is None:
                return
            default_name = f"PC_Spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "사양 텍스트 저장",
                default_name,
                "Text Files (*.txt);;All Files (*)",
            )
            if not file_path:
                return

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            show_information(self.view, "저장 완료", "PC 사양 텍스트 파일을 저장했습니다.")
            logger.info("PC 사양 텍스트 저장 완료: %s", file_path)
        except Exception as e:
            show_error(
                self.view,
                "오류",
                "PC 사양 텍스트를 저장하지 못했습니다.\n\n저장 경로 권한 또는 보안 정책을 확인해 주세요.",
            )
            self.handle_error(e)

    def on_copy_specs_clicked(self) -> None:
        try:
            text = self._get_formatted_specs_text_or_notify()
            if text is None:
                return
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            show_information(self.view, "복사 완료", "PC 사양을 클립보드에 복사했습니다.")
            logger.info("PC 사양 클립보드 복사 완료")
        except Exception as e:
            show_error(
                self.view,
                "오류",
                "PC 사양을 클립보드에 복사하지 못했습니다.\n\n보안 정책 또는 권한 설정을 확인해 주세요.",
            )
            self.handle_error(e)

    def render_specs(self, specs: dict) -> None:
        try:
            html = self._spec_formatter.format_specs_html(specs)
            self.view.set_specs_html(html)
            logger.info("PC 사양 렌더링 완료")
        except Exception as e:
            logger.exception("PC 사양 렌더링 실패")
            self.handle_error(e)

    def handle_error(self, exc: Exception) -> None:
        logger.exception("오류 발생: %s", str(exc))

        error_message = "PC 사양 수집 중 오류가 발생했습니다.\n\n"
        error_message += f"원인: {exc}\n\n"
        error_message += "다시 시도해 주세요."

        show_error(self.view, "오류", error_message)

    def _update_last_updated_time(self) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.view.set_last_updated_text(f"마지막 수집: {stamp}")

    def _get_formatted_specs_text_or_notify(self) -> str | None:
        if not self.current_specs:
            show_information(self.view, "알림", "먼저 PC 사양을 수집해 주세요.")
            return None
        return self._spec_formatter.format_specs_text(self.current_specs)

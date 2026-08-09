from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.domain.reporting.export_payload import CalculationExportPayload
from app.domain.reporting.report_sections import (
    EngineeringReportSections,
    ReportSection,
    build_report_sections,
)


class PdfReportV2GenerationError(RuntimeError):
    """Raised when the structured engineering PDF cannot be generated."""


class PdfReportV2Service:
    """Generate structured compressor engineering PDF reports."""

    def generate_calculation_report(
        self,
        payload: CalculationExportPayload,
    ) -> bytes:
        """Generate a structured engineering PDF from an export payload."""

        buffer = BytesIO()

        try:
            sections = build_report_sections(payload)

            document = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=16 * mm,
                leftMargin=16 * mm,
                topMargin=16 * mm,
                bottomMargin=16 * mm,
                title=payload.title,
                author="KES Compressor Engineering Suite",
                subject="Compressor Engineering Calculation Report",
            )

            styles = getSampleStyleSheet()

            cover_title_style = ParagraphStyle(
                "KESCoverTitle",
                parent=styles["Title"],
                fontSize=20,
                leading=24,
                spaceAfter=12,
            )

            cover_subtitle_style = ParagraphStyle(
                "KESCoverSubtitle",
                parent=styles["Heading2"],
                fontSize=12,
                leading=16,
                spaceAfter=8,
            )

            section_heading_style = ParagraphStyle(
                "KESSectionHeading",
                parent=styles["Heading2"],
                fontSize=13,
                leading=16,
                spaceBefore=8,
                spaceAfter=6,
            )

            section_description_style = ParagraphStyle(
                "KESSectionDescription",
                parent=styles["BodyText"],
                fontSize=8.5,
                leading=11,
                spaceAfter=5,
            )

            body_style = ParagraphStyle(
                "KESBody",
                parent=styles["BodyText"],
                fontSize=8.5,
                leading=11,
            )

            story: list[Any] = []

            self._add_cover_page(
                story=story,
                payload=payload,
                sections=sections,
                cover_title_style=cover_title_style,
                cover_subtitle_style=cover_subtitle_style,
                body_style=body_style,
            )

            story.append(PageBreak())

            for section in (
                sections.design_basis,
                sections.inputs,
                sections.results,
                sections.validation,
                sections.engineering_notes,
                sections.revision_audit,
            ):
                self._add_section(
                    story=story,
                    section=section,
                    heading_style=section_heading_style,
                    description_style=section_description_style,
                )

            document.build(story)

            return buffer.getvalue()

        except Exception as exc:
            raise PdfReportV2GenerationError(
                "Failed to generate structured compressor engineering PDF report."
            ) from exc

        finally:
            buffer.close()

    def _add_cover_page(
        self,
        *,
        story: list[Any],
        payload: CalculationExportPayload,
        sections: EngineeringReportSections,
        cover_title_style: ParagraphStyle,
        cover_subtitle_style: ParagraphStyle,
        body_style: ParagraphStyle,
    ) -> None:
        story.append(
            Paragraph(
                "KES Compressor Engineering Suite",
                cover_title_style,
            )
        )

        story.append(
            Paragraph(
                payload.title,
                cover_subtitle_style,
            )
        )

        story.append(Spacer(1, 8 * mm))

        story.append(
            self._build_table(
                sections.metadata.data,
            )
        )

        story.append(Spacer(1, 8 * mm))

        story.append(
            Paragraph(
                "Engineering Calculation Report",
                cover_subtitle_style,
            )
        )

        story.append(
            Paragraph(
                (
                    "This document presents the recorded engineering inputs, "
                    "calculation results, validation information, and audit "
                    "metadata for the selected compressor calculation case."
                ),
                body_style,
            )
        )

    def _add_section(
        self,
        *,
        story: list[Any],
        section: ReportSection,
        heading_style: ParagraphStyle,
        description_style: ParagraphStyle,
    ) -> None:
        story.append(
            Paragraph(
                section.title,
                heading_style,
            )
        )

        if section.description:
            story.append(
                Paragraph(
                    section.description,
                    description_style,
                )
            )

        if section.data:
            story.append(
                self._build_table(
                    section.data,
                )
            )
        else:
            story.append(
                Paragraph(
                    "No data available for this section.",
                    description_style,
                )
            )

        story.append(Spacer(1, 5 * mm))

    def _build_table(
        self,
        data: dict[str, Any],
    ) -> Table:
        rows: list[list[str]] = [
            ["Parameter", "Value"],
        ]

        for key, value in data.items():
            rows.append(
                [
                    self._format_key(key),
                    self._format_value(value),
                ]
            )

        table = Table(
            rows,
            colWidths=[65 * mm, 110 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEADING", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        return table

    def _format_key(
        self,
        key: str,
    ) -> str:
        return key.replace("_", " ").strip().title()

    def _format_value(
        self,
        value: Any,
    ) -> str:
        if value is None:
            return "-"

        if isinstance(value, dict):
            return "; ".join(
                f"{self._format_key(str(key))}: {self._format_value(item)}"
                for key, item in value.items()
            )

        if isinstance(value, (list, tuple)):
            return " | ".join(self._format_value(item) for item in value)

        if isinstance(value, bool):
            return "Yes" if value else "No"

        return str(value)


pdf_report_v2_service = PdfReportV2Service()

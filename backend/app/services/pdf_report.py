from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.domain.reporting.export_payload import CalculationExportPayload


class PdfReportGenerationError(RuntimeError):
    """Raised when an engineering PDF report cannot be generated."""


class PdfReportService:
    """Generate compressor engineering PDF reports."""

    def generate_calculation_report(
        self,
        payload: CalculationExportPayload,
    ) -> bytes:
        """Generate a PDF report from an export payload."""

        buffer = BytesIO()

        try:
            document = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=18 * mm,
                leftMargin=18 * mm,
                topMargin=18 * mm,
                bottomMargin=18 * mm,
                title=payload.title,
                author="KES Compressor Engineering Suite",
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                "KESReportTitle",
                parent=styles["Title"],
                fontSize=18,
                leading=22,
                spaceAfter=10,
            )

            heading_style = ParagraphStyle(
                "KESReportHeading",
                parent=styles["Heading2"],
                fontSize=12,
                leading=15,
                spaceBefore=8,
                spaceAfter=6,
            )

            body_style = ParagraphStyle(
                "KESReportBody",
                parent=styles["BodyText"],
                fontSize=9,
                leading=12,
            )

            story: list[Any] = []

            story.append(
                Paragraph(
                    "KES Compressor Engineering Suite",
                    title_style,
                )
            )

            story.append(
                Paragraph(
                    payload.title,
                    styles["Heading1"],
                )
            )

            story.append(Spacer(1, 5 * mm))

            metadata_rows = [
                ["Calculation Code", payload.calculation_code],
                ["Calculation Type", payload.calculation_type],
                ["Status", payload.status],
                ["Revision", str(payload.revision)],
                ["Project ID", str(payload.project_id)],
                ["Calculation Case ID", str(payload.calculation_case_id)],
                ["Created At", payload.created_at.isoformat()],
                ["Updated At", payload.updated_at.isoformat()],
                [
                    "Completed At",
                    payload.completed_at.isoformat() if payload.completed_at is not None else "-",
                ],
            ]

            metadata_table = Table(
                metadata_rows,
                colWidths=[50 * mm, 115 * mm],
                repeatRows=0,
            )

            metadata_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                        ("LEADING", (0, 0), (-1, -1), 11),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )

            story.append(metadata_table)

            if payload.description:
                story.append(Spacer(1, 5 * mm))
                story.append(
                    Paragraph(
                        "Description",
                        heading_style,
                    )
                )
                story.append(
                    Paragraph(
                        payload.description,
                        body_style,
                    )
                )

            story.append(Spacer(1, 5 * mm))
            story.append(
                Paragraph(
                    "Calculation Inputs",
                    heading_style,
                )
            )
            story.append(
                self._build_key_value_table(
                    payload.input_data,
                )
            )

            story.append(Spacer(1, 5 * mm))
            story.append(
                Paragraph(
                    "Calculation Results",
                    heading_style,
                )
            )

            if payload.result_data is None:
                story.append(
                    Paragraph(
                        "No calculation results are available.",
                        body_style,
                    )
                )
            else:
                story.append(
                    self._build_key_value_table(
                        payload.result_data,
                    )
                )

            if payload.engineering_notes:
                story.append(Spacer(1, 5 * mm))
                story.append(
                    Paragraph(
                        "Engineering Notes",
                        heading_style,
                    )
                )
                story.append(
                    Paragraph(
                        payload.engineering_notes,
                        body_style,
                    )
                )

            document.build(story)

            return buffer.getvalue()

        except Exception as exc:
            raise PdfReportGenerationError(
                "Failed to generate compressor engineering PDF report."
            ) from exc

        finally:
            buffer.close()

    def _build_key_value_table(
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
            colWidths=[70 * mm, 95 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
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
            return ", ".join(self._format_value(item) for item in value)

        return str(value)


pdf_report_service = PdfReportService()

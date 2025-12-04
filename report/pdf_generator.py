"""
Générateur de rapports au format PDF avec formatage amélioré.
"""

import os
import re
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from models.report_models import FullReport
from config.settings import settings


class PDFReportGenerator:
    """Générateur de rapports au format PDF avec ReportLab."""

    def __init__(self):
        """Initialise le générateur PDF."""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Crée des styles personnalisés pour le PDF."""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Style pour les titres de section (centrés)
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=15,
            spaceBefore=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        # Style pour le corps de texte
        self.styles.add(ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            firstLineIndent=0
        ))

        # Style pour les listes à puces
        self.styles.add(ParagraphStyle(
            name='BulletText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=20,
            spaceAfter=8
        ))

        # Style pour les informations en gras
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=8
        ))

    def _clean_markdown(self, text: str) -> str:
        """
        Nettoie le texte Markdown et le convertit en HTML pour ReportLab.

        Args:
            text: Texte potentiellement avec formatage Markdown

        Returns:
            Texte nettoyé avec balises HTML
        """
        if not text:
            return ""

        # Remplacer les doubles astérisques par des balises bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)

        # Remplacer les simples astérisques par des balises italic
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)

        # Remplacer les tirets de liste par des puces
        text = re.sub(r'^[-•]\s+', '• ', text, flags=re.MULTILINE)

        # Nettoyer les doubles espaces
        text = re.sub(r'\s+', ' ', text)

        # Échapper les caractères spéciaux XML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        # Restaurer les balises HTML que nous avons ajoutées
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')

        return text.strip()

    def _split_into_paragraphs(self, text: str) -> list:
        """
        Divise le texte en paragraphes.

        Args:
            text: Texte à diviser

        Returns:
            Liste de paragraphes
        """
        # Diviser par double saut de ligne
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]

    def generate(
        self,
        report: FullReport,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Génère un rapport PDF.

        Args:
            report: Rapport complet à générer
            output_filename: Nom du fichier de sortie (optionnel)

        Returns:
            Chemin du fichier PDF généré
        """
        # Générer le nom de fichier si non fourni
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = report.cover_page.client_name.replace(" ", "_")
            output_filename = f"rapport_{client_name}_{timestamp}.pdf"

        output_path = os.path.join(settings.reports_output_dir, output_filename)

        # Créer le document PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )

        # Construire le contenu
        story = []

        # 1. Page de garde
        story.extend(self._build_cover_page(report))
        story.append(PageBreak())

        # 2. Résumé exécutif
        story.extend(self._build_executive_summary(report))
        story.append(PageBreak())

        # 3. Contexte & Périmètre
        story.extend(self._build_context_scope(report))
        story.append(PageBreak())

        # 4. Méthodologie
        story.extend(self._build_methodology(report))
        story.append(PageBreak())

        # 5. Analyse globale
        story.extend(self._build_global_analysis(report))
        story.append(PageBreak())

        # 6. Findings détaillés
        story.extend(self._build_findings(report))
        story.append(PageBreak())

        # 7. Plan d'action
        story.extend(self._build_action_plan(report))
        story.append(PageBreak())

        # 8. Conclusion
        story.extend(self._build_conclusion(report))

        # Générer le PDF
        doc.build(story)

        return output_path

    def _build_cover_page(self, report: FullReport) -> list:
        """Construit la page de garde."""
        elements = []

        elements.append(Spacer(1, 4*cm))

        # Titre
        title = self._clean_markdown(report.cover_page.title)
        elements.append(Paragraph(title, self.styles['CustomTitle']))

        elements.append(Spacer(1, 3*cm))

        # Informations du client - centrées et stylisées
        info_data = [
            [Paragraph("<b>Client:</b>", self.styles['InfoText']),
             Paragraph(self._clean_markdown(report.cover_page.client_name), self.styles['InfoText'])],
            [Paragraph("<b>Type d'audit:</b>", self.styles['InfoText']),
             Paragraph(self._clean_markdown(report.cover_page.audit_type), self.styles['InfoText'])],
            [Paragraph("<b>Date:</b>", self.styles['InfoText']),
             Paragraph(report.cover_page.audit_date.strftime('%d/%m/%Y'), self.styles['InfoText'])],
            [Paragraph("<b>Auditeur:</b>", self.styles['InfoText']),
             Paragraph(self._clean_markdown(report.cover_page.auditor), self.styles['InfoText'])],
            [Paragraph("<b>Version:</b>", self.styles['InfoText']),
             Paragraph(report.cover_page.report_version, self.styles['InfoText'])]
        ]

        info_table = Table(info_data, colWidths=[5*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 4*cm))

        # Date de génération
        generation_text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
        elements.append(Paragraph(
            f"<i>{generation_text}</i>",
            self.styles['Normal']
        ))

        return elements

    def _build_executive_summary(self, report: FullReport) -> list:
        """Construit le résumé exécutif."""
        elements = []

        # Titre de section
        elements.append(Paragraph("Résumé Exécutif", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Overview - diviser en paragraphes
        overview_paragraphs = self._split_into_paragraphs(report.executive_summary.overview)
        for para in overview_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        elements.append(Spacer(1, 0.5*cm))

        # Niveau de risque global
        risk_level = report.executive_summary.global_risk_level.value
        risk_color = self._get_severity_color(risk_level)
        elements.append(Paragraph(
            f"<b>Niveau de risque global:</b> <font color='{risk_color}'><b>{risk_level}</b></font>",
            self.styles['InfoText']
        ))

        elements.append(Spacer(1, 0.5*cm))

        # Tableau des statistiques amélioré
        data = [
            [Paragraph('<b>Sévérité</b>', self.styles['Normal']),
             Paragraph('<b>Nombre</b>', self.styles['Normal'])],
            [Paragraph('Critical', self.styles['Normal']),
             Paragraph(str(report.executive_summary.critical_count), self.styles['Normal'])],
            [Paragraph('High', self.styles['Normal']),
             Paragraph(str(report.executive_summary.high_count), self.styles['Normal'])],
            [Paragraph('Medium', self.styles['Normal']),
             Paragraph(str(report.executive_summary.medium_count), self.styles['Normal'])],
            [Paragraph('Low', self.styles['Normal']),
             Paragraph(str(report.executive_summary.low_count), self.styles['Normal'])]
        ]

        table = Table(data, colWidths=[10*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.7*cm))

        # Recommandations prioritaires
        elements.append(Paragraph("<b>Recommandations prioritaires:</b>", self.styles['SubSectionTitle']))
        for i, rec in enumerate(report.executive_summary.top_recommendations, 1):
            clean_rec = self._clean_markdown(rec)
            elements.append(Paragraph(f"{i}. {clean_rec}", self.styles['BulletText']))

        elements.append(Spacer(1, 0.5*cm))

        # Timeline
        elements.append(Paragraph("<b>Timeline de remédiation:</b>", self.styles['SubSectionTitle']))
        timeline_paragraphs = self._split_into_paragraphs(report.executive_summary.remediation_timeline)
        for para in timeline_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        return elements

    def _build_context_scope(self, report: FullReport) -> list:
        """Construit le contexte et périmètre."""
        elements = []

        elements.append(Paragraph("Contexte & Périmètre", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Description de l'environnement
        env_paragraphs = self._split_into_paragraphs(report.context_scope.environment_description)
        for para in env_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        elements.append(Spacer(1, 0.3*cm))

        # Périmètres
        tech_scope = self._clean_markdown(report.context_scope.technical_scope)
        elements.append(Paragraph(f"<b>Périmètre technique:</b> {tech_scope}", self.styles['InfoText']))

        temp_scope = self._clean_markdown(report.context_scope.temporal_scope)
        elements.append(Paragraph(f"<b>Périmètre temporel:</b> {temp_scope}", self.styles['InfoText']))

        return elements

    def _build_methodology(self, report: FullReport) -> list:
        """Construit la méthodologie."""
        elements = []

        elements.append(Paragraph("Méthodologie", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Type et standards
        audit_type = self._clean_markdown(report.methodology.audit_type)
        elements.append(Paragraph(f"<b>Type d'audit:</b> {audit_type}", self.styles['InfoText']))

        standards = ', '.join(report.methodology.standards)
        elements.append(Paragraph(f"<b>Standards utilisés:</b> {standards}", self.styles['InfoText']))

        elements.append(Spacer(1, 0.3*cm))

        # Approche
        approach_paragraphs = self._split_into_paragraphs(report.methodology.approach)
        for para in approach_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        return elements

    def _build_global_analysis(self, report: FullReport) -> list:
        """Construit l'analyse globale."""
        elements = []

        elements.append(Paragraph("Analyse Globale", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Score de sécurité
        score = report.global_analysis.security_score
        elements.append(Paragraph(
            f"<b>Score de sécurité:</b> <font color='{'green' if score >= 70 else 'orange' if score >= 40 else 'red'}'><b>{score}/100</b></font>",
            self.styles['InfoText']
        ))

        elements.append(Spacer(1, 0.3*cm))

        # Description du score
        score_paragraphs = self._split_into_paragraphs(report.global_analysis.score_description)
        for para in score_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        elements.append(Spacer(1, 0.5*cm))

        # Distribution par sévérité
        elements.append(Paragraph("<b>Distribution par sévérité:</b>", self.styles['SubSectionTitle']))
        for severity, count in report.global_analysis.severity_distribution.items():
            elements.append(Paragraph(f"• <b>{severity}:</b> {count}", self.styles['BulletText']))

        return elements

    def _build_findings(self, report: FullReport) -> list:
        """Construit les findings détaillés."""
        elements = []

        elements.append(Paragraph("Findings Détaillés", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        for i, finding in enumerate(report.findings, 1):
            # Créer un bloc pour chaque finding
            finding_elements = []

            # Titre du finding
            title = self._clean_markdown(finding.title)
            finding_elements.append(Paragraph(
                f"<b>Finding #{i}: {title}</b>",
                self.styles['SubSectionTitle']
            ))

            # Métadonnées
            category = self._clean_markdown(finding.category.value)
            finding_elements.append(Paragraph(f"<b>Catégorie:</b> {category}", self.styles['InfoText']))

            severity = finding.severity.value
            severity_color = self._get_severity_color(severity)
            finding_elements.append(Paragraph(
                f"<b>Sévérité:</b> <font color='{severity_color}'><b>{severity}</b></font>",
                self.styles['InfoText']
            ))

            priority = finding.priority.value
            finding_elements.append(Paragraph(f"<b>Priorité:</b> {priority}", self.styles['InfoText']))

            finding_elements.append(Spacer(1, 0.3*cm))

            # Description
            finding_elements.append(Paragraph("<b>Description:</b>", self.styles['InfoText']))
            desc_paragraphs = self._split_into_paragraphs(finding.enriched_description)
            for para in desc_paragraphs:
                clean_text = self._clean_markdown(para)
                finding_elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

            # Impact métier
            finding_elements.append(Spacer(1, 0.2*cm))
            finding_elements.append(Paragraph("<b>Impact métier:</b>", self.styles['InfoText']))
            impact_paragraphs = self._split_into_paragraphs(finding.business_impact)
            for para in impact_paragraphs:
                clean_text = self._clean_markdown(para)
                finding_elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

            # Recommandation
            finding_elements.append(Spacer(1, 0.2*cm))
            finding_elements.append(Paragraph("<b>Recommandation:</b>", self.styles['InfoText']))
            rec_paragraphs = self._split_into_paragraphs(finding.enriched_recommendation)
            for para in rec_paragraphs:
                clean_text = self._clean_markdown(para)
                finding_elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

            # Garder ensemble si possible
            elements.append(KeepTogether(finding_elements))

            if i < len(report.findings):
                elements.append(Spacer(1, 1*cm))

        return elements

    def _build_action_plan(self, report: FullReport) -> list:
        """Construit le plan d'action avec tableau amélioré."""
        elements = []

        elements.append(Paragraph("Plan d'Action Priorisé", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Introduction
        intro_paragraphs = self._split_into_paragraphs(report.action_plan.introduction)
        for para in intro_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        elements.append(Spacer(1, 0.5*cm))

        # Tableau des actions avec word wrapping
        data = [[
            Paragraph('<b>#</b>', self.styles['Normal']),
            Paragraph('<b>Mesure</b>', self.styles['Normal']),
            Paragraph('<b>Priorité</b>', self.styles['Normal']),
            Paragraph('<b>Responsable</b>', self.styles['Normal']),
            Paragraph('<b>Délai</b>', self.styles['Normal'])
        ]]

        for i, action in enumerate(report.action_plan.actions, 1):
            # Nettoyer le texte Markdown
            measure = self._clean_markdown(action.measure)
            responsible = self._clean_markdown(action.responsible)

            data.append([
                Paragraph(str(i), self.styles['Normal']),
                Paragraph(measure, self.styles['Normal']),
                Paragraph(action.priority.value, self.styles['Normal']),
                Paragraph(responsible, self.styles['Normal']),
                Paragraph(action.deadline, self.styles['Normal'])
            ])

        # Tableau avec meilleure répartition des colonnes
        table = Table(data, colWidths=[1*cm, 8*cm, 2*cm, 2.5*cm, 2*cm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Colonne #
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),     # Colonne Mesure
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),  # Autres colonnes
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)

        return elements

    def _build_conclusion(self, report: FullReport) -> list:
        """Construit la conclusion."""
        elements = []

        elements.append(Paragraph("Conclusion", self.styles['SectionTitle']))
        elements.append(Spacer(1, 0.5*cm))

        # Résumé
        summary_paragraphs = self._split_into_paragraphs(report.conclusion.summary)
        for para in summary_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        elements.append(Spacer(1, 0.5*cm))

        # Points positifs
        elements.append(Paragraph("<b>Points positifs:</b>", self.styles['SubSectionTitle']))
        for point in report.conclusion.positive_points:
            clean_point = self._clean_markdown(point)
            elements.append(Paragraph(f"• {clean_point}", self.styles['BulletText']))

        elements.append(Spacer(1, 0.5*cm))

        # Axes d'amélioration
        elements.append(Paragraph("<b>Axes d'amélioration:</b>", self.styles['SubSectionTitle']))
        for area in report.conclusion.improvement_areas:
            clean_area = self._clean_markdown(area)
            elements.append(Paragraph(f"• {clean_area}", self.styles['BulletText']))

        elements.append(Spacer(1, 0.5*cm))

        # Recommandations stratégiques
        elements.append(Paragraph("<b>Recommandations stratégiques:</b>", self.styles['SubSectionTitle']))
        for rec in report.conclusion.strategic_recommendations:
            clean_rec = self._clean_markdown(rec)
            elements.append(Paragraph(f"• {clean_rec}", self.styles['BulletText']))

        elements.append(Spacer(1, 0.5*cm))

        # Prochaines étapes
        next_steps_paragraphs = self._split_into_paragraphs(report.conclusion.next_steps)
        for para in next_steps_paragraphs:
            clean_text = self._clean_markdown(para)
            elements.append(Paragraph(clean_text, self.styles['ReportBodyText']))

        return elements

    def _get_severity_color(self, severity: str) -> str:
        """Retourne la couleur selon la sévérité."""
        colors_map = {
            'Critical': 'red',
            'High': 'orange',
            'Medium': '#FFA500',
            'Low': 'green'
        }
        return colors_map.get(severity, 'black')

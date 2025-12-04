# -*- coding: utf-8 -*-
"""
Interface web Streamlit pour le générateur de rapports d'audit.

Permet de sélectionner un audit depuis la base de données, modifier les informations
et générer des rapports PDF/DOCX enrichis par IA via LangGraph.
"""

import streamlit as st
import sys
from datetime import date
from pathlib import Path

if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from db.audit_service import AuditService
from models.audit_models import SeverityLevel, CategoryType, PriorityLevel
from agents.workflow import ReportGenerationWorkflow
from report.pdf_generator import PDFReportGenerator
from report.docx_generator import DOCXReportGenerator
from config.settings import settings

st.set_page_config(
    page_title="Nexoryx - Générateur de Rapports",
    page_icon="🔒",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #1f4788;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables d'état de la session Streamlit."""
    if 'selected_audit_id' not in st.session_state:
        st.session_state.selected_audit_id = None
    if 'audit_data' not in st.session_state:
        st.session_state.audit_data = None


def main():
    """Point d'entrée principal de l'interface Streamlit."""
    init_session_state()

    st.markdown('<div class="main-header">🔒 Générateur de Rapports d\'Audit</div>', unsafe_allow_html=True)

    # ÉTAPE 1: Sélection de l'audit
    st.markdown("## 📋 Étape 1: Sélectionner un Audit")

    audits = AuditService.get_all_audits()

    if not audits:
        st.error("❌ Aucun audit trouvé dans la base de données")
        return

    # Créer les options pour le selectbox
    audit_options = {
        f"#{audit['id']} - {audit['client_name']} ({audit['audit_type']}) - {audit['audit_date']}": audit['id']
        for audit in audits
    }

    selected_label = st.selectbox(
        "Choisissez un audit",
        options=list(audit_options.keys()),
        key="audit_selector"
    )

    audit_id = audit_options[selected_label]

    # Charger l'audit si changé
    if st.session_state.selected_audit_id != audit_id:
        st.session_state.selected_audit_id = audit_id
        st.session_state.audit_data = AuditService.get_audit_by_id(audit_id)
        st.rerun()

    if not st.session_state.audit_data:
        st.error("❌ Impossible de charger l'audit")
        return

    audit = st.session_state.audit_data

    st.success(f"✅ Audit chargé: {audit.client_name} - {len(audit.findings)} vulnérabilités")

    st.markdown("---")

    # ÉTAPE 2: Afficher et modifier les informations
    st.markdown("## ✏️ Étape 2: Informations de l'Audit")

    with st.form("audit_form"):
        col1, col2 = st.columns(2)

        with col1:
            client_name = st.text_input("Nom du client", value=audit.client_name)
            audit_type = st.text_input("Type d'audit", value=audit.audit_type)
            auditor = st.text_input("Auditeur", value=audit.auditor)

        with col2:
            audit_date_input = st.date_input("Date de l'audit", value=audit.audit_date)
            scope = st.text_area("Périmètre", value=audit.scope, height=100)

        st.markdown("### 🔍 Vulnérabilités")

        st.write(f"**{len(audit.findings)} vulnérabilités détectées:**")

        # Afficher les vulnérabilités par sévérité
        critical = [f for f in audit.findings if f.severity == SeverityLevel.CRITICAL]
        high = [f for f in audit.findings if f.severity == SeverityLevel.HIGH]
        medium = [f for f in audit.findings if f.severity == SeverityLevel.MEDIUM]
        low = [f for f in audit.findings if f.severity == SeverityLevel.LOW]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 Critiques", len(critical))
        with col2:
            st.metric("🟠 Élevées", len(high))
        with col3:
            st.metric("🟡 Moyennes", len(medium))
        with col4:
            st.metric("🟢 Faibles", len(low))

        # Afficher la liste des vulnérabilités
        with st.expander(f"📄 Détails des {len(audit.findings)} vulnérabilités"):
            for idx, finding in enumerate(audit.findings, 1):
                severity_icon = {
                    SeverityLevel.CRITICAL: "🔴",
                    SeverityLevel.HIGH: "🟠",
                    SeverityLevel.MEDIUM: "🟡",
                    SeverityLevel.LOW: "🟢"
                }.get(finding.severity, "⚪")

                st.markdown(f"""
**{idx}. {severity_icon} {finding.title}**
- **Catégorie:** {finding.category.value}
- **Sévérité:** {finding.severity.value}
- **Description:** {finding.description[:200]}...
                """)
                st.markdown("---")

        st.markdown("---")

        # Boutons de génération
        st.markdown("## 📥 Étape 3: Générer le Rapport")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            generate_pdf = st.form_submit_button("📄 Générer PDF", use_container_width=True)

        with col2:
            generate_docx = st.form_submit_button("📝 Générer DOCX", use_container_width=True)

        with col3:
            generate_both = st.form_submit_button("📚 Générer PDF + DOCX", use_container_width=True)

    # Génération des rapports
    if generate_pdf or generate_docx or generate_both:
        # Mettre à jour les données de l'audit avec les modifications
        audit.client_name = client_name
        audit.audit_type = audit_type
        audit.auditor = auditor
        audit.audit_date = audit_date_input
        audit.scope = scope

        with st.spinner("🔄 Génération du rapport en cours (cela peut prendre quelques minutes)..."):
            try:
                # Créer le répertoire de sortie
                output_dir = Path(settings.reports_output_dir)
                output_dir.mkdir(exist_ok=True)

                # Générer le rapport avec le workflow LangGraph
                workflow = ReportGenerationWorkflow()
                full_report = workflow.generate_report(audit)

                st.success("✅ Rapport généré avec succès par l'IA!")

                # Créer le nom de fichier
                timestamp = date.today().strftime("%Y%m%d")
                base_filename = f"rapport_{client_name.replace(' ', '_')}_{timestamp}"

                # Générer les fichiers selon le choix
                pdf_path = None
                docx_path = None

                if generate_pdf or generate_both:
                    pdf_gen = PDFReportGenerator()
                    pdf_path = pdf_gen.generate(full_report, f"{base_filename}.pdf")
                    st.success(f"📄 PDF généré: {Path(pdf_path).name}")

                if generate_docx or generate_both:
                    docx_gen = DOCXReportGenerator()
                    docx_path = docx_gen.generate(full_report, f"{base_filename}.docx")
                    st.success(f"📝 DOCX généré: {Path(docx_path).name}")

                st.markdown("---")
                st.markdown("### 📥 Téléchargement")

                col1, col2 = st.columns(2)

                # Boutons de téléchargement
                if pdf_path and Path(pdf_path).exists():
                    with col1:
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📄 Télécharger PDF",
                                data=f,
                                file_name=Path(pdf_path).name,
                                mime="application/pdf",
                                use_container_width=True
                            )

                if docx_path and Path(docx_path).exists():
                    with col2:
                        with open(docx_path, "rb") as f:
                            st.download_button(
                                label="📝 Télécharger DOCX",
                                data=f,
                                file_name=Path(docx_path).name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
                import traceback
                with st.expander("📋 Détails de l'erreur"):
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

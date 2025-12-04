# -*- coding: utf-8 -*-
"""
Point d'entrée principal du système de génération de rapports d'audit.

Usage:
    python main.py --audit-id 1 --format pdf
    python main.py --audit-id 1 --format docx
    python main.py --audit-id 1 --format both
    python main.py --list-audits
"""

import argparse
import sys
from typing import Optional

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from db.audit_service import AuditService
from agents.workflow import ReportGenerationWorkflow
from report.pdf_generator import PDFReportGenerator
from report.docx_generator import DOCXReportGenerator
from config.settings import settings


def list_audits():
    """Liste tous les audits disponibles dans la base de données."""
    print("\n=== Audits disponibles ===\n")

    audits = AuditService.get_all_audits()

    if not audits:
        print("Aucun audit trouvé dans la base de données.")
        print("Exécutez 'python db/init_db.py' pour initialiser la base de données.")
        return

    for audit in audits:
        print(f"ID: {audit['id']}")
        print(f"  Client: {audit['client_name']}")
        print(f"  Type: {audit['audit_type']}")
        print(f"  Date: {audit['audit_date']}")
        print()

    print(f"Total: {len(audits)} audit(s)\n")


def generate_report(audit_id: int, output_format: str) -> bool:
    """
    Génère un rapport enrichi par IA pour un audit donné.

    Args:
        audit_id: ID de l'audit
        output_format: Format de sortie ('pdf', 'docx', 'both')

    Returns:
        True si succès, False sinon
    """
    print(f"\n=== Génération du rapport pour l'audit #{audit_id} ===\n")

    print("1. Extraction des données de l'audit...")
    audit_data = AuditService.get_audit_by_id(audit_id)

    if audit_data is None:
        print(f"Erreur: Audit #{audit_id} introuvable.")
        return False

    print(f"Audit trouvé: {audit_data.client_name} - {audit_data.audit_type}")
    print(f"   Nombre de findings: {audit_data.total_findings}")
    print()

    print("2. Génération du rapport avec IA (cela peut prendre quelques minutes)...")
    try:
        workflow = ReportGenerationWorkflow()
        full_report = workflow.generate_report(audit_data)
        print("Rapport généré avec succès!")
        print()
    except Exception as e:
        print(f"Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("3. Création du fichier de rapport...")

    generated_files = []

    try:
        if output_format in ['pdf', 'both']:
            pdf_gen = PDFReportGenerator()
            pdf_path = pdf_gen.generate(full_report)
            generated_files.append(pdf_path)
            print(f"  PDF généré: {pdf_path}")

        if output_format in ['docx', 'both']:
            docx_gen = DOCXReportGenerator()
            docx_path = docx_gen.generate(full_report)
            generated_files.append(docx_path)
            print(f"  DOCX généré: {docx_path}")

    except Exception as e:
        print(f"Erreur lors de la création du fichier: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("=" * 60)
    print("✓ Génération terminée avec succès!")
    print()
    print("Fichiers générés:")
    for file_path in generated_files:
        print(f"  • {file_path}")
    print("=" * 60)
    print()

    return True


def main():
    """Point d'entrée principal de l'application CLI."""
    parser = argparse.ArgumentParser(
        description="Générateur automatisé de rapports d'audit de cybersécurité",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --list-audits
  %(prog)s --audit-id 1 --format pdf
  %(prog)s --audit-id 1 --format docx
  %(prog)s --audit-id 1 --format both

Configuration:
  Créez un fichier .env à la racine avec vos clés API:
    OPENAI_API_KEY=sk-...
    (ou ANTHROPIC_API_KEY=sk-ant-...)
        """
    )

    parser.add_argument(
        '--list-audits',
        action='store_true',
        help='Liste tous les audits disponibles'
    )

    parser.add_argument(
        '--audit-id',
        type=int,
        help='ID de l\'audit pour lequel générer un rapport'
    )

    parser.add_argument(
        '--format',
        choices=['pdf', 'docx', 'both'],
        default='pdf',
        help='Format de sortie du rapport (défaut: pdf)'
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  NEXORYX - Générateur Automatisé de Rapports d'Audit")
    print("  Powered by IA & LangGraph")
    print("=" * 60)

    if args.list_audits:
        list_audits()
        return 0

    if args.audit_id:
        if not settings.openai_api_key and not settings.anthropic_api_key:
            print("\nErreur: Aucune clé API configurée!")
            print("   Créez un fichier .env avec OPENAI_API_KEY ou ANTHROPIC_API_KEY")
            print("   Voir .env.example pour un modèle")
            return 1

        success = generate_report(args.audit_id, args.format)
        return 0 if success else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

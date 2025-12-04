"""
Service d'accès aux données d'audit.
"""

from datetime import date
from typing import List, Optional
from models.audit_models import AuditData, AuditFinding, SeverityLevel, CategoryType
from db.database import get_connection


class AuditService:
    """Service  pour accéder aux données d'audit."""

    @staticmethod
    def get_audit_by_id(audit_id: int) -> Optional[AuditData]:
        """
        Récupère un audit complet par son ID.

        Args:
            audit_id: ID de l'audit

        Returns:
            AuditData complet ou None si non trouvé
        """
        conn = get_connection()
        cur = conn.cursor()

        # Récupérer les informations de l'audit
        cur.execute("""
            SELECT id, client_name, audit_type, audit_date, auditor, scope
            FROM audits WHERE id=?
        """, (audit_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return None

        # Récupérer les findings
        cur.execute("""
            SELECT id, title, description, severity, evidence, recommendation, category
            FROM audit_findings WHERE audit_id=?
        """, (audit_id,))
        finding_rows = cur.fetchall()

        findings = [
            AuditFinding(
                id=f[0],
                title=f[1],
                description=f[2],
                severity=SeverityLevel(f[3]),
                evidence=f[4],
                recommendation=f[5],
                category=CategoryType(f[6])
            )
            for f in finding_rows
        ]

        # Récupérer les métadonnées
        cur.execute("""
            SELECT key, value FROM audit_metadata WHERE audit_id=?
        """, (audit_id,))
        metadata_rows = cur.fetchall()

        metadata = {key: value for key, value in metadata_rows}

        conn.close()

        # Créer l'objet AuditData
        return AuditData(
            id=row[0],
            client_name=row[1],
            audit_type=row[2],
            audit_date=date.fromisoformat(row[3]),
            auditor=row[4],
            scope=row[5] or "",
            findings=findings,
            metadata=metadata
        )

    @staticmethod
    def get_all_audits() -> List[dict]:
        """
        Récupère la liste de tous les audits (informations de base).

        Returns:
            Liste de dictionnaires avec id, client_name, audit_type, audit_date
        """
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, client_name, audit_type, audit_date FROM audits")
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "client_name": row[1],
                "audit_type": row[2],
                "audit_date": row[3]
            }
            for row in rows
        ]

    @staticmethod
    def get_audits_count() -> int:
        """
        Retourne le nombre total d'audits.

        Returns:
            Nombre d'audits
        """
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM audits")
        count = cur.fetchone()[0]
        conn.close()
        return count

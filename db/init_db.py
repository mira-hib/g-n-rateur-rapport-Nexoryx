import sqlite3
import random

DB_PATH = "db/audit_system.db"

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        audit_type TEXT NOT NULL,
        audit_date TEXT NOT NULL,
        auditor TEXT NOT NULL,
        scope TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_findings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        severity TEXT,
        evidence TEXT,
        recommendation TEXT,
        category TEXT,
        FOREIGN KEY (audit_id) REFERENCES audits(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        FOREIGN KEY (audit_id) REFERENCES audits(id)
    );
    """)

    conn.commit()
    conn.close()
    print("[OK] Tables created successfully.")


def seed_data():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM audits")
    if cur.fetchone()[0] > 0:
        print("[INFO] Data already exists - skipping insertion.")
        return

    print("[INFO] Inserting sample data...")

    audits = [
        ("Nexoryx Bank", "Pentest Réseau", "2025-01-12", "Ibrahim Bamba", "Réseau interne + VPN"),
        ("Agora Telecom", "Audit ISO27001", "2025-01-20", "Marie K.", "SI global + RH + Finance"),
        ("OrangeDev", "Pentest Application Web", "2025-02-01", "Charles A.", "Portail web + API"),
        ("CloudPlus", "Audit Cloud Security AWS", "2025-02-10", "Moussa T.", "Comptes IAM + S3 + EC2"),
        ("PayXpert", "Audit SOC2 Type II", "2025-02-22", "Jean-Luc R.", "Processus + Logs + Access"),
        ("CIV Bank", "Forensic Investigation", "2025-03-03", "Awa S.", "Serveur compromis + réseau")
    ]

    cur.executemany("""
    INSERT INTO audits (client_name, audit_type, audit_date, auditor, scope)
    VALUES (?, ?, ?, ?, ?)
    """, audits)

    # ---------------------------------
    # 🔥 FINDINGS FICTIFS PAR CATÉGORIE
    # ---------------------------------

    findings_pool = {
        "Network": [
            ("Port non sécurisé ouvert", "Plusieurs ports inutilisés sont exposés.", "High"),
            ("Absence de segmentation", "Le réseau plat expose toute l'infra.", "Critical"),
            ("Firewall obsolète", "Version non supportée selon l’éditeur.", "High")
        ],
        "AppSec": [
            ("Injection SQL", "Paramètre vulnérable à une extraction de données.", "Critical"),
            ("XSS Refletée", "Input non filtrée renvoyée au client.", "Medium"),
            ("Session non sécurisée", "Cookies sans flags HttpOnly/Secure.", "High")
        ],
        "IAM": [
            ("MFA absent", "Aucun double facteur activé.", "High"),
            ("Comptes dormants", "Plus de 50 comptes inactifs non désactivés.", "Medium"),
            ("Mot de passe faible", "Politique faible, pas de rotation.", "Critical")
        ],
        "Cloud": [
            ("Bucket S3 public", "Données sensibles accessibles publiquement.", "Critical"),
            ("IAM Policy trop permissive", "Usage de '*' dans policies.", "High"),
            ("Instance non patchée", "EC2 vulnérable (CVE-xxx).", "Medium")
        ],
        "Governance": [
            ("Politique de sécurité non mise à jour", "Dernière version 2019.", "Low"),
            ("Logs non centralisés", "Absence de SIEM.", "Medium"),
            ("Incident response non testé", "Aucun test IR depuis 3 ans.", "High")
        ],
        "Forensic": [
            ("Malware détecté", "Backdoor persistante trouvée.", "Critical"),
            ("Trace d’exfiltration", "Transferts massifs vers IP inconnue.", "High"),
            ("Compte compromis", "Credentials exposés.", "High")
        ]
    }

    def create_finding_row(audit_id, title, desc, severity, category):
        return (
            audit_id,
            title,
            desc,
            severity,
            f"Évidence : capture outils / logs. ID preuve: {random.randint(1000,9999)}",
            f"Recommandation générale pour {title.lower()}",
            category
        )

    # Génération de findings pour chaque audit
    cur.execute("SELECT id, audit_type FROM audits")
    audits_rows = cur.fetchall()

    for audit_id, audit_type in audits_rows:
        selected_categories = []

        if "Réseau" in audit_type:
            selected_categories = ["Network", "IAM"]
        elif "ISO" in audit_type:
            selected_categories = ["Governance", "IAM"]
        elif "Application" in audit_type:
            selected_categories = ["AppSec"]
        elif "Cloud" in audit_type:
            selected_categories = ["Cloud", "IAM"]
        elif "SOC2" in audit_type:
            selected_categories = ["Governance", "IAM", "Network"]
        elif "Forensic" in audit_type:
            selected_categories = ["Forensic"]

        # ajouter 5–12 findings aléatoires
        for cat in selected_categories:
            for f in findings_pool[cat]:
                title, desc, sev = f
                row = create_finding_row(audit_id, title, desc, sev, cat)
                cur.execute("""
                INSERT INTO audit_findings
                (audit_id, title, description, severity, evidence, recommendation, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, row)

    # --------------------------
    # 🔥 METADATA FICTIVE
    # --------------------------
    metadata_samples = [
        ("sector", ["Finance", "Tech", "Cloud", "Telecom", "Banking"]),
        ("company_size", ["SME", "Large", "Startup", "Corporate"]),
        ("global_risk", ["Low", "Medium", "High", "Critical"]),
    ]

    for audit_id, _ in audits_rows:
        for key, values in metadata_samples:
            cur.execute("""
            INSERT INTO audit_metadata (audit_id, key, value)
            VALUES (?, ?, ?)
            """, (audit_id, key, random.choice(values)))

    conn.commit()
    conn.close()

    print("[SUCCESS] Data enriched: ~50 findings, ~20 metadata, 6 audits.")
    

if __name__ == "__main__":
    create_tables()
    seed_data()

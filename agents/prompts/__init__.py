from .generation_prompts import GenerationPrompts
from .validation_prompts import ValidationPrompts


class AuditPrompts:
    @staticmethod
    def prompt_resume_executif(audit_data, top_findings_text):
        return GenerationPrompts.resume_executif(audit_data, top_findings_text)

    @staticmethod
    def prompt_enrichissement_vulnerabilite(audit_data, finding):
        return GenerationPrompts.enrichissement_vulnerabilite(audit_data, finding)

    @staticmethod
    def prompt_plan_action(audit_data, findings_text):
        return GenerationPrompts.plan_action(audit_data, findings_text)

    @staticmethod
    def prompt_conclusion(audit_data, findings):
        return GenerationPrompts.conclusion(audit_data, findings)

    @staticmethod
    def prompt_validate_resume(summary, total_findings):
        return ValidationPrompts.validate_resume(summary, total_findings)

    @staticmethod
    def prompt_validate_finding(finding, context):
        return ValidationPrompts.validate_finding(finding, context)

    @staticmethod
    def prompt_validate_plan_action(action_plan, findings_count, format_actions):
        return ValidationPrompts.validate_plan_action(action_plan, findings_count, format_actions)

    @staticmethod
    def prompt_validate_conclusion(conclusion, context):
        return ValidationPrompts.validate_conclusion(conclusion, context)

    @staticmethod
    def prompt_validate_full_report(sections, format_sections):
        return ValidationPrompts.validate_full_report(sections, format_sections)


__all__ = ["AuditPrompts", "GenerationPrompts", "ValidationPrompts"]

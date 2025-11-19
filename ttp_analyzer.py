"""TTP analysis using Claude API with adaptive extraction."""
import json
import os
from typing import Dict, Any
from anthropic import Anthropic


class TTPAnalyzer:
    """Analyzes security content and extracts TTPs using Claude API."""

    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def analyze(self, content: str, source_url: str) -> Dict[str, Any]:
        """
        Analyze content and extract TTPs.

        Two-stage process:
        1. Classify content type
        2. Extract intelligence based on type
        """
        # Stage 1: Classify content
        content_type = self._classify_content(content)

        if not content_type['has_actionable_intel']:
            return {
                'source_url': source_url,
                'content_type': 'not_actionable',
                'summary': content_type['summary'],
                'data': None
            }

        # Stage 2: Extract based on type
        extracted_data = self._extract_by_type(content, content_type['content_type'], source_url)

        return {
            'source_url': source_url,
            'content_type': content_type['content_type'],
            'data': extracted_data
        }

    def _classify_content(self, content: str) -> Dict[str, Any]:
        """Determine what type of security intelligence this content contains."""
        prompt = f"""Analyze this security content and determine what type of intelligence it contains.

Return ONLY valid JSON with this exact structure:

{{
  "content_type": "ioc_based" | "technique_research" | "tool_analysis" | "threat_actor_profile" | "vulnerability_analysis" | "detection_engineering" | "general_news",
  "has_actionable_intel": true | false,
  "summary": "one line summary of what this is about"
}}

Content:
{content[:3000]}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            # Extract JSON from response (in case there's extra text)
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0]

            return json.loads(result_text)
        except Exception as e:
            print(f"Error classifying content: {e}")
            return {
                "content_type": "general_news",
                "has_actionable_intel": False,
                "summary": "Classification failed"
            }

    def _extract_by_type(self, content: str, content_type: str, source_url: str) -> Dict[str, Any]:
        """Extract intelligence based on content type."""
        prompts = {
            "ioc_based": self._get_ioc_prompt(),
            "technique_research": self._get_technique_prompt(),
            "tool_analysis": self._get_tool_prompt(),
            "threat_actor_profile": self._get_actor_prompt(),
            "vulnerability_analysis": self._get_vuln_prompt(),
            "detection_engineering": self._get_detection_prompt()
        }

        prompt = prompts.get(content_type, self._get_generic_prompt())
        full_prompt = f"{prompt}\n\nSource: {source_url}\n\nContent:\n{content[:8000]}"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": full_prompt}]
            )

            result_text = response.content[0].text
            # Extract JSON from response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0]

            return json.loads(result_text)
        except Exception as e:
            print(f"Error extracting {content_type}: {e}")
            return {"error": str(e)}

    def _get_ioc_prompt(self) -> str:
        """Prompt for IOC-based threat intelligence."""
        return """Extract technical threat intelligence. You're analyzing for a security analyst - skip basics, give actionable details.

Return ONLY valid JSON:
{
  "threat_name": "name",
  "iocs": {
    "ips": [],
    "domains": [],
    "urls": [],
    "hashes": {"sha256": [], "md5": [], "sha1": []},
    "file_names": [],
    "registry_keys": [],
    "mutex": [],
    "user_agents": [],
    "email_subjects": []
  },
  "infrastructure": {
    "hosting_provider": "",
    "asn": "",
    "registrar": "",
    "ssl_certs": []
  },
  "technical_details": {
    "execution_flow": "actual command line / process tree",
    "obfuscation": "how it's packed/obfuscated",
    "persistence_mechanism": "exact registry key or scheduled task",
    "c2_protocol": "HTTP/HTTPS/DNS/custom",
    "encryption": "what encryption used",
    "sandbox_evasion": "anti-analysis tricks"
  },
  "detection_queries": [
    "KQL queries for MDO/Defender/Sentinel",
    "specific EDR detection logic"
  ],
  "sample_info": {
    "sample_links": ["any.run/virustotal/hybrid-analysis links"],
    "yara_rules": "YARA rule if provided"
  },
  "key_findings": "the actual sauce - what's new/interesting about this threat"
}"""

    def _get_technique_prompt(self) -> str:
        """Prompt for technique/research analysis."""
        return """Extract details about this attack technique or research. Focus on what matters for detection.

Return ONLY valid JSON:
{
  "technique_name": "",
  "attack_vector": "how it works technically",
  "prerequisites": "what attacker needs",
  "detection_gap": "why current tools miss it",
  "detection_ideas": [
    "specific ways to detect this",
    "telemetry sources to monitor",
    "behavioral indicators"
  ],
  "affected_products": ["EDR/product names that are blind to this"],
  "mitigation": "how to prevent or reduce risk",
  "poc_available": true | false,
  "key_takeaway": "why this matters for your environment - what to do about it"
}"""

    def _get_tool_prompt(self) -> str:
        """Prompt for tool analysis."""
        return """Analyze this security tool from a detection perspective.

Return ONLY valid JSON:
{
  "tool_name": "",
  "tool_purpose": "what it does",
  "capabilities": ["list of key features"],
  "detection_methods": [
    "how to detect usage in your environment",
    "specific IOCs or behaviors"
  ],
  "legitimate_use_cases": ["when it's benign"],
  "malicious_use_cases": ["how attackers use it"],
  "telemetry_sources": ["where to look for it - EDR/network/email"],
  "key_takeaway": "should you monitor for this? how?"
}"""

    def _get_actor_prompt(self) -> str:
        """Prompt for threat actor analysis."""
        return """Extract threat actor intelligence.

Return ONLY valid JSON:
{
  "actor_name": "",
  "aliases": [],
  "targeting": {
    "industries": [],
    "geos": [],
    "motivation": "financial/espionage/destructive"
  },
  "ttp_changes": "what's new in their playbook",
  "infrastructure_patterns": "their infrastructure style/preferences",
  "recent_activity": "latest campaigns or changes",
  "watch_for": "specific things to monitor in your environment if you match their targeting"
}"""

    def _get_vuln_prompt(self) -> str:
        """Prompt for vulnerability analysis."""
        return """Extract vulnerability details.

Return ONLY valid JSON:
{
  "cve_id": "",
  "affected_products": [],
  "severity": "critical/high/medium/low",
  "exploit_available": true | false,
  "exploit_complexity": "easy/medium/hard",
  "attack_vector": "how it's exploited",
  "detection_methods": ["how to detect exploitation attempts"],
  "mitigation": "patching info or workarounds",
  "observed_in_wild": true | false,
  "key_takeaway": "do you need to act on this immediately?"
}"""

    def _get_detection_prompt(self) -> str:
        """Prompt for detection engineering content."""
        return """Extract detection engineering intelligence.

Return ONLY valid JSON:
{
  "detection_name": "",
  "what_it_detects": "specific threat or behavior",
  "data_sources": ["telemetry needed"],
  "detection_logic": "the actual query or rule",
  "false_positive_potential": "low/medium/high",
  "tuning_recommendations": "how to reduce FPs",
  "coverage": "what this does and doesn't catch",
  "key_takeaway": "should you implement this?"
}"""

    def _get_generic_prompt(self) -> str:
        """Fallback prompt for general content."""
        return """Summarize this security content from an analyst perspective.

Return ONLY valid JSON:
{
  "summary": "what this is about",
  "actionable_items": ["things you should do based on this"],
  "relevance": "why this matters or doesn't matter"
}"""


if __name__ == "__main__":
    # Test the analyzer
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ttp_analyzer.py <test_content>")
        sys.exit(1)

    # Load API key from .env if it exists
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    os.environ['ANTHROPIC_API_KEY'] = line.split('=', 1)[1].strip()

    analyzer = TTPAnalyzer()
    test_content = sys.argv[1]
    result = analyzer.analyze(test_content, "test://url")
    print(json.dumps(result, indent=2))

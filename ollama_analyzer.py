"""TTP analysis using Ollama (local LLM) with adaptive extraction."""
import json
import requests
from typing import Dict, Any


class OllamaTTPAnalyzer:
    """Analyzes security content and extracts TTPs using Ollama local LLM."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama analyzer.

        Args:
            model: Ollama model name (llama3.1, gemma2, mixtral, qwen2.5, etc.)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

        # Verify Ollama is running
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]

            if not any(self.model in name for name in model_names):
                print(f"Warning: Model {self.model} not found. Available models: {model_names}")
                print(f"Run: ollama pull {self.model}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama at {base_url}. Is it running? Error: {e}")

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

    def _call_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Ollama API and get response."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.1,  # Lower temperature for more consistent JSON
            }
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result['response']
        except Exception as e:
            raise Exception(f"Ollama API error: {e}")

    def _classify_content(self, content: str) -> Dict[str, Any]:
        """Determine what type of security intelligence this content contains."""
        prompt = f"""Analyze this security content and determine what type of intelligence it contains.

Return ONLY valid JSON with this exact structure (no markdown, no extra text):

{{
  "content_type": "ioc_based" | "technique_research" | "tool_analysis" | "threat_actor_profile" | "vulnerability_analysis" | "detection_engineering" | "general_news",
  "has_actionable_intel": true | false,
  "summary": "one line summary of what this is about"
}}

Content:
{content[:3000]}

JSON Response:"""

        try:
            result_text = self._call_ollama(prompt, max_tokens=500)

            # Extract JSON from response (in case there's extra text)
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0]

            # Find JSON object
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end > start:
                result_text = result_text[start:end]

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
        full_prompt = f"{prompt}\n\nSource: {source_url}\n\nContent:\n{content[:8000]}\n\nJSON Response:"

        try:
            result_text = self._call_ollama(full_prompt, max_tokens=3000)

            # Extract JSON from response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1].split('```')[0]

            # Find JSON object
            start = result_text.find('{')
            end = result_text.rfind('}') + 1
            if start != -1 and end > start:
                result_text = result_text[start:end]

            return json.loads(result_text)
        except Exception as e:
            print(f"Error extracting {content_type}: {e}")
            return {"error": str(e)}

    def _get_ioc_prompt(self) -> str:
        """Prompt for IOC-based threat intelligence."""
        return """Extract technical threat intelligence. You're analyzing for a security analyst - skip basics, give actionable details.

Return ONLY valid JSON (no markdown, no extra text):
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

Return ONLY valid JSON (no markdown, no extra text):
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
  "poc_available": true,
  "key_takeaway": "why this matters for your environment - what to do about it"
}"""

    def _get_tool_prompt(self) -> str:
        """Prompt for tool analysis."""
        return """Analyze this security tool from a detection perspective.

Return ONLY valid JSON (no markdown, no extra text):
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

Return ONLY valid JSON (no markdown, no extra text):
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

Return ONLY valid JSON (no markdown, no extra text):
{
  "cve_id": "",
  "affected_products": [],
  "severity": "critical/high/medium/low",
  "exploit_available": true,
  "exploit_complexity": "easy/medium/hard",
  "attack_vector": "how it's exploited",
  "detection_methods": ["how to detect exploitation attempts"],
  "mitigation": "patching info or workarounds",
  "observed_in_wild": true,
  "key_takeaway": "do you need to act on this immediately?"
}"""

    def _get_detection_prompt(self) -> str:
        """Prompt for detection engineering content."""
        return """Extract detection engineering intelligence.

Return ONLY valid JSON (no markdown, no extra text):
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

Return ONLY valid JSON (no markdown, no extra text):
{
  "summary": "what this is about",
  "actionable_items": ["things you should do based on this"],
  "relevance": "why this matters or doesn't matter"
}"""


if __name__ == "__main__":
    # Test the analyzer
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ollama_analyzer.py <test_content>")
        sys.exit(1)

    analyzer = OllamaTTPAnalyzer()
    test_content = sys.argv[1]
    result = analyzer.analyze(test_content, "test://url")
    print(json.dumps(result, indent=2))

"""
Groq LLM client for the reasoning layer.

Provides integration with Groq's fast inference API including:
- API client with retry logic
- Rate limiting
- Error handling and fallbacks
- Response parsing
"""
import json
import asyncio
from typing import Any, Optional
from datetime import datetime
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

try:
    from openai import OpenAI, AsyncOpenAI, APIError, RateLimitError
except ImportError:
    OpenAI = None
    AsyncOpenAI = None
    APIError = Exception
    RateLimitError = Exception

from config.settings import settings

logger = structlog.get_logger(__name__)


class GroqClientError(Exception):
    """Base exception for Groq client errors."""
    pass


class GroqRateLimitError(GroqClientError):
    """Raised when rate limited by the API."""
    pass


class GroqClient:
    """
    Client for interacting with Groq's fast inference API.

    Features:
    - Automatic retry with exponential backoff
    - Rate limiting compliance
    - Response validation and parsing
    - Fallback handling
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        timeout: int = None,
        max_retries: int = None,
    ):
        """
        Initialize the Groq client.

        Args:
            api_key: Groq API key (defaults to settings)
            base_url: API base URL (defaults to settings)
            model: Model to use (defaults to settings)
            temperature: LLM temperature (defaults to settings)
            max_tokens: Max response tokens (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
            max_retries: Max retry attempts (defaults to settings)
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.base_url = base_url or settings.GROQ_BASE_URL
        self.model = model or settings.GROQ_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.timeout = timeout or settings.LLM_TIMEOUT
        self.max_retries = max_retries or settings.LLM_MAX_RETRIES

        # Initialize client
        self._client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None

        # Usage tracking
        self.total_requests = 0
        self.total_tokens_used = 0
        self.last_request_time: Optional[datetime] = None

        # Initialize if API key available
        if self.api_key and OpenAI:
            self._init_clients()

    def _init_clients(self):
        """Initialize OpenAI-compatible clients."""
        try:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            self._async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            logger.info("Groq client initialized", model=self.model)
        except Exception as e:
            logger.warning("Failed to initialize Groq client", error=str(e))

    @property
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        return self._client is not None and bool(self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    def complete(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        response_format: str = None,
    ) -> dict[str, Any]:
        """
        Get a completion from Groq.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Optional response format ("json" for JSON mode)

        Returns:
            Dict containing response and metadata
        """
        if not self.is_available:
            return self._fallback_response(prompt, "Client not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            # Note: Groq doesn't support response_format yet, so we'll handle JSON in post-processing
            if response_format == "json":
                # Add JSON instruction to the prompt
                if system_prompt:
                    messages[0]["content"] += "\n\nIMPORTANT: Respond with valid JSON only."
                else:
                    messages.insert(0, {"role": "system", "content": "Respond with valid JSON only."})

            response = self._client.chat.completions.create(**kwargs)

            self._update_stats(response)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "success": True,
            }

        except RateLimitError as e:
            logger.warning("Rate limited by Groq API", error=str(e))
            raise GroqRateLimitError(str(e))

        except APIError as e:
            logger.error("Groq API error", error=str(e))
            raise

        except Exception as e:
            logger.error("Unexpected error calling Groq", error=str(e))
            return self._fallback_response(prompt, str(e))

    async def complete_async(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        response_format: str = None,
    ) -> dict[str, Any]:
        """
        Async version of complete.
        """
        if not self._async_client:
            return self._fallback_response(prompt, "Async client not available")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if response_format == "json":
                if system_prompt:
                    messages[0]["content"] += "\n\nIMPORTANT: Respond with valid JSON only."
                else:
                    messages.insert(0, {"role": "system", "content": "Respond with valid JSON only."})

            response = await self._async_client.chat.completions.create(**kwargs)

            self._update_stats(response)

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "success": True,
            }

        except Exception as e:
            logger.error("Async Groq call failed", error=str(e))
            return self._fallback_response(prompt, str(e))

    def complete_json(
        self,
        prompt: str,
        system_prompt: str = None,
        schema: dict = None,
    ) -> dict[str, Any]:
        """
        Get a JSON-formatted completion from Groq.

        Args:
            prompt: The user prompt (should request JSON output)
            system_prompt: Optional system prompt
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON response
        """
        # Enhance prompt to request JSON
        json_prompt = prompt
        if not "json" in prompt.lower():
            json_prompt = f"{prompt}\n\nRespond with valid JSON only."

        response = self.complete(
            prompt=json_prompt,
            system_prompt=system_prompt,
            response_format="json",
        )

        if not response["success"]:
            return response

        # Parse JSON response
        try:
            content = response["content"]
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            parsed = json.loads(content)

            # Validate against schema if provided
            if schema:
                # Basic validation (could use jsonschema for full validation)
                for required_key in schema.get("required", []):
                    if required_key not in parsed:
                        raise ValueError(f"Missing required key: {required_key}")

            return {
                **response,
                "parsed": parsed,
            }

        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON response", error=str(e))
            return {
                **response,
                "parsed": None,
                "parse_error": str(e),
            }

    def _update_stats(self, response):
        """Update usage statistics."""
        self.total_requests += 1
        self.last_request_time = datetime.utcnow()
        if hasattr(response, 'usage') and response.usage:
            self.total_tokens_used += response.usage.total_tokens

    def _fallback_response(self, prompt: str, error: str) -> dict[str, Any]:
        """Generate a fallback response when API is unavailable."""
        logger.warning("Using fallback response", error=error)
        return {
            "content": self._generate_fallback_content(prompt),
            "model": "fallback",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "finish_reason": "fallback",
            "success": False,
            "error": error,
        }

    def _generate_fallback_content(self, prompt: str) -> str:
        """Generate basic fallback content based on prompt."""
        # Enhanced rule-based fallback with actual logistics logic
        if "situation" in prompt.lower() and "assessment" in prompt.lower():
            return json.dumps({
                "situation_summary": "Rule-based analysis: System monitoring active fleet",
                "issues": self._detect_issues_rule_based(prompt),
                "risk_assessment": "Medium - Manual verification recommended",
                "recommendations": [
                    "Review truck locations for anomalies",
                    "Check traffic conditions on active routes",
                    "Verify load assignments and priorities"
                ],
                "confidence": 0.6,
                "reasoning_trace": [
                    "Applied rule-based issue detection",
                    "Analyzed fleet status patterns",
                    "Generated safety-first recommendations"
                ]
            })
        elif "issue" in prompt.lower() or "problem" in prompt.lower():
            return json.dumps({
                "situation_summary": "Unable to analyze - LLM unavailable",
                "issues": [],
                "risk_assessment": "Unknown - manual review required",
                "recommendations": ["Review system manually", "Check LLM connectivity"],
                "confidence": 0.0,
            })
        return "Fallback response - LLM unavailable. Please review manually."

    def _detect_issues_rule_based(self, prompt: str) -> list:
        """Enhanced rule-based issue detection from prompt content."""
        issues = []
        
        # Extract basic patterns from prompt
        if "stuck" in prompt.lower():
            issues.append({
                "id": f"ISSUE-STUCK-{datetime.utcnow().strftime('%H%M%S')}",
                "type": "stuck",
                "severity": "high",
                "description": "Truck appears to be stuck based on status",
                "affected_truck_ids": [],
                "affected_load_ids": [],
                "metadata": {"detection_method": "rule_based"}
            })
        
        if "heavy" in prompt.lower() and "traffic" in prompt.lower():
            issues.append({
                "id": f"ISSUE-TRAFFIC-{datetime.utcnow().strftime('%H%M%S')}",
                "type": "traffic",
                "severity": "medium",
                "description": "Heavy traffic conditions detected",
                "affected_truck_ids": [],
                "affected_load_ids": [],
                "metadata": {"detection_method": "rule_based"}
            })
        
        if "urgent" in prompt.lower() and ("unassigned" in prompt.lower() or "pending" in prompt.lower()):
            issues.append({
                "id": f"ISSUE-CAPACITY-{datetime.utcnow().strftime('%H%M%S')}",
                "type": "capacity_mismatch",
                "severity": "high",
                "description": "Urgent loads require immediate assignment",
                "affected_truck_ids": [],
                "affected_load_ids": [],
                "metadata": {"detection_method": "rule_based"}
            })
        
        return issues

    def get_stats(self) -> dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
            "model": self.model,
            "is_available": self.is_available,
        }


# Singleton instance
_groq_client: Optional[GroqClient] = None


def get_groq_client() -> GroqClient:
    """Get or create the global Groq client instance."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client

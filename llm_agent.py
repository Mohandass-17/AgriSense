from __future__ import annotations
import json
import os
import re
import asyncio
import httpx
from typing import Any, Dict, List
from dotenv import load_dotenv

from agents.base_agent import BaseAgent

load_dotenv()

class LLMAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="LLMAgent",
            description="Agricultural chatbot powered by Gemini REST API.",
        )
        self.api_key = (
            os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        )
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip()        
        self.model = self.model_name
        self.provider = "gemini"
        self.remedies: Dict[str, Dict[str, Any]] = {}
        
        self.is_configured = bool(self.api_key)

    def _system_instruction(self) -> str:
        return (
            "You are AgriSense, an expert agricultural assistant for farmers and agronomists. "
            "Give practical, crop-aware advice on irrigation, diseases, pests, nutrients, and "
            "farm planning. Prefer concise, actionable guidance. Mention uncertainty when details "
            "such as crop stage, variety, soil type, or region are missing."
        )

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        lines: List[str] = []
        for item in history[-6:]:
            role = "User" if item.get("role") == "user" else "Assistant"
            text = str(item.get("text", "")).strip()
            if text:
                lines.append(f"{role}: {text}")
        return "\n".join(lines) if lines else "No prior conversation."

    def _build_prompt(
        self,
        question: str,
        metadata: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> str:
        return (
            "Answer the farmer's question using the metadata and conversation history.\n"
            "Return only valid JSON with this schema:\n"
            '{\n'
            '"reply":"string",\n'
            '"topic":"chat|disease_management|fertilizer|pest_control|irrigation|crop_selection",\n'
            '"details":{"crop":"string","provider":"gemini","notes":"string"}\n'
            '}\n'
            "Do not use markdown fences.\n"
            f"Metadata: {json.dumps(metadata, ensure_ascii=True)}\n"
            f"Conversation:\n{self._format_history(history)}\n"
            f"Question: {question}"
        )

    def _extract_json_payload(self, raw_text: str) -> Dict[str, Any] | None:
        raw_text = raw_text.strip()
        if not raw_text:
            return None
            
        candidates = [raw_text]
        fence_match = re.search(r"`{3}(?:json)?\s*(\{.*?\})\s*`{3}", raw_text, re.DOTALL)
        if fence_match:
            candidates.append(fence_match.group(1))
            
        brace_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
        if brace_match:
            candidates.append(brace_match.group(1))
            
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
        return None

    def _normalize_result(
        self,
        payload: Dict[str, Any] | None,
        fallback_text: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        crop = str(metadata.get("crop_type", "unknown")).strip() or "unknown"
        details = payload.get("details", {}) if isinstance(payload, dict) else {}
        if not isinstance(details, dict):
            details = {}
            
        return {
            "text": (
                str(payload.get("reply", "")).strip()
                if isinstance(payload, dict) and payload.get("reply")
                else fallback_text
            ),
            "topic": (
                str(payload.get("topic", "chat")).strip()
                if isinstance(payload, dict)
                else "chat"
            ),
            "details": {
                **details,
                "crop": str(details.get("crop", crop)).strip() or crop,
                "provider": self.provider,
                "model": self.model_name,
            },
        }

    async def _call_gemini_async(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "systemInstruction": {
                "parts": [{"text": self._system_instruction()}]
            },
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        max_retries = 4
        base_delay = 2

        # Use an explicit async HTTP client to solve proxy/SSL issues natively
        # Disable strict SSL verification to bypass the lab network firewall proxy
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    # Intercept rate limits (429) or server errors (500, 503)
                    if response.status_code in [429, 500, 503] and attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt)
                        self.logger.warning(f"API capacity limited (HTTP {response.status_code}). Retrying in {sleep_time}s...")
                        await asyncio.sleep(sleep_time)
                        continue
                        
                    response.raise_for_status()
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                    
                except httpx.HTTPStatusError as e:
                    # Expose the JSON body for debugging on hard errors like 400 or 404
                    error_body = e.response.text
                    raise Exception(f"HTTP {e.response.status_code}: {error_body}")
                    
                except httpx.RequestError as e:
                    # Network connection errors
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt)
                        self.logger.warning(f"Network error: {str(e)}. Retrying in {sleep_time}s...")
                        await asyncio.sleep(sleep_time)
                        continue
                        
                    raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")

    async def respond_to_query(
        self,
        question: str,
        metadata: Dict[str, Any] | None = None,
        history: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        metadata = metadata or {}
        history = history or []
        crop = str(metadata.get("crop_type", "unknown")).strip() or "unknown"
        
        if not self.api_key:
            return {
                "text": (
                    "Gemini API key not configured. Set GEMINI_API_KEY in your environment "
                    "or .env file and restart the server."
                ),
                "topic": "error",
                "details": {"provider": self.provider, "crop": crop, "model": self.model_name},
            }
            
        prompt = self._build_prompt(question=question, metadata=metadata, history=history)
        
        try:
            # We now call the async httpx function directly (no more thread blocking)
            raw_text = await self._call_gemini_async(prompt)
            payload = self._extract_json_payload(raw_text)
            return self._normalize_result(payload, raw_text.strip(), metadata)
        except Exception as exc:
            return {
                "text": f"System Error: {exc}",
                "topic": "error",
                "details": {
                    "provider": self.provider,
                    "crop": crop,
                    "model": self.model_name,
                },
            }
"""Iztack-Finance - Portal Learner. Analyzes and fills billing forms via Playwright + IA."""
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from app.utils.llm import LLMClient

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)


class PortalLearner:
    """Learns and fills billing portal forms using Playwright + LLM analysis."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def analyze_portal(self, portal_url: str, store_name: str) -> Dict[str, Any]:
        """Analyze a billing portal to detect its structure (uses Playwright browser)."""
        # Try to load saved template
        template = self._load_template(store_name)
        if template:
            logger.info(f"Using saved template for {store_name}")
            return template

        # Analyze with Playwright
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(portal_url, timeout=30000)
                await page.wait_for_load_state("networkidle", timeout=15000)

                # Get page content for analysis
                html = await page.content()
                title = await page.title()

                # Ask LLM to analyze the page structure
                analysis_prompt = (
                    f"Analiza esta página de facturación de '{store_name}' (URL: {portal_url}).\n"
                    f"Título: {title}\n"
                    f"Partes clave del HTML:\n{html[:3000]}\n\n"
                    "Responde SOLO en JSON con esta estructura:\n"
                    '{"requires_login": bool, "requires_fiscal_data": bool, '
                    '"form_method": "post|get", "has_captcha": bool, '
                    '"fields": [{"name": "rfc|folio|fecha|total|regimen|uso_cfdi|...", "type": "text|select|date", "required": bool}], '
                    '"login_url": "url o null"}'
                )

                response = await self.llm.chat(
                    user_message=analysis_prompt,
                    max_tokens=500,
                    temperature=0.0,
                )

                # Parse JSON from LLM response
                structure = self._parse_json_response(response)
                if not structure:
                    structure = {
                        "requires_login": False,
                        "requires_fiscal_data": True,
                        "form_method": "post",
                        "has_captcha": False,
                        "fields": [],
                    }

                # Save template for future use
                self._save_template(store_name, structure)

                await browser.close()
                return structure

        except ImportError:
            logger.warning("Playwright not installed, using LLM-only analysis")
            return await self._analyze_with_llm_only(portal_url, store_name)
        except Exception as e:
            logger.error(f"Playwright portal analysis error: {e}")
            return await self._analyze_with_llm_only(portal_url, store_name)

    async def fill_and_submit(
        self,
        portal_url: str,
        ticket: Any,
        credentials: Any = None,
        fiscal_data: Dict = None,
        gasto_type: str = None,
    ) -> Dict:
        """Fill and submit a billing form using Playwright."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(portal_url, timeout=30000)

                # Login if needed
                if credentials and hasattr(credentials, "encrypted_password"):
                    password = credentials.credential_hint  # TODO: decrypt
                    # Find and fill login form
                    await self._fill_login_form(page, credentials.credential_hint, password)

                # Fill billing form
                if fiscal_data:
                    # Fill RFC
                    if fiscal_data.get("rfc"):
                        await self._fill_field(page, "rfc", fiscal_data["rfc"])

                    # Fill razon_social
                    if fiscal_data.get("razon_social"):
                        await self._fill_field(page, "razon_social", fiscal_data["razon_social"])

                    # Fill CP
                    if fiscal_data.get("codigo_postal"):
                        await self._fill_field(page, "codigo_postal", fiscal_data["codigo_postal"])

                    # Select regimen fiscal
                    if fiscal_data.get("regimen_fiscal"):
                        await self._select_option(page, "regimen", fiscal_data["regimen_fiscal"])

                # Fill ticket data
                if ticket.receipt_number:
                    await self._fill_field(page, "folio", ticket.receipt_number)
                if ticket.purchase_date:
                    await self._fill_field(page, "fecha", str(ticket.purchase_date))
                if ticket.total_amount:
                    await self._fill_field(page, "total", str(ticket.total_amount))

                # Select gasto type
                if gasto_type:
                    await self._select_option(page, "uso_cfdi", gasto_type)

                # Submit
                submit_btn = await page.query_selector(
                    "button[type=submit], input[type=submit], button:has-text('Enviar'), button:has-text('Generar')"
                )
                if submit_btn:
                    await submit_btn.click()
                    await page.wait_for_timeout(5000)

                await browser.close()
                return {"success": True, "invoice": None}

        except ImportError:
            return {"success": False, "error": "Playwright no instalado"}
        except Exception as e:
            logger.error(f"Form fill error: {e}")
            return {"success": False, "error": str(e)[:200]}

    async def _analyze_with_llm_only(self, portal_url: str, store_name: str) -> Dict:
        """Fallback: analyze portal structure using LLM without Playwright."""
        prompt = (
            f"Para la tienda '{store_name}', la URL de facturación es '{portal_url}'.\n"
            "¿Qué campos suele pedir un portal de facturación mexicano típico?\n"
            "Responde SOLO en JSON: {\"requires_login\": bool, \"requires_fiscal_data\": bool, "
            "\"fields\": [{\"name\": \"...\", \"required\": bool}]}"
        )
        try:
            response = await self.llm.chat(user_message=prompt, max_tokens=300, temperature=0.0)
            return self._parse_json_response(response) or {"requires_login": False, "requires_fiscal_data": True, "fields": []}
        except Exception:
            return {"requires_login": False, "requires_fiscal_data": True, "fields": []}

    async def _fill_login_form(self, page, username: str, password: str):
        """Fill a login form."""
        try:
            await page.fill("input[name=email], input[type=email]", username)
            await page.fill("input[name=password], input[type=password]", password)
            login_btn = await page.query_selector("button[type=submit], button:has-text('Entrar'), button:has-text('Iniciar')")
            if login_btn:
                await login_btn.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Login form fill error: {e}")

    async def _fill_field(self, page, field_name: str, value: str):
        """Fill a single form field by name or placeholder."""
        try:
            selector = (
                f"input[name*='{field_name}'], "
                f"input[placeholder*='{field_name}'], "
                f"select[name*='{field_name}']"
            )
            el = await page.query_selector(selector)
            if el:
                await el.fill(value)
        except Exception:
            pass  # Field not found, skip

    async def _select_option(self, page, field_name: str, value: str):
        """Select an option from a dropdown."""
        try:
            selector = f"select[name*='{field_name}']"
            el = await page.query_selector(selector)
            if el:
                await el.select_option(label=value)
        except Exception:
            pass

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response."""
        import re
        code_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        json_str = code_match.group(1).strip() if code_match else None
        if not json_str:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            json_str = json_match.group(0) if json_match else None
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None

    def _save_template(self, store_name: str, structure: Dict):
        """Save portal structure template to disk."""
        safe_name = "".join(c for c in store_name if c.isalnum() or c in "_ ")[:50]
        path = TEMPLATES_DIR / f"{safe_name}.json"
        try:
            path.write_text(json.dumps(structure, indent=2, ensure_ascii=False))
            logger.info(f"Template saved: {path}")
        except Exception as e:
            logger.error(f"Failed to save template: {e}")

    def _load_template(self, store_name: str) -> Optional[Dict]:
        """Load a saved portal template."""
        safe_name = "".join(c for c in store_name if c.isalnum() or c in "_ ")[:50]
        path = TEMPLATES_DIR / f"{safe_name}.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return None
        return None
"""AgentMail service - email for AI agents."""
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from agentmail import AgentMail
    AGENTMAIL_AVAILABLE = True
except ImportError:
    AGENTMAIL_AVAILABLE = False
    logger.warning("agentmail not installed: pip install agentmail")


@dataclass
class EmailMessage:
    message_id: str
    thread_id: str
    subject: str
    from_email: str
    to_email: str
    text: str
    html: str = ""
    timestamp: str = ""
    labels: List[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class AgentMailService:
    """Service for sending and receiving emails via AgentMail."""

    def __init__(self):
        self.api_key = os.environ.get("AGENTMAIL_API_KEY", "")
        self.inbox_email = "amanita@agentmail.to"
        self.inbox_id = None
        self.client = None
        self._initialize()

    def _initialize(self):
        """Initialize the AgentMail client."""
        if not AGENTMAIL_AVAILABLE:
            logger.error("agentmail package not installed")
            return

        if not self.api_key:
            logger.error("AGENTMAIL_API_KEY not set")
            return

        try:
            self.client = AgentMail(api_key=self.api_key)
            self._find_inbox()
            logger.info(f"AgentMail initialized: {self.inbox_email}")
        except Exception as e:
            logger.error(f"Failed to initialize AgentMail: {e}")

    def _find_inbox(self):
        """Find the existing inbox or create one."""
        if not self.client:
            return

        try:
            inboxes = self.client.inboxes.list()
            for inbox in inboxes.inboxes:
                if inbox.email == self.inbox_email:
                    self.inbox_id = inbox.inbox_id
                    logger.info(f"Found inbox: {self.inbox_id}")
                    return

            # Create inbox if not found
            inbox = self.client.inboxes.create(
                username="amanita",
                client_id="ai-agency-inbox-v1"
            )
            self.inbox_id = inbox.inbox_id
            logger.info(f"Created inbox: {self.inbox_id}")
        except Exception as e:
            logger.error(f"Failed to find/create inbox: {e}")

    def is_configured(self) -> bool:
        """Check if AgentMail is properly configured."""
        return bool(self.api_key and self.client and self.inbox_id)

    def get_status(self) -> Dict:
        """Get AgentMail status."""
        return {
            "configured": self.is_configured(),
            "api_key_set": bool(self.api_key),
            "inbox_email": self.inbox_email,
            "inbox_id": self.inbox_id,
            "sdk_available": AGENTMAIL_AVAILABLE,
        }

    def send_email(self, to: str, subject: str, text: str, html: str = None) -> Dict:
        """Send an email from the agent's inbox."""
        if not self.is_configured():
            return {"success": False, "error": "AgentMail not configured"}

        try:
            kwargs = {
                "to": to,
                "subject": subject,
                "text": text,
            }
            if html:
                kwargs["html"] = html

            result = self.client.inboxes.messages.send(self.inbox_id, **kwargs)
            logger.info(f"Email sent to {to}: {result.message_id}")
            return {
                "success": True,
                "message_id": result.message_id,
                "thread_id": result.thread_id,
            }
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}

    def check_inbox(self, limit: int = 10) -> List[EmailMessage]:
        """Check inbox for new emails."""
        if not self.is_configured():
            return []

        try:
            messages = self.client.inboxes.messages.list(self.inbox_id, limit=limit)
            result = []
            for msg in messages.messages:
                result.append(EmailMessage(
                    message_id=msg.message_id,
                    thread_id=msg.thread_id,
                    subject=msg.subject or "",
                    from_email=msg.from_[0].email if msg.from_ else "",
                    to_email=msg.to[0].email if msg.to else "",
                    text=msg.extracted_text or msg.text or "",
                    html=msg.extracted_html or msg.html or "",
                    timestamp=str(msg.created_at) if msg.created_at else "",
                    labels=msg.labels or [],
                ))
            return result
        except Exception as e:
            logger.error(f"Failed to check inbox: {e}")
            return []

    def get_verification_code(self, platform: str = None) -> Optional[str]:
        """Search for verification codes in recent emails."""
        messages = self.check_inbox(limit=20)

        for msg in messages:
            text = msg.text.lower()
            subject = msg.subject.lower()

            # Look for verification codes
            if platform and platform.lower() in subject:
                # Common patterns for verification codes
                import re
                patterns = [
                    r'verification code[:\s]*(\d{4,6})',
                    r'code[:\s]*(\d{4,6})',
                    r'(\d{4,6})\s*is your.*code',
                    r'your.*code.*is\s*(\d{4,6})',
                    r'verify.*account.*code[:\s]*(\d{4,6})',
                ]
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        return match.group(1)

            # Look for verification links
            if 'verify' in text or 'confirm' in text:
                import re
                url_pattern = r'(https?://[^\s<>"]+(?:verify|confirm|activate)[^\s<>"]*)'
                match = re.search(url_pattern, text)
                if match:
                    return match.group(1)

        return None

    def get_thread(self, thread_id: str) -> Dict:
        """Get a specific email thread."""
        if not self.is_configured():
            return {"error": "AgentMail not configured"}

        try:
            thread = self.client.inboxes.threads.get(self.inbox_id, thread_id)
            return {
                "thread_id": thread.thread_id,
                "subject": thread.subject,
                "message_count": len(thread.messages) if hasattr(thread, 'messages') else 0,
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
agentmail_service = AgentMailService()

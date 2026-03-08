"""Gmail API 客户端。"""

import base64
from email.message import EmailMessage

from googleapiclient.discovery import build


class GmailClient:
    def __init__(self, credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    def get_messages(self, query: str = "is:inbox", max_results: int = 10) -> dict:
        resp = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        return {"messages": resp.get("messages", []), "nextPageToken": resp.get("nextPageToken")}

    def get_message(self, message_id: str) -> dict:
        return (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

    def search_messages(self, query: str, max_results: int = 10) -> dict:
        return self.get_messages(query=query, max_results=max_results)

    def create_draft(self, to: str, subject: str, body: str) -> dict:
        msg = EmailMessage()
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        return (
            self.service.users()
            .drafts()
            .create(userId="me", body={"message": {"raw": raw}})
            .execute()
        )

    def mark_read(self, message_id: str) -> dict:
        return (
            self.service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
            .execute()
        )

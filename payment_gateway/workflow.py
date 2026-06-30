from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional
import uuid


@dataclass
class PaymentRequest:
    merchant_id: str
    customer_id: str
    amount: float
    currency: str
    payment_method: str
    card_number: str
    device_risk_score: int = 0
    velocity_flag: bool = False


class PaymentGateway:
    def __init__(self) -> None:
        self._transactions: Dict[str, Dict[str, object]] = {}

    def process_payment(self, request: PaymentRequest) -> Dict[str, object]:
        payment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        fraud_result = self._run_fraud_checks(request)
        if fraud_result["decision"] != "allow":
            result = {
                "payment_id": payment_id,
                "status": "blocked",
                "authorization_status": "blocked",
                "capture_status": "not_requested",
                "settlement_status": "not_started",
                "reconciliation_status": "not_required",
                "fraud_decision": fraud_result["decision"],
                "fraud_reason": fraud_result["reason"],
                "created_at": now,
            }
            self._transactions[payment_id] = result
            return result

        authorization_status = self._authorize(request)
        if authorization_status != "approved":
            result = {
                "payment_id": payment_id,
                "status": "declined",
                "authorization_status": authorization_status,
                "capture_status": "not_requested",
                "settlement_status": "not_started",
                "reconciliation_status": "not_required",
                "fraud_decision": "allow",
                "created_at": now,
            }
            self._transactions[payment_id] = result
            return result

        capture_status = self._capture(payment_id, request)
        settlement_status = self._settle(payment_id, request)
        reconciliation_status = self._reconcile(payment_id, request)

        result = {
            "payment_id": payment_id,
            "status": "settled",
            "authorization_status": authorization_status,
            "capture_status": capture_status,
            "settlement_status": settlement_status,
            "reconciliation_status": reconciliation_status,
            "fraud_decision": "allow",
            "created_at": now,
        }
        self._transactions[payment_id] = result
        return result

    def _run_fraud_checks(self, request: PaymentRequest) -> Dict[str, str]:
        if request.velocity_flag:
            return {"decision": "block", "reason": "velocity_exceeded"}
        if request.device_risk_score >= 80:
            return {"decision": "review", "reason": "high_device_risk"}
        if request.amount >= 1000:
            return {"decision": "review", "reason": "high_amount"}
        return {"decision": "allow", "reason": "ok"}

    def _authorize(self, request: PaymentRequest) -> str:
        if not request.card_number:
            return "declined"
        if request.amount <= 0:
            return "declined"
        if request.card_number.endswith("002"):
            return "declined"
        return "approved"

    def _capture(self, payment_id: str, request: PaymentRequest) -> str:
        return "captured"

    def _settle(self, payment_id: str, request: PaymentRequest) -> str:
        return "settled"

    def _reconcile(self, payment_id: str, request: PaymentRequest) -> str:
        return "reconciled"

    def process_chargeback(self, payment_id: str, reason: str) -> Dict[str, object]:
        transaction = self._transactions.get(payment_id)
        if not transaction:
            return {"status": "not_found"}

        transaction["chargeback_status"] = "initiated"
        transaction["chargeback_reason"] = reason
        transaction["status"] = "chargeback"
        transaction["reconciliation_status"] = "chargeback_pending"
        return transaction

    def get_transaction(self, payment_id: str) -> Optional[Dict[str, object]]:
        return self._transactions.get(payment_id)

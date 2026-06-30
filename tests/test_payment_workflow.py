import unittest

from payment_gateway.workflow import PaymentGateway, PaymentRequest


class PaymentWorkflowTests(unittest.TestCase):
    def test_successful_payment_lifecycle(self):
        gateway = PaymentGateway()
        request = PaymentRequest(
            merchant_id="merchant-001",
            customer_id="customer-001",
            amount=125.50,
            currency="USD",
            payment_method="card",
            card_number="4111111111111111",
        )

        result = gateway.process_payment(request)

        self.assertEqual(result["status"], "settled")
        self.assertEqual(result["authorization_status"], "approved")
        self.assertEqual(result["capture_status"], "captured")
        self.assertEqual(result["settlement_status"], "settled")
        self.assertEqual(result["reconciliation_status"], "reconciled")
        self.assertIn("payment_id", result)

    def test_declined_payment_lifecycle(self):
        gateway = PaymentGateway()
        request = PaymentRequest(
            merchant_id="merchant-001",
            customer_id="customer-002",
            amount=500.00,
            currency="USD",
            payment_method="card",
            card_number="4000000000000002",
        )

        result = gateway.process_payment(request)

        self.assertEqual(result["status"], "declined")
        self.assertEqual(result["authorization_status"], "declined")
        self.assertEqual(result["capture_status"], "not_requested")
        self.assertEqual(result["settlement_status"], "not_started")
        self.assertEqual(result["reconciliation_status"], "not_required")

    def test_fraud_blocked_payment(self):
        gateway = PaymentGateway()
        request = PaymentRequest(
            merchant_id="merchant-001",
            customer_id="customer-003",
            amount=150.00,
            currency="USD",
            payment_method="card",
            card_number="4111111111111111",
            velocity_flag=True,
        )

        result = gateway.process_payment(request)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["authorization_status"], "blocked")
        self.assertEqual(result["fraud_decision"], "block")
        self.assertEqual(result["fraud_reason"], "velocity_exceeded")

    def test_chargeback_flow(self):
        gateway = PaymentGateway()
        payment = gateway.process_payment(
            PaymentRequest(
                merchant_id="merchant-001",
                customer_id="customer-004",
                amount=250.00,
                currency="USD",
                payment_method="card",
                card_number="4111111111111111",
            )
        )

        updated = gateway.process_chargeback(payment["payment_id"], "unauthorized_transaction")

        self.assertEqual(updated["chargeback_status"], "initiated")
        self.assertEqual(updated["chargeback_reason"], "unauthorized_transaction")
        self.assertEqual(updated["status"], "chargeback")


if __name__ == "__main__":
    unittest.main()

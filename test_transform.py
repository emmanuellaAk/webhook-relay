from app.transformer import render_template

payload = {
    "id": "evt_001",
    "type": "payment.succeeded",
    "data": {"amount": 5000, "currency": "usd", "customer": "Ama"},
}

# Whole-value: should return the integer 5000, not "5000"
print(render_template("{{data.amount}}", payload))

# Embedded: should splice into a sentence
print(render_template("Payment {{id}} for {{data.amount}} received", payload))

# Nested template (Slack-shaped), with a missing field to prove graceful handling
slack = {
    "text": "New payment from {{data.customer}}",
    "amount": "{{data.amount}}",
    "note": "ref {{data.missing_field}}",
}
print(render_template(slack, payload))
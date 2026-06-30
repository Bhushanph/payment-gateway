from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_path = Path('/workspaces/payment-gateway/docs/payment_gateway_architecture.png')
out_path.parent.mkdir(parents=True, exist_ok=True)

width, height = 1400, 850
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

# Colors
blue = '#2F5D8C'
green = '#2E7D32'
orange = '#C96A00'
purple = '#6A4C93'
gray = '#4B5563'
light = '#EAF2F8'
light_green = '#E8F5E9'
light_orange = '#FFF3E0'
light_purple = '#F3E5F5'

# Helpers

def rounded_box(x0, y0, x1, y1, color, fill, title, subtitle):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=fill, outline=color, width=3)
    draw.text((x0 + 20, y0 + 18), title, fill=color)
    draw.text((x0 + 20, y0 + 56), subtitle, fill=gray)


# Boxes
rounded_box(80, 90, 330, 220, blue, light, 'Customer', 'Checkout, wallet, card, bank transfer')
rounded_box(430, 90, 760, 220, blue, light, 'Merchant App', 'Order management, checkout UI')
rounded_box(820, 90, 1180, 220, blue, light, 'API Gateway', 'Secure entry point, auth, routing')

rounded_box(80, 330, 330, 500, green, light_green, 'Payment Orchestrator', 'Validation, workflows, state')
rounded_box(430, 330, 760, 500, green, light_green, 'Fraud & Risk Engine', 'Velocity, device risk, rules')
rounded_box(820, 330, 1180, 500, green, light_green, 'Token Vault', 'PCI-safe payment token storage')

rounded_box(80, 570, 330, 740, orange, light_orange, 'Acquiring Bank', 'Authorization, capture, settlement')
rounded_box(430, 570, 760, 740, orange, light_orange, 'Issuer / Card Network', 'Customer account validation')
rounded_box(820, 570, 1180, 740, purple, light_purple, 'Reconciliation & Ledger', 'Settlement, reporting, chargebacks')

# Arrows
arrow_color = '#374151'

def arrow(x1, y1, x2, y2):
    draw.line([x1, y1, x2, y2], fill=arrow_color, width=3)
    draw.polygon([(x2, y2), (x2 - 12, y2 - 6), (x2 - 12, y2 + 6)], fill=arrow_color)

arrow(330, 155, 430, 155)
arrow(760, 155, 820, 155)
arrow(205, 220, 205, 330)
arrow(595, 220, 595, 330)
arrow(1000, 220, 1000, 330)
arrow(205, 500, 205, 570)
arrow(595, 500, 595, 570)
arrow(1000, 500, 1000, 570)

# Header
try:
    font = ImageFont.load_default()
except Exception:
    font = None

header = 'Payment Gateway Architecture'
subheader = 'Secure payment orchestration for banking and financial services'
if font:
    draw.text((80, 25), header, fill='black')
    draw.text((80, 60), subheader, fill=gray)
else:
    draw.text((80, 25), header, fill='black')
    draw.text((80, 60), subheader, fill=gray)

img.save(out_path)
print(f'Created {out_path}')

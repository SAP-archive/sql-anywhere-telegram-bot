MSG_START = "Hello, {name}\!\n\nPlease, choose your language\."

MSG_NOTIFY_EN = (
    """Hello, {first_name}\!\n\n"""
    """As of {timestamp}, your order `{id}` has arrived to our base.\n"""
    """We are going to deliver it to your address _{address}_ no later than in 3 days.\n\n"""
    """*Product Details:*\n"""
    """Product: {product}\n"""
    """Model: {model}\n"""
    """Price: €{price:.2f}\n"""
    """Amount: {amount}\n"""
    """Weight: {weight:.3f} kg\n"""
    """ID: {id}"""
)

MSG_NOTIFY_RU = (
    """Здравствуйте, {first_name}\!\n\n"""
    """{timestamp} Ваш заказ `{id}` доставлен в наш центр.\n"""
    """Мы доставим его по Вашему адресу _{address}_ не позже, чем через 3 дня.\n\n"""
    """*Детали заказа:*\n"""
    """Товар: {product}\n"""
    """Модель: {model}\n"""
    """Цена: €{price:.2f}\n"""
    """Количество: {amount}\n"""
    """Вес: {weight:.3f} кг\n"""
    """ID: {id}"""
)

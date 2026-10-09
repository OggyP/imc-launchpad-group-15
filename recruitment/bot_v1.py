from student_bot import StudentBot
from models import OrderBook, OrderRequest, Side

print_feed_top = True
print_positions = True

L = "LETTUCE"
C = "CHICKEN"
B = "BUN"

CLB = "BURGER"
CL = "SALAD"

class YourBot(StudentBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arbs = [
                    [[CLB], [C, L, B]],
                    [[CL], [C, L]]
                ]

    # returns None if no quotes, else [price, volume]
    def best_price(self, direction, prods: list[str], orderbooks: dict[str, OrderBook]): 
        valid = True
        price = 0
        volume = None
        for prod in prods:
            orderbook = orderbooks[prod]
            quotes = orderbook.buy_orders if direction == "BUY" else orderbook.sell_orders
            if len(quotes) > 0:
                price += quotes[0].price
                if volume == None:
                    volume = quotes[0].volume
                else:
                    volume = min(volume, quotes[0].volume)
            else:
                valid = False

        if valid:
            return [price, volume]

    def amount_to_buy_for_regularization(self, position: int):
        return 0

    def get_position_regularization_order(self, product: str, position: int):
        buy_volume = self.amount_to_buy_for_regularization(position)
        side = Side.BUY if buy_volume >= 0 else Side.SELL
        volume = abs(buy_volume)

        return OrderRequest(product=product, price=1499 if side == Side.BUY else 2, side=side, volume=volume)

    def regularize_position(self):
        positions = self.get_positions()
        for product, position in positions.items():
            order = self.get_position_regularization_order(product, position)
            self.hit(order)

    def on_orderbooks(self, orderbooks: dict[str, OrderBook]):
        # TODO: implement smart money making strategies in this handler
        # This will run everytime an orderbook updates.
        # The method receives a dictionary of {PRODUCT_NAME (str): OrderBook}
        # You are not guaranteed to have a valid orderbook for every product.

        self.regularize_position()
from student_bot import StudentBot
from models import OrderBook, OrderRequest, Side
import time

print_feed_top = True
print_positions = True

L = "LETTUCE"
C = "CHICKEN"
B = "BUN"

CLB = "BURGER"
CL = "SALAD"

FEE = 0
BLOCK_TIME = 2

class YourBot(StudentBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arbs = [
                    [[CLB], [C, L, B]],
                    [[CL], [C, L]]
                ]
        self.block_time = None

    # returns None if no quotes, else [price, volume]

    def amount_to_buy_for_regularization(self, position: int):
        if abs(position) > 100:
            return int(- 2 * round(position / 150))
        return 0

    def get_position_regularization_order(self, product: str, position: int):
        buy_volume = self.amount_to_buy_for_regularization(position)
        side = Side.BUY if buy_volume >= 0 else Side.SELL
        volume = abs(buy_volume)

        return OrderRequest(product=product, price=1499 if side == Side.BUY else 2, side=side, volume=volume)

    def regularize_position(self):
        positions = self.get_positions()

        positions.setdefault(L, 0)
        positions.setdefault(C, 0)
        positions.setdefault(B, 0)
        positions.setdefault(CLB, 0)
        positions.setdefault(CL, 0)

        positions[C] += positions[CLB]
        positions[L] += positions[CLB]
        positions[B] += positions[CLB]

        positions[C] += positions[CL]
        positions[L] += positions[CL]

        positions[CL] = 0
        positions[CLB] = 0
        
        for product, position in positions.items():
            order = self.get_position_regularization_order(product, position)
            if order.volume > 0:
                self.hit(order)

    def best_price(self, direction, prods: list[str], orderbooks: dict[str, OrderBook]):
        if direction not in ("BUY", "SELL"):
            raise ValueError("direction must be BUY or SELL")

        total_price = 0
        prices = []
        volume = None
        for prod in prods:
            orderbook = orderbooks.get(prod)
            if orderbook is None:
                return None

            quotes = orderbook.sell_orders if direction == "BUY" else orderbook.buy_orders
            if not quotes:
                return None

            quote = quotes[0]
            total_price += quote.price
            prices.append(quote.price)
            volume = quote.volume if volume is None else min(volume, quote.volume)

        if volume is None or volume <= 0:
            return None
        return total_price, volume, prices

    def execute_arbitrage(self, sell_quote, sell_products, buy_quote, buy_products):
        self.block_time = time.time() + BLOCK_TIME
        volume = min(sell_quote[1], buy_quote[1])
        if volume <= 0 or sell_quote[0] <= buy_quote[0]:
            return

        print("ARB Found:", sell_products, buy_products,
              "Profit:", (sell_quote[0] - buy_quote[0]) * volume)
        for product, price in zip(sell_products, sell_quote[2]):
            self.hit(OrderRequest(product=product, side=Side.SELL,
                                  price=price, volume=volume))
        for product, price in zip(buy_products, buy_quote[2]):
            self.hit(OrderRequest(product=product, side=Side.BUY,
                                  price=price, volume=volume))

    def arbitrage(self, orderbooks: dict[str, OrderBook]):
        for arb_left, arb_right in self.arbs:
            buy_left = self.best_price("BUY", arb_left, orderbooks)
            buy_right = self.best_price("BUY", arb_right, orderbooks)
            sell_left = self.best_price("SELL", arb_left, orderbooks)
            sell_right = self.best_price("SELL", arb_right, orderbooks)

            if sell_left is not None and buy_right is not None:
                self.execute_arbitrage(sell_left, arb_left, buy_right, arb_right)

            if sell_right is not None and buy_left is not None:
                self.execute_arbitrage(sell_right, arb_right, buy_left, arb_left)

    def on_orderbooks(self, orderbooks: dict[str, OrderBook]):
        # TODO: implement smart money making strategies in this handler
        # This will run everytime an orderbook updates.
        # The method receives a dictionary of {PRODUCT_NAME (str): OrderBook}
        # You are not guaranteed to have a valid orderbook for every product.

        # products = [C, L, B, CLB, CL]     

        # print(orderbooks.keys())

        self.arbitrage(orderbooks)
        if self.block_time is None or time.time() < self.block_time:
            self.regularize_position()

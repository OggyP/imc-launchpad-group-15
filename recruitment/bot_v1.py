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



    def on_orderbooks(self, orderbooks: dict[str, OrderBook]):
        # TODO: implement smart money making strategies in this handler
        # This will run everytime an orderbook updates.
        # The method receives a dictionary of {PRODUCT_NAME (str): OrderBook}
        # You are not guaranteed to have a valid orderbook for every product.

        products = [C, L, B, CLB, CL]     

        for arb_left, arb_right in self.arbs:
            buy_left = self.best_price("BUY", arb_left, orderbooks)
            buy_right = self.best_price("BUY", arb_right, orderbooks)
            sell_left = self.best_price("SELL", arb_left, orderbooks)
            sell_right = self.best_price("SELL", arb_right, orderbooks)

            if buy_left != None and sell_left == None:
                if buy_left[0] < sell_left[0]:


                

            


        print("Hitting LETTUCE")
        # WARNING: this code will attempt to buy 1 LETTUCE at price 20 for every iteration
        # self.hit(OrderRequest(product="LETTUCE", side=Side.BUY, price=20, volume=1))

        if print_feed_top:
            for orderbook in orderbooks.values():
                buy_quotes = orderbook.buy_orders
                if len(buy_quotes) > 0:
                    print(
                        "BEST BID for",
                        orderbook.product,
                        ":",
                        buy_quotes[0].volume,
                        "@ $",
                        buy_quotes[0].price,
                    )

                sell_quotes = orderbook.sell_orders
                if len(sell_quotes) > 0:
                    print(
                        "BEST ASK for",
                        orderbook.product,
                        ":",
                        sell_quotes[0].volume,
                        "@ $",
                        sell_quotes[0].price,
                    )
        if print_positions:
            print(self.get_positions())
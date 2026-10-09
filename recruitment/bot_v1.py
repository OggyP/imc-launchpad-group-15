from student_bot import StudentBot
from models import OrderBook, OrderRequest, Side

print_feed_top = True
print_positions = True

L = "LETTUCE"
C = "CHICKEN"
B = "BUN"

CLB = "BURGER"
CL = "SALAD"

FEE = 0

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
        prices = []
        volume = 0
        for prod in prods:
            if not prod in orderbooks:
                return
            orderbook = orderbooks[prod]
            quotes = orderbook.buy_orders if direction == "BUY" else orderbook.sell_orders
            if len(quotes) > 0:
                price += quotes[0].price
                prices.append(quotes[0].price)
                if volume == None:
                    volume = quotes[0].volume
                else:
                    volume = min(volume, quotes[0].volume)
            else:
                return

        if valid:
            return (price, volume, prices)

    def arb_attempt(self, orderbooks: dict[str, OrderBook]):
        for arb_left, arb_right in self.arbs:
            buy_left = self.best_price("BUY", arb_left, orderbooks)
            buy_right = self.best_price("BUY", arb_right, orderbooks)
            sell_left = self.best_price("SELL", arb_left, orderbooks)
            sell_right = self.best_price("SELL", arb_right, orderbooks)

            if sell_left != None and buy_right != None:
                print("Profit per:", sell_left[0], buy_right[0])
                profit_per = sell_left[0] - buy_right[0]
                volume = min(sell_left[1], buy_right[1])
                profit = profit_per * volume
                print()
                if profit > 0:
                    print("ARB Found:", arb_left, arb_right, "Profit:", profit)
                    print("Prices:", sell_left[2], buy_right[2])
                    print("Prices for each product:", list(zip(arb_left, sell_left[2])), list(zip(arb_right, buy_right[2])))
                
                    for i, prod in enumerate(arb_left):
                        self.hit(OrderRequest(product=prod, side=Side.SELL, price=sell_left[2][i], volume=sell_left[1]))
                    for i, prod in enumerate(arb_right):
                        self.hit(OrderRequest(product=prod, side=Side.BUY, price=buy_right[2][i], volume=buy_right[1]))
                    # arb possible 

            if sell_right != None and buy_left != None:
                print("Profit per:", sell_right[0], buy_left[0])
                profit_per = sell_right[0] - buy_left[0]
                volume = min(sell_right[1], buy_left[1])
                profit = profit_per * volume
                if profit > 0:
                    print("ARB Found:", arb_right, arb_left, "Profit:", profit)
                    print("Prices:", sell_right[2], buy_left[2])
                    print("Prices for each product:", list(zip(arb_right, sell_right[2])), list(zip(arb_left, buy_left[2])))

                    for i, prod in enumerate(arb_right):
                        self.hit(OrderRequest(product=prod, side=Side.SELL, price=sell_right[2][i], volume=sell_right[1]))
                    for i, prod in enumerate(arb_left):
                        self.hit(OrderRequest(product=prod, side=Side.BUY, price=buy_left[2][i], volume=buy_left[1]))
                    # arb possible 


    def on_orderbooks(self, orderbooks: dict[str, OrderBook]):
        # TODO: implement smart money making strategies in this handler
        # This will run everytime an orderbook updates.
        # The method receives a dictionary of {PRODUCT_NAME (str): OrderBook}
        # You are not guaranteed to have a valid orderbook for every product.

        # products = [C, L, B, CLB, CL]     

        print(orderbooks.keys())

        


        # print("Hitting LETTUCE")
        # # WARNING: this code will attempt to buy 1 LETTUCE at price 20 for every iteration
        # # self.hit(OrderRequest(product="LETTUCE", side=Side.BUY, price=20, volume=1))

        # if print_feed_top:
        #     for orderbook in orderbooks.values():
        #         buy_quotes = orderbook.buy_orders
        #         if len(buy_quotes) > 0:
        #             print(
        #                 "BEST BID for",
        #                 orderbook.product,
        #                 ":",
        #                 buy_quotes[0].volume,
        #                 "@ $",
        #                 buy_quotes[0].price,
        #             )

        #         sell_quotes = orderbook.sell_orders
        #         if len(sell_quotes) > 0:
        #             print(
        #                 "BEST ASK for",
        #                 orderbook.product,
        #                 ":",
        #                 sell_quotes[0].volume,
        #                 "@ $",
        #                 sell_quotes[0].price,
        #             )
        # if print_positions:
        #     print(self.get_positions())
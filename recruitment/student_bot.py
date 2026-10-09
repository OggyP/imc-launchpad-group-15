from base_bot import BaseBot
from models import OrderBook, OrderRequest, OrderResponse, Trade

class StudentBot(BaseBot):
    _orderbooks: dict[str, OrderBook]
    _positions: dict[str, int]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orderbooks = {}
        self._positions = self.request_positions() or {}

    def request_net_positions(self):
        raise NotImplementedError(
            "This function will not be implemented in the StudentBot class."
        )

    def on_orderbooks(self, orderbooks: dict[str, OrderBook]):
        raise NotImplementedError("You must override this method.")

    def on_orderbook(self, orderbook):
        pass

    def get_positions(self) -> dict[str, int]:
        return self._positions

    def on_trades(self, trades: list[Trade]) -> None:
        self._positions = self.request_positions() or {}

    def quote(self, order_request: OrderRequest) -> OrderResponse | None:
        return self.send_order(order_request)

    def hit(
        self, order_request: OrderRequest
    ) -> tuple[OrderResponse | None] | tuple[OrderResponse, dict | None]:
        order_response = self.send_order(order_request)
        if order_response and order_response.volume > 0:
            cancel_response = self.cancel_order_by_id(order_response.id)
            return (order_response, cancel_response)
        return (order_response,)

    def start(self, *args, **kwargs) -> None:
        super().start(*args, **kwargs, on_orderbook=self._on_orderbook)

    def _on_orderbook(self, orderbook: OrderBook):
        self._orderbooks[orderbook.product] = orderbook
        self.on_orderbooks(self._orderbooks)

    def _register_bot(self) -> None:
        """
        Disallow student bot from self-registering to prevent accidental sign-ups
        """
        pass

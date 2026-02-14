from arb_monitor.exchanges import OpinionClient, PolymarketClient


def test_opinion_parse_data_shape():
    payload = {"data": {"bids": [{"price": "0.51", "size": "120"}], "asks": [{"price": "0.55", "size": "80"}]}}
    top = OpinionClient._parse(payload)
    assert top.bid and top.bid.price == 0.51
    assert top.ask and top.ask.price == 0.55


def test_poly_parse_clob_shape():
    payload = {"bids": [{"price": "0.44", "size": "200"}], "asks": [{"price": "0.46", "size": "150"}]}
    top = PolymarketClient._parse(payload)
    assert top.bid and top.bid.price == 0.44
    assert top.ask and top.ask.price == 0.46

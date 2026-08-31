def naive_match_orders(bids, asks):
    # Filter out orders with qty <= 0
    bids = [b for b in bids if b.qty > 0]
    asks = [a for a in asks if a.qty > 0]
    
    # Sort bids: highest price first, then earliest ts, then lex id
    bids.sort(key=lambda x: (-x.price, x.ts, x.id))
    # Sort asks: lowest price first, then earliest ts, then lex id
    asks.sort(key=lambda x: (x.price, x.ts, x.id))
    
    trades = []
    i, j = 0, 0  # pointers for bids and asks
    
    while i < len(bids) and j < len(asks):
        bid = bids[i]
        ask = asks[j]
        
        # Check if they can match
        if bid.price >= ask.price:
            # Match quantity is the minimum of remaining quantities
            match_qty = min(bid.qty, ask.qty)
            if match_qty > 0:
                # Create trade at ask's price
                trade = {
                    "bid": bid.id,
                    "ask": ask.id,
                    "price": ask.price,
                    "qty": match_qty
                }
                trades.append(trade)
                
                # Update remaining quantities
                bid.qty -= match_qty
                ask.qty -= match_qty
            
            # Move to next order if current is fully filled
            if bid.qty == 0:
                i += 1
            if ask.qty == 0:
                j += 1
        else:
            # No more matches possible due to price mismatch
            break
    
    return trades
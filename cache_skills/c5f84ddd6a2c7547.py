def fast_allocate(demands, stocks):
    # Create a copy of available stock quantities that we can modify
    stock_available = {st.sku: st.available for st in stocks}
    
    # Sort demands by priority (descending) then by id (ascending)
    sorted_demands = sorted(demands, key=lambda d: (-d.priority, d.id))
    
    allocations = []
    
    for demand in sorted_demands:
        # Check if there's any stock available for this SKU
        if demand.sku in stock_available and stock_available[demand.sku] > 0:
            # Allocate the minimum of what's demanded and what's available
            alloc_qty = min(demand.qty, stock_available[demand.sku])
            
            # Only create an allocation if qty > 0
            if alloc_qty > 0:
                # Create allocation as a dict
                allocations.append({
                    "id": demand.id,
                    "sku": demand.sku,
                    "qty": alloc_qty
                })
                
                # Reduce available stock
                stock_available[demand.sku] -= alloc_qty
    
    return allocations
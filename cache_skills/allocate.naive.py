def naive_allocate(demands, stocks):
    # Aggregate available stock by SKU
    stock_dict = {}
    for st in stocks:
        stock_dict[st.sku] = stock_dict.get(st.sku, 0) + st.available
    
    # Sort demands: higher priority first, then by id ascending
    sorted_demands = sorted(demands, key=lambda d: (-d.priority, d.id))
    
    allocations = []
    # Track how much has been allocated per demand and per sku
    allocated_to_demand = {d.id: 0 for d in demands}
    allocated_per_sku = {sku: 0 for sku in stock_dict}

    for demand in sorted_demands:
        remaining_demand = demand.qty - allocated_to_demand[demand.id]
        if remaining_demand <= 0:
            continue
        
        available_stock = stock_dict.get(demand.sku, 0) - allocated_per_sku.get(demand.sku, 0)
        if available_stock <= 0:
            continue

        alloc_qty = min(remaining_demand, available_stock)
        if alloc_qty > 0:
            allocations.append({
                "id": demand.id,
                "sku": demand.sku,
                "qty": alloc_qty
            })
            allocated_to_demand[demand.id] += alloc_qty
            allocated_per_sku[demand.sku] += alloc_qty

    return allocations
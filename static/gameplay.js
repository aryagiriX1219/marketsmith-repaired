function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Track placed orders AND in-flight requests
const placedOrders  = { BID: false, ASK: false };
const pendingOrders = { BID: false, ASK: false };  // double-click guard

async function executeTrade(action) {
    const orderType = action === 'Buy' ? 'BID' : 'ASK';
    const priceInput = document.getElementById("price-input");
    const price = Number(priceInput.value);

    if (!price || price <= 0) { alert("Enter valid price"); return; }
    if (price > 100)          { alert("Maximum price is 100"); return; }

    // Already placed OR request in-flight → ignore
    if (placedOrders[orderType] || pendingOrders[orderType]) {
        alert(`You already placed a ${action} order this round`);
        return;
    }

    const buyBtn  = document.getElementById("buy-btn");
    const sellBtn = document.getElementById("sell-btn");

    // Lock immediately BEFORE the fetch
    pendingOrders[orderType] = true;
    if (orderType === 'BID') { buyBtn.disabled = true;  buyBtn.style.opacity  = '0.4'; }
    else                     { sellBtn.disabled = true; sellBtn.style.opacity = '0.4'; }

    try {
        const response = await fetch('/api/order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({
                'type': orderType,
                'price': parseInt(price),
                'game_id': window.currentGameId
            })
        });

        const result = await response.json();

        if (result.status === 'queued') {
            placedOrders[orderType] = true;
            addOrderToUI(action, price);
            priceInput.value = '';

            // Keep button frozen permanently for this round
            if (orderType === 'BID') {
                buyBtn.disabled = true;
                buyBtn.style.opacity = '0.4';
                buyBtn.style.cursor  = 'not-allowed';
                buyBtn.title = 'BID already placed this round';
            } else {
                sellBtn.disabled = true;
                sellBtn.style.opacity = '0.4';
                sellBtn.style.cursor  = 'not-allowed';
                sellBtn.title = 'ASK already placed this round';
            }
        } else {
            // Server rejected → re-enable so they can try different price
            pendingOrders[orderType] = false;
            if (orderType === 'BID') { buyBtn.disabled  = false; buyBtn.style.opacity  = '1'; }
            else                     { sellBtn.disabled = false; sellBtn.style.opacity = '1'; }
            alert(result.message);
        }

    } catch (error) {
        console.error('Error placing order:', error);
        pendingOrders[orderType] = false;
        if (orderType === 'BID') { buyBtn.disabled  = false; buyBtn.style.opacity  = '1'; }
        else                     { sellBtn.disabled = false; sellBtn.style.opacity = '1'; }
        alert("Connection lost.");
    }
}

function addOrderToUI(action, price) {
    const actionColor = action === 'Buy' ? '#38a169' : '#e53e3e';
    const ordersList  = document.getElementById('working-orders-list');
    const orderRow    = document.createElement('div');
    orderRow.className = 'data-row order-item';
    orderRow.innerHTML = `
        <span style="color:${actionColor};font-weight:bold;">${action}</span>
        <span>$${price}</span>
    `;
    ordersList.appendChild(orderRow);
}

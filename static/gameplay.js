/**
 * Helper to get Django CSRF Token from cookies
 */
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

// Track which orders placed this round
const placedOrders = { BID: false, ASK: false };

/**
 * Connects to the backend API to place an order
 */
async function executeTrade(action) {
    const orderType = action === 'Buy' ? 'BID' : 'ASK';
    const priceInput = document.getElementById("price-input");
    const price = Number(priceInput.value);

    if (!price || price <= 0) {
        alert("Enter valid price");
        return;
    }

    if (price > 100) {
        alert("Maximum price is 100");
        return;
    }

    // Already placed this type — freeze
    if (placedOrders[orderType]) {
        alert(`You already placed a ${action} order this round`);
        return;
    }

    const buyBtn  = document.getElementById("buy-btn");
    const sellBtn = document.getElementById("sell-btn");

    // Disable button immediately to prevent double click
    if (orderType === 'BID') buyBtn.disabled = true;
    else sellBtn.disabled = true;

    const orderData = new URLSearchParams({
        'type': orderType,
        'price': parseInt(price),
        'game_id': window.currentGameId
    });

    try {
        const response = await fetch('/api/order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: orderData
        });

        const result = await response.json();

        if (result.status === 'queued') {
            placedOrders[orderType] = true;
            addOrderToUI(action, price);
            priceInput.value = '';

            // Visually freeze the button
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
            // Re-enable on error so they can retry with different price
            if (orderType === 'BID') buyBtn.disabled = false;
            else sellBtn.disabled = false;
            alert(result.message);
        }

    } catch (error) {
        console.error('Error placing order:', error);
        if (orderType === 'BID') buyBtn.disabled = false;
        else sellBtn.disabled = false;
        alert("Connection lost.");
    }
}

/**
 * Internal UI helper to render the row
 */
function addOrderToUI(action, price) {
    const actionColor = action === 'Buy' ? '#38a169' : '#e53e3e';
    const ordersList = document.getElementById('working-orders-list');

    const orderRow = document.createElement('div');
    orderRow.className = 'data-row order-item';

    orderRow.innerHTML = `
        <span style="color: ${actionColor}; font-weight: bold;">${action}</span>
        <span>$${price}</span>
    `;

    ordersList.appendChild(orderRow);
}

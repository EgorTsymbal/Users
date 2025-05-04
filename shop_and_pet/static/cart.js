document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('clear-cart-btn').addEventListener('click', clearCart);
});

function updateQuantity(itemId, change) {
    const newQuantity = getCurrentQuantity(itemId) + change;

    if (newQuantity < 1) {
        removeCartItem(itemId);
        return;
    }

    fetch(`/api/cart/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity: newQuantity
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка обновления количества');
        return response.json();
    })
    .then(data => {
        updateItemDisplay(itemId, newQuantity);
        updateGrandTotal();
        showToast('Количество обновлено');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Ошибка при обновлении количества', 'error');
    });
}

function getCurrentQuantity(itemId) {
    const quantityElement = document.querySelector(`.cart-item[data-item-id="${itemId}"] .item-quantity`);
    return parseInt(quantityElement.textContent);
}

function updateItemDisplay(itemId, newQuantity) {
    const itemElement = document.querySelector(`.cart-item[data-item-id="${itemId}"]`);
    const price = parseFloat(itemElement.querySelector('.item-price').textContent.split(' ')[0]);

    itemElement.querySelector('.item-quantity').textContent = newQuantity;
    itemElement.querySelector('.item-total span').textContent = (price * newQuantity).toFixed(2);
}

function removeCartItem(itemId) {
    if (!confirm('Удалить товар из корзины?')) return;

    fetch(`/api/cart/${itemId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка удаления товара');
        return response.json();
    })
    .then(data => {
        document.querySelector(`.cart-item[data-item-id="${itemId}"]`).remove();
        updateGrandTotal();
        showToast(data.message || 'Товар удалён из корзины');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Ошибка при удалении товара', 'error');
    });
}

function clearCart() {
    if (!confirm('Вы уверены, что хотите очистить корзину?')) return;

    fetch('/api/cart', {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка очистки корзины');
        return response.json();
    })
    .then(data => {
        document.querySelector('.cart-items').innerHTML = '';
        updateGrandTotal();
        showToast(data.message || 'Корзина очищена');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Ошибка при очистке корзины', 'error');
    });
}

function updateGrandTotal() {
    let total = 0;
    document.querySelectorAll('.item-total span').forEach(el => {
        total += parseFloat(el.textContent);
    });
    document.getElementById('grand-total').textContent = total.toFixed(2);

    // Если корзина пуста, скрываем кнопки
    if (total === 0) {
        document.querySelector('.cart-actions').style.display = 'none';
        document.querySelector('.cart-total').style.display = 'none';
    } else {
        document.querySelector('.cart-actions').style.display = 'block';
        document.querySelector('.cart-total').style.display = 'block';
    }
}

function checkout() {
    fetch('/api/checkout', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка оформления заказа');
        return response.json();
    })
    .then(data => {
        showToast(data.message || 'Заказ успешно оформлен');
        setTimeout(() => window.location.href = '/shop', 2000);
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Ошибка при оформлении заказа', 'error');
    });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.getElementById('toast-container').appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
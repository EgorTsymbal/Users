document.addEventListener('DOMContentLoaded', function() {
    initApplication();
});

function initApplication() {
    // Инициализация корзины
    updateCartCount();

    // Настройка обработчиков событий
    setupEventListeners();

    // Загрузка товаров по умолчанию
    loadProducts('pet_food');
}

function setupEventListeners() {
    // Обработчик для типа животного
    document.getElementById('animal-type-filter').addEventListener('change', function() {
        const animalType = this.value;
        const productType = document.querySelector('.product-type-btn.active').dataset.type;
        updateBreedFilter(animalType, productType);
    });

    // Обработчики для кнопок типа товара
    document.querySelectorAll('.product-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Активируем выбранную кнопку
            document.querySelectorAll('.product-type-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Обновляем фильтр пород при смене типа товара
            const animalType = document.getElementById('animal-type-filter').value;
            if (animalType) {
                updateBreedFilter(animalType, this.dataset.type);
            }

            applyFilters();
        });
    });

    // Обработчики для других фильтров
    document.getElementById('breed-filter').addEventListener('change', applyFilters);
    document.getElementById('age-filter').addEventListener('change', applyFilters);
}

function updateBreedFilter(animalType, productType) {
    const breedSelect = document.getElementById('breed-filter');

    // Показываем загрузку
    breedSelect.disabled = true;
    breedSelect.innerHTML = '<option value="">Загрузка пород...</option>';

    // Запрашиваем породы для выбранного типа животного
    fetch(`/api/breeds?animal_type=${animalType}&product_type=${productType}`)
        .then(response => response.json())
        .then(breeds => {
            breedSelect.innerHTML = '<option value="">Все породы</option>';

            if (breeds && breeds.length > 0) {
                breeds.forEach(breed => {
                    const option = document.createElement('option');
                    option.value = breed;
                    option.textContent = breed;
                    breedSelect.appendChild(option);
                });
            } else {
                breedSelect.innerHTML = '<option value="">Нет доступных пород</option>';
            }

            breedSelect.disabled = false;
            applyFilters();
        })
        .catch(error => {
            console.error('Ошибка загрузки пород:', error);
            breedSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
            breedSelect.disabled = false;
        });
}

function applyFilters() {
    const productType = document.querySelector('.product-type-btn.active').dataset.type;
    loadProducts(productType);
}

function loadProducts(type) {
    showLoading(true);

    const animalType = document.getElementById('animal-type-filter').value;
    const breed = document.getElementById('breed-filter').value;
    const age = document.getElementById('age-filter').value;

    const params = new URLSearchParams();
    params.append('type', type);
    if (animalType) params.append('animal_type', animalType);
    if (breed) params.append('breed', breed);
    if (age) params.append('age', age);

    fetch(`/api/products?${params.toString()}`)
        .then(response => response.json())
        .then(products => {
            renderProducts(products);
        })
        .catch(error => {
            console.error('Error loading products:', error);
            showError('Ошибка загрузки товаров');
        })
        .finally(() => showLoading(false));
}

function renderProducts(products) {
    const container = document.getElementById('products-container');

    if (!products || products.length === 0) {
        container.innerHTML = '';
        document.getElementById('no-products').style.display = 'block';
        return;
    }

    document.getElementById('no-products').style.display = 'none';
    container.innerHTML = '';

    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';

        productCard.innerHTML = `
            <h3>${product.name}</h3>
            <div class="product-details">
                <p><strong>Порода:</strong> ${product.breed}</p>
                <p><strong>Вес упаковки:</strong> ${product.weight} кг</p>
                <p><strong>Возраст:</strong> ${getAgeText(product.age_plus)}</p>
                <p><strong>Состав:</strong> ${product.structure}</p>
                <p><strong>Аллергены:</strong> ${product.allergies || 'нет'}</p>
                <p class="price"><strong>Цена:</strong> ${product.price} руб.</p>
            </div>
            <button class="add-to-cart-btn" 
                    onclick="addToCart(${product.id}, '${product.type}', ${product.price})">
                Добавить в корзину
            </button>
        `;

        container.appendChild(productCard);
    });
}

function getAgeText(agePlus) {
    const ageMap = {
        '1': 'Для молодых',
        '2': 'Для взрослых',
        '3': 'Для пожилых'
    };
    return ageMap[agePlus] || agePlus;
}

function addToCart(itemId, itemType, price) {
    showLoading(true);

    fetch('/api/cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            item_type: itemType,
            price: price,
            quantity: 1
        }),
    })
    .then(response => {
        if (!response.ok) throw new Error('Error adding to cart');
        return response.json();
    })
    .then(data => {
        updateCartCount();
        showToast(data.message || 'Товар добавлен в корзину');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Ошибка при добавлении в корзину', 'error');
    })
    .finally(() => showLoading(false));
}

function updateCartCount() {
    fetch('/api/cart')
        .then(response => {
            if (!response.ok) throw new Error('Error getting cart');
            return response.json();
        })
        .then(items => {
            const total = items.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cart-count').textContent = total;
        })
        .catch(error => console.error('Error updating cart count:', error));
}

function showLoading(show) {
    document.getElementById('loading-spinner').style.display = show ? 'flex' : 'none';
    if (show) {
        document.getElementById('no-products').style.display = 'none';
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Делаем функции глобальными для вызова из HTML
window.addToCart = addToCart;
window.loadProducts = loadProducts;
// FarmConnect Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Form validation feedback
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Star rating preview
    const ratingSelects = document.querySelectorAll('select[id$="_rating"]');
    ratingSelects.forEach(select => {
        select.addEventListener('change', function() {
            const value = parseInt(this.value);
            const parent = this.closest('.mb-3');
            let preview = parent.querySelector('.rating-preview');
            
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'rating-preview mt-2';
                this.after(preview);
            }
            
            let stars = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= value) {
                    stars += '<i class="fas fa-star text-warning"></i> ';
                } else {
                    stars += '<i class="far fa-star text-warning"></i> ';
                }
            }
            preview.innerHTML = stars;
        });
    });

    // Price calculator for orders
    const quantityInput = document.getElementById('id_quantity');
    if (quantityInput) {
        const priceElement = document.querySelector('[data-unit-price]');
        if (priceElement) {
            const unitPrice = parseFloat(priceElement.dataset.unitPrice);
            
            quantityInput.addEventListener('input', function() {
                const quantity = parseFloat(this.value) || 0;
                const total = (quantity * unitPrice).toFixed(2);
                
                let totalDisplay = document.getElementById('total-display');
                if (!totalDisplay) {
                    totalDisplay = document.createElement('div');
                    totalDisplay.id = 'total-display';
                    totalDisplay.className = 'alert alert-info mt-2';
                    this.after(totalDisplay);
                }
                
                totalDisplay.innerHTML = `<strong>Total Price:</strong> $${total}`;
            });
        }
    }

    // Toggle delivery address field based on delivery method
    const deliveryMethodSelect = document.getElementById('id_delivery_method');
    if (deliveryMethodSelect) {
        const addressField = document.getElementById('id_delivery_address');
        const addressContainer = addressField?.closest('.mb-3');
        
        function toggleAddressField() {
            if (deliveryMethodSelect.value === 'delivery') {
                addressContainer?.style.setProperty('display', 'block');
            } else {
                addressContainer?.style.setProperty('display', 'none');
            }
        }
        
        deliveryMethodSelect.addEventListener('change', toggleAddressField);
        toggleAddressField(); // Initial check
    }

    // Search filter toggle
    const filterToggle = document.getElementById('filter-toggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const filterPanel = document.getElementById('filter-panel');
            filterPanel.classList.toggle('d-none');
        });
    }

    // Image preview for file uploads
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    let preview = input.parentElement.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        input.parentElement.appendChild(preview);
                    }
                    preview.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading state for buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.closest('form')?.addEventListener('submit', function() {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalText;
            }, 3000);
        });
    });

    console.log('FarmConnect initialized successfully!');
});

// Utility Functions

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}
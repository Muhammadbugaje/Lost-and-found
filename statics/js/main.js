document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('deleteModal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.querySelector('.cancel-btn');
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const itemNameSpan = document.getElementById('itemName');
    const deleteForm = document.getElementById('deleteForm');
    
    console.log('JavaScript loaded', deleteButtons.length, 'delete buttons found');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const claimId = this.getAttribute('data-claim-id');
            const itemName = this.getAttribute('data-item-name');
            itemNameSpan.textContent = itemName;
            deleteForm.action = `/delete-claim/${claimId}`;
            modal.style.display = 'flex';
        });
    });

    closeBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    cancelBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
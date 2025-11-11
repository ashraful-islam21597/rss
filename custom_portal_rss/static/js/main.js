
console.log("Main JS Loaded");
// Open Modal Function
function openModalF(modalId, btnSelector) {
    const modal = document.getElementById(modalId)
    const overlay = document.querySelector('.modal-overlay');
    const btns = document.querySelectorAll(btnSelector)


    if (btns) {
        btns.forEach(btn => {
            btn.addEventListener('click', function () {
                if (modal) { modal.classList.add('active') }
                if (overlay) { overlay.classList.add('active') }
            })
        })
    }
}

openModalF('create-article-modal', '#open-create-article-modal-btn');

// Open and close modal
function closeAndOpenF(closeButtonId, closeModalId, openModalId) {
    const closeButton = document.getElementById(closeButtonId);
    const closeModal = document.getElementById(closeModalId);
    const openModal = document.getElementById(openModalId);

    if (closeButton) {
        closeButton.addEventListener('click', function () {
            closeModal.classList.remove('active');

            openModal.classList.add('active');
        });
    }
}


// close button function
function closeButtonF() {
    document.addEventListener('DOMContentLoaded', () => {
        const closeButtons = document.querySelectorAll('.close-btn');
        const overlay = document.querySelector('.modal-overlay');
        const modals = document.querySelectorAll('.my-modal');

        if (modals) {
            modals.forEach(modal => {
                modal.addEventListener('click', function (e) {
                    // If clicked directly on the modal (not on modal-content)
                    if (e.target === modal) {
                        modal.classList.remove('active');
                        document.querySelector('.modal-overlay')?.classList.remove('active');
                    }
                });
            });
        }

        if (closeButtons) {
            closeButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const modal = btn.closest('.my-modal');
                    const notification = btn.closest('.notification');

                    if (modal) {
                        modal.classList.remove('active');
                        overlay?.classList.remove('active'); // only modal close e overlay off
                    }

                    if (notification) {
                        notification.classList.remove('active');
                    }
                });
            });
        }


        // Close when overlay is clicked
        if (overlay) {
            overlay.addEventListener('click', () => {
                document.querySelectorAll('.my-modal.active').forEach(modal => {
                    modal.classList.remove('active');
                });
                overlay.classList.remove('active');
            });
        }
    });
}

closeButtonF()

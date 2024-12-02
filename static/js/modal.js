document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === "modal-content") {
        document.getElementById('modal').classList.remove('hidden');
    }
});

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
    document.getElementById('modal-content').innerHTML = '';
}

document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if (evt.detail.target.id === "operations-table") {
        closeModal();
    }
});

// Select2 initialization
$(document).ready(function() {
    $('.select2').select2({
        minimumInputLength: 1,
        allowClear: true,
        width: '100%',
    });
});

$(document).on('select2:open', () => {
    document.querySelector('.select2-search__field').focus();
});

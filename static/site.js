
pizza_toggle_paid = function(pid) {
    btn = $('#paid' + pid);
    if (btn.hasClass('active')) {
        btn.removeClass('active');
        btn.removeClass('btn-success');
    } else {
        btn.addClass('active');
        btn.addClass('btn-success');
    }
    $.post('/edit/' + pid + '/toggle_paid')
}

pizza_delete = function(pid) {
    entry = $('#entry' + pid);
    entry.remove()
    $.post('/edit/' + pid + '/delete')
}

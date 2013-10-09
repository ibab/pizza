
display_nopizzas = function() {
    if($.trim($("#orders").html())=='') {
        li = $('<li>', {id: 'noentry', class: 'list-group-item'}).append(
               $('<em>').text('No pizzas so far. Why not add one?')
              )
        li.slideDown();
        li.css('display', 'block');
        $("#orders").append(li);
    } else {
        $('#noentry').slideUp(function() {
            $('#noentry').remove();
        });
    }
}

render_initial_entries = function() {
    $.getJSON('/get/entries', function(entries) {
        pizza_entries = entries
        orders = $("#orders")
        for (var i=0; i<entries.length; i++) {
            create_entry(entries[i]);
        }
        display_nopizzas();
    });
}

create_entry = function(entry) {
    description = entry['description'];
    pid = entry['pid'];
    console.log(pid);
    price = entry['price'];
    author = entry['author'];
    paid = entry['paid'];

    var li = $('<li>', {id: 'entry'+pid, class: 'list-group-item'});
    var span = $('<span>', {class: 'badge pull-left'});
    span.text(price);
    li.append(span);
    li.append(description + ' (' + author + ')');

    button1 = $('<button>', {id: 'paid'+pid, class: 'btn btn-default btn-xs'}).append('bezahlt');
    button2 = $('<button>', {class: 'btn btn-default btn-xs'}).append('löschen');
    if (paid) {
        button1.addClass('active btn-success');
    }

    button1.click(pid, function(pid) {
        $.post('/edit/' + pid.data + '/toggle_paid');
    });
    button2.click(pid, function(pid) {
        $.post('/edit/' + pid.data + '/delete');
    });

    btngrp = $('<div>', {class: 'btn-group pull-right'}).append(button1, button2);
    li.slideDown();
    li.css('display', 'block');
    li.append(btngrp);
    $('#orders').append(li);
    display_nopizzas();
}


delete_entry = function(pid) {
    entry = $('#entry' + pid);
    entry.slideUp(400, function() {
        entry.remove();
        display_nopizzas();
    });
}

toggle_paid = function(pid) {
    btn = $('#paid' + pid);
    if (btn.hasClass('active')) {
        btn.removeClass('active');
        btn.removeClass('btn-success');
    } else {
        btn.addClass('active');
        btn.addClass('btn-success');
    }
}

render_initial_entries();

$('#addpizza').on('submit', function(event) {
    event.preventDefault();
    $.post('/add', $('#addpizza').serialize(), function(data) {
        type = data.type;
        msg = data.msg
        var div = undefined
        if (type == 'error') {
            div = $('<div>', {class: 'alert alert-danger alert-dismissable'});
            div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>')
            div.append($('<strong>').text('Failure! '));
            div.append(msg);
        } else if (type == 'success') {
            div = $('<div>', {class: 'alert alert-success alert-dismissable'});
            div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>')
            div.append($('<strong>').text('Success! '));
            div.append(msg);
        }
        div.slideDown();
        $('#main-panel').before(div);
        div.delay(3000).slideUp();
    });
});

(function(){
    ws = new WebSocket("ws://pizza.babushk.in:5000/websocket");
    //ws.addEventListener('open', function(e){
    //});
    //ws.onerror = function(){
    //    setTimeout(function(){start(websocketServerLocation)}, 1000);
    //};
    ws.addEventListener('message', function(e) {
        evt = JSON.parse(e.data);
        if (evt['type'] == 'create_entry') {
            create_entry(evt['data']);
        }
        if (evt['type'] == 'delete_entry') {
            delete_entry(evt['data']);
        }
        if (evt['type'] == 'toggle_paid') {
            toggle_paid(evt['data']);
        }
    });
})();

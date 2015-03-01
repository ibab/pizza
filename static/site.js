var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;

/*
 * The Orders component is responsible for
 * managing the state of all orders
 *
 */
var Orders = React.createClass({
    getInitialState: function() {
        state = {orders: []};
        return state;
    },
    componentDidMount: function() {
        $.getJSON('/get/entries', function(orders) {
            this.setState({orders: orders});
        }.bind(this));

        // Set up websocket to get updates
        ws = new WebSocket("ws://localhost:5000/websocket");
        ws.addEventListener('message', function(e) {
            evt = JSON.parse(e.data);
            if (evt.type == 'update') {
                orders = JSON.parse(evt.data);
                this.setState({orders: orders});
            }
        }.bind(this));
    },
    togglePaid: function(i) {
        id = this.state.orders[i].pid

        var orders = this.state.orders
        orders[i].paid = !orders[i].paid
        this.setState({orders: orders});

        $.post('/edit/' + id + '/toggle_paid');
    },
    deleteOrder: function(i) {
        id = this.state.orders[i].pid
        $.post('/edit/' + id + '/delete');

        var neworders = React.addons.update(this.state.orders, {$splice: [[i, 1]]});
        this.setState({orders: neworders});

    },
    render: function() {
        if (this.state.orders.length == 0) {
            return (
                <li id="noentry" className="list-group-item">
                    <em>Soweit keine Bestellungen.</em>
                </li>
            );
        } else {
            var orderList = this.state.orders.map(function(order, i) {
                return (
                    <Order description={order.description}
                           price={order.price}
                           author={order.author}
                           paid={order.paid}
                           togglePaid={this.togglePaid.bind(this, i)}
                           deleteOrder={this.deleteOrder.bind(this, i)}
                           key={order.pid}>
                    </Order>
                );
            }.bind(this));

            return (
                <ReactCSSTransitionGroup transitionName="example">
                {orderList}
                </ReactCSSTransitionGroup>
            );
        }
    }
});

/*
 * The Order component represents a single
 * entry in the orders list.
 *
 */
var Order = React.createClass({
    render: function() {
        if (this.props.paid) {
            var paidClass = "active btn-success";
        } else {
            var paidClass = "";
        }

        return (
            <li className="list-group-item">
                <span className="badge pull-left">
                    {this.props.price}
                </span>
                {this.props.description + ' (' + this.props.author + ')'}
                <div className="btn-group pull-right">
                    <button onClick={this.props.togglePaid} className={"btn btn-default btn-xs " + paidClass}>
                        bezahlt
                    </button>
                    <button onClick={this.props.deleteOrder} className="btn btn-default btn-xs">
                        löschen
                    </button>
                </div>
            </li>
        );
    }
});

React.render(
  <Orders />,
  document.getElementById('orders')
);

/*
 * The OrderForm component allows the user to add a
 * new order to the list.
 *
 */
var OrderForm = React.createClass({
    onSubmit: function(e) {
        e.preventDefault();
        var author = this.refs.author.getDOMNode().value;
        var description = this.refs.description.getDOMNode().value;
        var price = this.refs.price.getDOMNode().value;

        $.post('/add', {
            author: author,
            description: description,
            price: price
        },
        function(data) {
            if (data.type == "error") {
                div = $('<div>', {class: 'alert alert-danger alert-dismissable'});
                div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>')
                div.append($('<strong>').text('Failure! '));
                div.append(data.msg);
                $('#main-panel').before(div);
            }
        });

        this.refs.author.getDOMNode().value = '';
        this.refs.description.getDOMNode().value = '';
        this.refs.price.getDOMNode().value = '';
    },
    render: function() {
        return (
            <form id="addpizza" className="form-inline" role="form" onSubmit={this.onSubmit}>
              <div className="form-group col-sm-4">
                <input type="text" className="form-control" ref="description" placeholder="Bestellung"></input>
              </div>
              <div className="form-group col-sm-3">
                <input type="text" className="form-control" ref="author" placeholder="Name"></input>
              </div>
              <div className="form-group col-sm-3">
                <div className="input-group">
                  <input type="text" className="form-control" ref="price" placeholder="Preis"></input>
                  <span className="input-group-addon">€</span>
                </div>
              </div>
              <div className="form-group">
                <button type="submit" className="btn btn-primary">Bestellen</button>
              </div>
            </form>
        );
    }
});

React.render(
  <OrderForm />,
  document.getElementById('order-form')
);


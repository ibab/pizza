
ReactCSSTransitionGroup = React.addons.CSSTransitionGroup
update = React.addons.update
events = new Events()

# The Orders component is responsible for
# managing the state of all orders
Orders = React.createClass
  getInitialState: -> {orders: []}

  componentDidMount: ->
    $.getJSON '/get/entries', (orders) => @setState(orders: orders)

    ws = new WebSocket 'ws://localhost:5000/websocket'
    ws.addEventListener 'message', (e) =>
      evt = JSON.parse(e.data)
      if evt.type == 'update'
        orders = JSON.parse(evt.data)
        @setState(orders: orders)

    # Listen to delete-all event
    events.on 'delete-all', =>
      @state.orders.map (order) ->
        $.post "/edit/#{order.pid}/delete"

  togglePaid: (i) ->
    id = @state.orders[i].pid
    orders = @state.orders
    orders[i].paid = !orders[i].paid
    @setState(orders: orders)
    $.post "/edit/#{id}/toggle_paid"

  deleteOrder: (i) ->
    id = @state.orders[i].pid
    $.post "/edit/#{id}/delete"
    neworders = update @state.orders, {$splice: [[i, 1]]}
    @setState(orders: neworders)

  render: ->
    if @state.orders.length == 0
      orderList = (
        <li className="list-group-item">
          <em>Soweit keine Bestellungen.</em>
        </li>
      )
    else
      orderList = @state.orders.map (order, i) =>
        (
          <Order description={order.description}
                 price={order.price}
                 author={order.author}
                 paid={order.paid}
                 togglePaid={@togglePaid.bind(@, i)}
                 deleteOrder={@deleteOrder.bind(@, i)}
                 key={order.pid}>
          </Order>
        )
    return (
      <ReactCSSTransitionGroup transitionName="orders"
                               component="ul"
                               id="orders-list"
                               className="list-group">
          {orderList}
      </ReactCSSTransitionGroup>
    )

# The Order component represents a single entry in the orders list.
Order = React.createClass
  render: ->
    paidClass = if @props.paid then "active btn-success" else ""
    (
      <li className="list-group-item">
          <span className="badge pull-left">
              {@props.price}
          </span>
          {@props.description + ' (' + @props.author + ')'}
          <div className="btn-group pull-right">
              <button onClick={@props.togglePaid}
                      className="btn btn-default btn-xs #{paidClass}">
                  bezahlt
              </button>
              <button onClick={@props.deleteOrder}
                      className="btn btn-default btn-xs">
                  löschen
              </button>
          </div>
      </li>
    )

# The OrderForm component allows the user to add a new order to the list.
OrderForm = React.createClass
  onSubmit: (e) ->
    e.preventDefault()
    author = @refs.author.getDOMNode().value
    description = @refs.description.getDOMNode().value
    price = @refs.price.getDOMNode().value

    $.post '/add',
      author: author
      description: description
      price: price
    , (data) -> if data.type == 'error'
      div = $('<div>', {class: 'alert alert-danger alert-dismissable'})
      div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>')
      div.append($('<strong>').text('Failure! '))
      div.append(data.msg)
      $('#orders-panel').before(div)

    @refs.author.getDOMNode().value = ''
    @refs.description.getDOMNode().value = ''
    @refs.price.getDOMNode().value = ''

  render: ->
    (
      <div id="order-form" className="panel-footer">
        <form id="addpizza"
              className="form-inline"
              role="form"
              onSubmit={@onSubmit}>
          <div className="form-group col-sm-4">
            <input type="text"
                   className="form-control"
                   ref="description"
                   placeholder="Bestellung"></input>
          </div>
          <div className="form-group col-sm-3">
            <input type="text"
                   className="form-control"
                   ref="author"
                   placeholder="Name"></input>
          </div>
          <div className="form-group col-sm-3">
            <div className="input-group">
              <input type="text"
                     className="form-control"
                     ref="price"
                     placeholder="Preis"></input>
              <span className="input-group-addon">€</span>
            </div>
          </div>
          <div className="form-group">
            <button type="submit"
                    className="btn btn-primary">Bestellen</button>
          </div>
        </form>
      </div>
    )

# The OrdersPanel component represents the entire orders UI.
OrdersPanel = React.createClass
  render: ->
    (
      <div className="panel panel-default">
        <div className="panel-heading">
          <h3 className="panel-title">
            Bestellungen
          </h3>
        </div>
          <Orders />
          <OrderForm />
      </div>
    )

React.render <OrdersPanel />,
             document.getElementById 'orders-panel'

AdminPanel = React.createClass
  deleteAll: ->
    events.emit('delete-all')
  render: ->
    (
      <div className="col-sm-5">
        <div className="panel panel-default">
          <div className="panel-heading">
            <h3 className="panel-title">
              Admin
            </h3>
          </div>
          <ul className="list-group">
            <li className="list-group-item">
              <a href="/order.pdf" className="btn btn-primary">Bestellung herunterladen</a>
            </li>
            <li className="list-group-item">
              <a onClick={this.deleteAll} className="btn btn-primary">Bestellungen löschen</a>
            </li>
          </ul>
        </div>
      </div>
    )

React.render <AdminPanel />,
             document.getElementById 'admin-panel'


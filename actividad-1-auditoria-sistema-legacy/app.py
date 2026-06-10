from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "legacy_inventario.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with open("database.sql", "r", encoding="utf-8") as file:
        sql_script = file.read()

    conn = get_connection()
    conn.executescript(sql_script)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return """
    <h1>Sistema Legacy de Inventario</h1>
    <p>Eco-Distribuidora S.A.</p>
    <ul>
        <li><a href="/productos">Ver productos</a></li>
        <li><a href="/ventas">Ver ventas</a></li>
        <li><a href="/producto/nuevo">Registrar producto</a></li>
        <li><a href="/venta/nueva">Registrar venta</a></li>
    </ul>
    <p><strong>Nota:</strong> Sistema CRUD básico, funcional pero pobre para la toma de decisiones.</p>
    """


@app.route("/productos")
def productos():
    conn = get_connection()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()

    html = """
    <h1>Listado de Productos</h1>
    <a href="/">Volver</a> | <a href="/producto/nuevo">Nuevo producto</a>
    <table border="1" cellpadding="6">
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Stock</th>
            <th>Precio</th>
            <th>Acciones</th>
        </tr>
        {% for p in productos %}
        <tr>
            <td>{{ p["id_producto"] }}</td>
            <td>{{ p["nombre"] }}</td>
            <td>{{ p["categoria"] }}</td>
            <td>{{ p["stock"] }}</td>
            <td>{{ p["precio"] }}</td>
            <td>
                <a href="/producto/editar/{{ p['id_producto'] }}">Editar</a>
                <a href="/producto/eliminar/{{ p['id_producto'] }}">Eliminar</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    """
    return render_template_string(html, productos=productos)


@app.route("/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        conn = get_connection()
        conn.execute(
            "INSERT INTO productos (nombre, categoria, stock, precio) VALUES (?, ?, ?, ?)",
            (
                request.form["nombre"],
                request.form["categoria"],
                request.form["stock"],
                request.form["precio"]
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("productos"))

    return """
    <h1>Registrar Producto</h1>
    <form method="post">
        <label>Nombre:</label><br>
        <input type="text" name="nombre"><br><br>

        <label>Categoría:</label><br>
        <input type="text" name="categoria"><br><br>

        <label>Stock:</label><br>
        <input type="number" name="stock"><br><br>

        <label>Precio:</label><br>
        <input type="number" step="0.01" name="precio"><br><br>

        <button type="submit">Guardar</button>
    </form>
    <br>
    <a href="/productos">Volver</a>
    """


@app.route("/producto/editar/<int:id_producto>", methods=["GET", "POST"])
def editar_producto(id_producto):
    conn = get_connection()

    if request.method == "POST":
        conn.execute(
            """
            UPDATE productos
            SET nombre = ?, categoria = ?, stock = ?, precio = ?
            WHERE id_producto = ?
            """,
            (
                request.form["nombre"],
                request.form["categoria"],
                request.form["stock"],
                request.form["precio"],
                id_producto
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("productos"))

    producto = conn.execute(
        "SELECT * FROM productos WHERE id_producto = ?",
        (id_producto,)
    ).fetchone()
    conn.close()

    html = """
    <h1>Editar Producto</h1>
    <form method="post">
        <label>Nombre:</label><br>
        <input type="text" name="nombre" value="{{ producto['nombre'] }}"><br><br>

        <label>Categoría:</label><br>
        <input type="text" name="categoria" value="{{ producto['categoria'] }}"><br><br>

        <label>Stock:</label><br>
        <input type="number" name="stock" value="{{ producto['stock'] }}"><br><br>

        <label>Precio:</label><br>
        <input type="number" step="0.01" name="precio" value="{{ producto['precio'] }}"><br><br>

        <button type="submit">Actualizar</button>
    </form>
    <br>
    <a href="/productos">Volver</a>
    """
    return render_template_string(html, producto=producto)


@app.route("/producto/eliminar/<int:id_producto>")
def eliminar_producto(id_producto):
    conn = get_connection()
    conn.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
    conn.commit()
    conn.close()
    return redirect(url_for("productos"))


@app.route("/ventas")
def ventas():
    conn = get_connection()
    ventas = conn.execute("SELECT * FROM ventas").fetchall()
    conn.close()

    html = """
    <h1>Listado de Ventas</h1>
    <a href="/">Volver</a> | <a href="/venta/nueva">Nueva venta</a>
    <table border="1" cellpadding="6">
        <tr>
            <th>ID</th>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Total</th>
            <th>Fecha</th>
        </tr>
        {% for v in ventas %}
        <tr>
            <td>{{ v["id_venta"] }}</td>
            <td>{{ v["producto"] }}</td>
            <td>{{ v["cantidad"] }}</td>
            <td>{{ v["total"] }}</td>
            <td>{{ v["fecha"] }}</td>
        </tr>
        {% endfor %}
    </table>
    """
    return render_template_string(html, ventas=ventas)


@app.route("/venta/nueva", methods=["GET", "POST"])
def nueva_venta():
    if request.method == "POST":
        conn = get_connection()
        conn.execute(
            "INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
            (
                request.form["producto"],
                request.form["cantidad"],
                request.form["total"],
                request.form["fecha"]
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("ventas"))

    return """
    <h1>Registrar Venta</h1>
    <form method="post">
        <label>Producto:</label><br>
        <input type="text" name="producto"><br><br>

        <label>Cantidad:</label><br>
        <input type="number" name="cantidad"><br><br>

        <label>Total:</label><br>
        <input type="number" step="0.01" name="total"><br><br>

        <label>Fecha:</label><br>
        <input type="date" name="fecha"><br><br>

        <button type="submit">Guardar venta</button>
    </form>
    <br>
    <a href="/ventas">Volver</a>
    """


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
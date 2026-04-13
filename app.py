from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, Integer
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from openai import OpenAI

TZ_COLOMBIA = timezone(timedelta(hours=-5))

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Configuración de la base de datos (Soporta Railway y Local)
database_uri = os.getenv('DATABASE_URL', os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///montebello.db'))
# Railway usa "postgres://" pero SQLAlchemy requiere "postgresql://"
if database_uri.startswith("postgres://"):
    database_uri = database_uri.replace("postgres://", "postgresql://", 1)
# Si la URI no empieza con un esquema válido, usar SQLite como fallback
if not database_uri.startswith(("postgresql://", "postgresql+", "sqlite://", "mysql://")):
    print(f"ADVERTENCIA: DATABASE_URL inválida ('{database_uri[:30]}...'), usando SQLite.")
    database_uri = 'sqlite:///montebello.db'

# Intentar psycopg3 si psycopg2 no está disponible
if database_uri.startswith("postgresql://"):
    try:
        import psycopg2
    except ImportError:
        try:
            import psycopg
            database_uri = database_uri.replace("postgresql://", "postgresql+psycopg://", 1)
        except ImportError:
            pass

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)

# Tabla de Productos
class Producto(db.Model):
    __tablename__ = 'productos'
    id_Prod = db.Column(db.Integer, primary_key=True)
    Nom_Prod = db.Column(db.String(100), nullable=False)
    Medida = db.Column(db.String(10), nullable=False)  # sac, lbs, ata, rac, cart, uni, cub
    Id_Prov = db.Column(db.Integer, db.ForeignKey('proveedores.Id_Prov'), nullable=False)
    
    # Relación con proveedor
    proveedor = db.relationship('Proveedor', backref=db.backref('productos', lazy=True))

# Tabla de Proveedores
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    Id_Prov = db.Column(db.Integer, primary_key=True)
    Nom_Prov = db.Column(db.String(100), nullable=False)
    Num_Ced = db.Column(db.String(20), nullable=False)
    Num_Anden = db.Column(db.String(10))
    Num_Puesto = db.Column(db.String(10))

# Tabla Compras del Día
class CompraDia(db.Model):
    __tablename__ = 'compras_dia'
    Id_Lin_Comp = db.Column(db.Integer, primary_key=True)
    Id_Comp = db.Column(db.Integer, nullable=False)
    Fec_Comp = db.Column(db.Date, nullable=False, default=lambda: datetime.now(TZ_COLOMBIA).date())
    Id_Prod = db.Column(db.Integer, db.ForeignKey('productos.id_Prod'), nullable=False)
    Cant_Ped = db.Column(db.Float, nullable=False)
    Cant_Bod = db.Column(db.Float, nullable=False)
    Cant_Comp = db.Column(db.Float, nullable=False)
    Val_Pag = db.Column(db.Float, nullable=False)
    Id_Prov = db.Column(db.Integer, db.ForeignKey('proveedores.Id_Prov'), nullable=False)
    
    # Relaciones
    producto = db.relationship('Producto', backref=db.backref('compras_dia', lazy=True))
    proveedor_compra = db.relationship('Proveedor', backref=db.backref('compras_dia', lazy=True))

# Tabla Histórico de Compras
class HistoricoCompra(db.Model):
    __tablename__ = 'historico_compras'
    Id_Lin_Comp = db.Column(db.Integer, primary_key=True)
    Id_Comp = db.Column(db.Integer, nullable=False)
    Fec_Comp = db.Column(db.Date, nullable=False)
    Id_Prod = db.Column(db.Integer, db.ForeignKey('productos.id_Prod'), nullable=False)
    Cant_Ped = db.Column(db.Float, nullable=False)
    Cant_Comp = db.Column(db.Float, nullable=False)
    Cant_Bod = db.Column(db.Float, nullable=False)
    Val_Pag = db.Column(db.Float, nullable=False)
    Id_Prov = db.Column(db.Integer, db.ForeignKey('proveedores.Id_Prov'), nullable=False)
    
    # Relaciones
    producto_h = db.relationship('Producto', backref=db.backref('historico_compras', lazy=True))
    proveedor_h = db.relationship('Proveedor', backref=db.backref('historico_compras', lazy=True))

# Tabla Pedidos de Compra
class PedidoCompra(db.Model):
    __tablename__ = 'pedidos_compra'
    Id_Lin_Ped = db.Column(db.Integer, primary_key=True)
    Id_Lista = db.Column(db.Integer, nullable=False)  # ID secuencial anual
    Id_Prod = db.Column(db.Integer, db.ForeignKey('productos.id_Prod'), nullable=False)
    Cant_Ped = db.Column(db.Float, nullable=False)
    Cant_Bod = db.Column(db.Float, nullable=False)
    Fec_Ped = db.Column(db.Date, nullable=False, default=lambda: datetime.now(TZ_COLOMBIA).date())
    
    # Relaciones
    producto_pedido = db.relationship('Producto', backref=db.backref('pedidos_compra', lazy=True))

# Tabla de Medidas
class Medida(db.Model):
    __tablename__ = 'medidas'
    id_Medida = db.Column(db.Integer, primary_key=True)
    Cod_Medida = db.Column(db.String(10), nullable=False, unique=True)
    Nom_Medida = db.Column(db.String(50), nullable=False)

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

# CRUD Productos
@app.route('/productos')
def productos():
    productos = Producto.query.order_by(Producto.Nom_Prod).all()
    proveedores = Proveedor.query.all()
    medidas = Medida.query.order_by(Medida.Nom_Medida).all()
    return render_template('productos.html', productos=productos, proveedores=proveedores, medidas=medidas)

@app.route('/productos/add', methods=['POST'])
def add_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        medida = request.form.get('medida')
        id_prov = request.form.get('proveedor')
        
        if not nombre or not medida or not id_prov:
            flash('Por favor complete todos los campos obligatorios.')
            return redirect(url_for('productos'))
        
        try:
            nuevo_producto = Producto(Nom_Prod=nombre, Medida=medida, Id_Prov=id_prov)
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto agregado exitosamente!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar producto: {str(e)}')
            
        return redirect(url_for('productos'))

@app.route('/productos/edit/<int:id>', methods=['GET', 'POST'])
def edit_producto(id):
    producto = Producto.query.get_or_404(id)
    proveedores = Proveedor.query.all()
    medidas = Medida.query.order_by(Medida.Nom_Medida).all()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        medida = request.form.get('medida')
        id_prov = request.form.get('proveedor')
        
        if not nombre or not medida or not id_prov:
            flash('Por favor complete todos los campos obligatorios.')
            return render_template('edit_producto.html', producto=producto, proveedores=proveedores, medidas=medidas)
        
        try:
            producto.Nom_Prod = nombre
            producto.Medida = medida
            producto.Id_Prov = id_prov
            db.session.commit()
            flash('Producto actualizado exitosamente!')
            return redirect(url_for('productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar producto: {str(e)}')
    
    return render_template('edit_producto.html', producto=producto, proveedores=proveedores, medidas=medidas)

@app.route('/productos/delete/<int:id>')
def delete_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar: puede que el producto esté referenciado en compras o pedidos.')
    return redirect(url_for('productos'))

# CRUD Proveedores
@app.route('/proveedores')
def proveedores():
    proveedores = Proveedor.query.order_by(cast(Proveedor.Num_Anden, Integer), cast(Proveedor.Num_Puesto, Integer)).all()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/proveedores/add', methods=['POST'])
def add_proveedor():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cedula = request.form.get('cedula')
        anden = request.form.get('anden')
        puesto = request.form.get('puesto')
        
        if not nombre or not cedula:
            flash('Nombre y Cédula son campos obligatorios.')
            return redirect(url_for('proveedores'))

        if Proveedor.query.filter(Proveedor.Nom_Prov.ilike(nombre)).first():
            flash(f'El proveedor "{nombre}" ya existe.')
            return redirect(url_for('proveedores'))
            
        try:
            nuevo_proveedor = Proveedor(Nom_Prov=nombre, Num_Ced=cedula, Num_Anden=anden, Num_Puesto=puesto)
            db.session.add(nuevo_proveedor)
            db.session.commit()
            flash('Proveedor agregado exitosamente!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar proveedor: {str(e)}')
            
        return redirect(url_for('proveedores'))

@app.route('/proveedores/edit/<int:id>', methods=['GET', 'POST'])
def edit_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cedula = request.form.get('cedula')
        anden = request.form.get('anden')
        puesto = request.form.get('puesto')
        
        if not nombre or not cedula:
            flash('Nombre y Cédula son campos obligatorios.')
            return render_template('edit_proveedor.html', proveedor=proveedor)
            
        try:
            proveedor.Nom_Prov = nombre
            proveedor.Num_Ced = cedula
            proveedor.Num_Anden = anden
            proveedor.Num_Puesto = puesto
            db.session.commit()
            flash('Proveedor actualizado exitosamente!')
            return redirect(url_for('proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}')
    
    return render_template('edit_proveedor.html', proveedor=proveedor)

@app.route('/proveedores/delete/<int:id>')
def delete_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    try:
        db.session.delete(proveedor)
        db.session.commit()
        flash('Proveedor eliminado exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar: puede que el proveedor tenga productos asociados.')
    return redirect(url_for('proveedores'))

# Compras del Día
@app.route('/compras')
def compras():
    compras = CompraDia.query.all()
    productos = Producto.query.all()
    proveedores = Proveedor.query.all()
    return render_template('compras.html', compras=compras, productos=productos, proveedores=proveedores)

@app.route('/compras/add', methods=['POST'])
def add_compra():
    if request.method == 'POST':
        try:
            # Obtener el siguiente Id_Comp
            ultima_compra = CompraDia.query.order_by(CompraDia.Id_Comp.desc()).first()
            id_comp = (ultima_compra.Id_Comp + 1) if ultima_compra else 1
            
            id_prod = request.form.get('producto')
            cant_ped = float(request.form.get('cant_ped', 0))
            cant_bod = float(request.form.get('cant_bod', 0))
            cant_comp = float(request.form.get('cant_comp', 0))
            val_pag = float(request.form.get('val_pag', 0))
            
            if not id_prod:
                flash('Debe seleccionar un producto.')
                return redirect(url_for('compras'))
            
            # Obtener el proveedor del producto
            producto = Producto.query.get(id_prod)
            if not producto:
                flash('Producto no encontrado.')
                return redirect(url_for('compras'))
            
            id_prov = producto.Id_Prov
            
            nueva_compra = CompraDia(
                Id_Comp=id_comp,
                Id_Prod=id_prod,
                Cant_Ped=cant_ped,
                Cant_Bod=cant_bod,
                Cant_Comp=cant_comp,
                Val_Pag=val_pag,
                Id_Prov=id_prov
            )
            
            db.session.add(nueva_compra)
            db.session.commit()
            flash('Compra agregada exitosamente!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar compra: {str(e)}')
            
        return redirect(url_for('compras'))

@app.route('/compras/update/<int:id>', methods=['POST'])
def update_compra(id):
    compra = CompraDia.query.get_or_404(id)
    try:
        data = request.get_json()
        if 'cant_comp' in data:
            compra.Cant_Comp = float(data['cant_comp'])
        if 'val_pag' in data:
            compra.Val_Pag = float(data['val_pag'])
        db.session.commit()
        total = sum(c.Val_Pag for c in CompraDia.query.all())
        return {'ok': True, 'total': round(total, 2)}
    except Exception as e:
        db.session.rollback()
        return {'ok': False, 'error': str(e)}, 400

@app.route('/compras/delete/<int:id>')
def delete_compra(id):
    compra = CompraDia.query.get_or_404(id)
    try:
        db.session.delete(compra)
        db.session.commit()
        flash('Compra eliminada exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}')
    return redirect(url_for('compras'))

# CRUD Medidas
@app.route('/medidas')
def medidas():
    medidas = Medida.query.order_by(Medida.Nom_Medida).all()
    return render_template('medidas.html', medidas=medidas)

@app.route('/medidas/add', methods=['POST'])
def add_medida():
    cod = request.form.get('cod_medida', '').strip().lower()
    nom = request.form.get('nom_medida', '').strip()
    if not cod or not nom:
        flash('Complete todos los campos.')
        return redirect(url_for('medidas'))
    if Medida.query.filter_by(Cod_Medida=cod).first():
        flash(f'El código "{cod}" ya existe. Use otro código o edite la medida existente.')
        return redirect(url_for('medidas'))
    try:
        db.session.add(Medida(Cod_Medida=cod, Nom_Medida=nom))
        db.session.commit()
        flash('Medida agregada exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}')
    return redirect(url_for('medidas'))

@app.route('/medidas/edit/<int:id>', methods=['GET', 'POST'])
def edit_medida(id):
    medida = Medida.query.get_or_404(id)
    if request.method == 'POST':
        cod = request.form.get('cod_medida', '').strip().lower()
        nom = request.form.get('nom_medida', '').strip()
        if not cod or not nom:
            flash('Complete todos los campos.')
            return render_template('edit_medida.html', medida=medida)
        try:
            medida.Cod_Medida = cod
            medida.Nom_Medida = nom
            db.session.commit()
            flash('Medida actualizada!')
            return redirect(url_for('medidas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
    return render_template('edit_medida.html', medida=medida)

@app.route('/medidas/delete/<int:id>')
def delete_medida(id):
    medida = Medida.query.get_or_404(id)
    try:
        db.session.delete(medida)
        db.session.commit()
        flash('Medida eliminada!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}')
    return redirect(url_for('medidas'))

# Histórico de Compras
@app.route('/historico')
def historico():
    historico = HistoricoCompra.query.order_by(HistoricoCompra.Id_Comp.desc(), HistoricoCompra.Id_Lin_Comp).all()
    return render_template('historico.html', historico=historico)

# Mover compras del día a histórico
@app.route('/mover_historico')
def mover_historico():
    try:
        compras_hoy = CompraDia.query.all()
        
        if not compras_hoy:
            flash('No hay compras para mover al histórico.')
            return redirect(url_for('compras'))
            
        for compra in compras_hoy:
            historico_registro = HistoricoCompra(
                Id_Comp=compra.Id_Comp,
                Fec_Comp=compra.Fec_Comp,
                Id_Prod=compra.Id_Prod,
                Cant_Ped=compra.Cant_Ped,
                Cant_Comp=compra.Cant_Comp,
                Cant_Bod=compra.Cant_Bod,
                Val_Pag=compra.Val_Pag,
                Id_Prov=compra.Id_Prov
            )
            db.session.add(historico_registro)
        
        CompraDia.query.delete()
        db.session.commit()
        flash('Compras movidas al histórico exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al mover al histórico: {str(e)}')
        
    return redirect(url_for('compras'))

# Pedidos de Compra
@app.route('/pedidos')
def pedidos():
    pedidos = PedidoCompra.query.order_by(PedidoCompra.Id_Lista.desc()).all()
    productos = Producto.query.all()
    return render_template('pedidos.html', pedidos=pedidos, productos=productos)

@app.route('/pedidos/add', methods=['POST'])
def add_pedido():
    if request.method == 'POST':
        try:
            # Obtener el siguiente Id_Lista secuencial para el año actual
            año_actual = datetime.now().year
            ultimo_pedido = PedidoCompra.query.filter(
                db.extract('year', PedidoCompra.Fec_Ped) == año_actual
            ).order_by(PedidoCompra.Id_Lista.desc()).first()
            
            id_lista = (ultimo_pedido.Id_Lista + 1) if ultimo_pedido else 1
            
            id_prod = request.form.get('producto')
            # Si el campo está vacío, se asigna 0.0 automáticamente
            try:
                cant_ped = float(request.form.get('cant_ped') or 0)
                cant_bod = float(request.form.get('cant_bod') or 0)
            except ValueError:
                flash('Las cantidades deben ser valores numéricos.')
                return redirect(url_for('pedidos'))
            
            if not id_prod:
                flash('Debe seleccionar un producto.')
                return redirect(url_for('pedidos'))
                
            nuevo_pedido = PedidoCompra(
                Id_Lista=id_lista,
                Id_Prod=id_prod,
                Cant_Ped=cant_ped,
                Cant_Bod=cant_bod
            )
            
            db.session.add(nuevo_pedido)
            db.session.commit()
            flash('Pedido agregado exitosamente!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar pedido: {str(e)}')
            
        return redirect(url_for('pedidos'))

@app.route('/pedidos/delete/<int:id>')
def delete_pedido(id):
    pedido = PedidoCompra.query.get_or_404(id)
    try:
        db.session.delete(pedido)
        db.session.commit()
        flash('Pedido eliminado exitosamente!')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}')
    return redirect(url_for('pedidos'))

@app.route('/transferir_pedidos')
def transferir_pedidos():
    try:
        pedidos_pendientes = PedidoCompra.query.all()
        
        if not pedidos_pendientes:
            flash('No hay pedidos pendientes para transferir.')
            return redirect(url_for('compras'))
        
        # Si ya hay compras hoy, reutilizar el mismo Id_Comp (es la misma compra del día)
        hoy = datetime.now(TZ_COLOMBIA).date()
        compra_hoy = CompraDia.query.filter_by(Fec_Comp=hoy).first()
        
        if compra_hoy:
            id_comp = compra_hoy.Id_Comp
        else:
            ultima_compra_dia = CompraDia.query.order_by(CompraDia.Id_Comp.desc()).first()
            ultimo_historico = HistoricoCompra.query.order_by(HistoricoCompra.Id_Comp.desc()).first()
            id_max_dia = ultima_compra_dia.Id_Comp if ultima_compra_dia else 0
            id_max_hist = ultimo_historico.Id_Comp if ultimo_historico else 0
            id_comp = max(id_max_dia, id_max_hist) + 1
        
        transferidos = 0
        for pedido in pedidos_pendientes:
            producto = Producto.query.get(pedido.Id_Prod)
            if not producto:
                continue
                
            id_prov = producto.Id_Prov
            nueva_compra = CompraDia(
                Id_Comp=id_comp, # Se usa el mismo Id_Comp para todos los productos de esta transferencia
                Id_Prod=pedido.Id_Prod,
                Cant_Ped=pedido.Cant_Ped,
                Cant_Bod=pedido.Cant_Bod,
                Cant_Comp=0,
                Val_Pag=0,
                Id_Prov=id_prov
            )
            db.session.add(nueva_compra)
            transferidos += 1
        
        PedidoCompra.query.delete()
        db.session.commit()
        flash(f'Se han transferido {transferidos} pedidos a la Compra Num: {id_comp}.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al transferir pedidos: {str(e)}')
        
    return redirect(url_for('compras'))

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f'Advertencia al crear tablas: {e}')


@app.route('/consultas-ia', methods=['GET', 'POST'])
def consultas_ia():
    respuesta = None
    error = None
    pregunta = None
    if request.method == 'POST':
        pregunta = request.form.get('pregunta', '').strip()
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                error = 'No se encontró la API Key de OpenRouter.'
            else:
                client = OpenAI(
                    base_url='https://openrouter.ai/api/v1',
                    api_key=api_key
                )

                historico = HistoricoCompra.query.order_by(HistoricoCompra.Fec_Comp.desc()).limit(100).all()
                compras_hoy = CompraDia.query.all()

                contexto = "Datos de compras del día actual (pendientes de confirmar valores):\n"
                for r in compras_hoy:
                    contexto += f"- Comp={r.Id_Comp}, Fecha={r.Fec_Comp}, Producto={r.producto.Nom_Prod} ({r.producto.Medida}), cant_pedida={r.Cant_Ped}, cant_comprada={r.Cant_Comp}, valor=${r.Val_Pag}, proveedor={r.proveedor_compra.Nom_Prov}\n"
                contexto += "\nHistórico de compras anteriores:\n"
                for r in historico:
                    contexto += f"- Comp={r.Id_Comp}, Fecha={r.Fec_Comp}, Producto={r.producto_h.Nom_Prod} ({r.producto_h.Medida}), cant_pedida={r.Cant_Ped}, cant_comprada={r.Cant_Comp}, valor=${r.Val_Pag}, proveedor={r.proveedor_h.Nom_Prov}\n"

                sistema = (
                    "Eres un asistente de una app de compras de mercado. "
                    "Responde SIEMPRE en español, de forma clara y concisa. "
                    "El campo 'Id_Comp' o 'Comp' es el número de compra que agrupa todos los productos comprados en una misma salida al mercado. "
                    "Nunca mezcles otros idiomas. No incluyas explicaciones técnicas ni notas al pie."
                )
                prompt = f"{contexto}\nPregunta: {pregunta}"
                response = client.chat.completions.create(
                    model='deepseek/deepseek-chat-v3-0324',
                    messages=[
                        {'role': 'system', 'content': sistema},
                        {'role': 'user', 'content': prompt}
                    ]
                )
                respuesta = response.choices[0].message.content
        except Exception as e:
            error = f'Error al consultar IA: {str(e)}'
    return render_template('consultas_ia.html', respuesta=respuesta, error=error, pregunta=pregunta)

if __name__ == '__main__':
    # Railway asigna el puerto automáticamente en la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host='0.0.0.0', port=port)


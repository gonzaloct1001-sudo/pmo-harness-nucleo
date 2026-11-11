"""Modelos de análisis: fórmulas de negocio con nombre, entradas y resultados, sobre las que `simular.py` corre
escenarios, sensibilidad y simulación. Cada modelo es una función pura (mismas entradas, mismo resultado).

Fracciones como fracción (0,05 = 5 %); montos en la moneda del proyecto. Un resultado que no se puede calcular con
esas entradas (por ejemplo, una baja de precio mayor que el margen) vale `None` y el simulador lo cuenta aparte.
También está la evaluación segura de una fórmula propia (`modelo: formula`), que solo admite aritmética, comparaciones
y unas pocas funciones: nada de nombres con punto, índices ni llamadas a otra cosa.
"""
import ast
import math

FUNCIONES = {"min": min, "max": max, "abs": abs, "round": round, "sqrt": math.sqrt, "ceil": math.ceil, "floor": math.floor}
NODOS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load, ast.Call, ast.Compare, ast.BoolOp, ast.IfExp,
         ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv, ast.UAdd, ast.USub, ast.And, ast.Or, ast.Not,
         ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)


class FormulaInvalida(ValueError):
    pass


def compilar(formula):
    """(código listo para evaluar, nombres que usa) de una fórmula propia. Lanza FormulaInvalida si trae algo que no
    sea aritmética, comparaciones, `a if condición else b` o las funciones min, max, abs, round, sqrt, ceil y floor."""
    try:
        arbol = ast.parse(str(formula).strip(), mode="eval")
    except SyntaxError as e:
        raise FormulaInvalida(f"la fórmula «{formula}» no se entiende ({e.msg})")
    nombres = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, NODOS):
            raise FormulaInvalida(f"la fórmula «{formula}» usa algo no permitido ({type(nodo).__name__}): solo números, nombres "
                                  "de entradas, + - * / ** %, comparaciones, `a if c else b` y min, max, abs, round, sqrt, ceil, floor")
        if isinstance(nodo, ast.Constant) and not isinstance(nodo.value, (int, float)):
            raise FormulaInvalida(f"la fórmula «{formula}» solo admite números")
        if isinstance(nodo, ast.Call) and (not isinstance(nodo.func, ast.Name) or nodo.func.id not in FUNCIONES or nodo.keywords):
            raise FormulaInvalida(f"la fórmula «{formula}» llama a una función no permitida")
        if isinstance(nodo, ast.Name) and nodo.id not in FUNCIONES and nodo.id not in nombres:
            nombres.append(nodo.id)
    return compile(arbol, "<formula>", "eval"), nombres


def evaluar(codigo, valores):
    """Valor de una fórmula ya compilada con esos valores; None si no se puede calcular (división por cero, raíz negativa)."""
    try:
        v = eval(codigo, {"__builtins__": {}}, {**FUNCIONES, **valores})  # el árbol ya fue validado nodo por nodo
        v = float(v)
        return v if math.isfinite(v) else None
    except (ZeroDivisionError, ValueError, OverflowError, TypeError):
        return None


def _div(a, b):
    return a / b if b else None


# --------------------------------------------------------------------------------------------- los cinco modelos
def precio_volumen(e):
    m, p, a = e["margen"], e["cambio_precio"], e.get("perdida_volumen", 0.0)
    unitario = m + p  # margen por cada $1 del precio original, después del cambio
    equilibrio = _div(-p, unitario) if unitario > 0 else None
    total = unitario * (1 - a) / m - 1 if m > 0 else None
    reponer = max(0.0, m / unitario - (1 - a)) if unitario > 0 else None
    return {"cambio_margen_total": total, "volumen_de_equilibrio": equilibrio, "clientes_a_reponer": reponer,
            "margen_bruto_nuevo": e.get("ventas", 0.0) * unitario * (1 - a) if e.get("ventas") else None}


def equilibrio(e):
    meta = e["gastos_fijos"] + e.get("retiro_objetivo", 0.0) + e.get("contrataciones", 0.0) + e.get("gastos_nuevos", 0.0)
    ventas = _div(meta, e["margen"]) if e["margen"] > 0 else None
    transacciones = _div(meta, e["margen_por_transaccion"]) if e.get("margen_por_transaccion", 0) > 0 else None
    clientes = _div(transacciones, e["frecuencia"]) if transacciones is not None and e.get("frecuencia", 0) > 0 else None
    holgura = e["ventas_esperadas"] * e["margen"] - meta if e.get("ventas_esperadas") is not None else None
    return {"holgura": holgura, "gasto_meta": meta, "ventas_necesarias": ventas, "transacciones_necesarias": transacciones,
            "clientes_necesarios": clientes}


def palancas(e):
    bruto = e["clientes"] * e["frecuencia"] * e["margen_por_transaccion"]
    return {"margen_bruto": bruto, "resultado": bruto - e.get("gastos_fijos", 0.0)}


def caja_crecimiento(e):
    ct = _div(e.get("cuentas_por_cobrar", 0.0) + e.get("inventario", 0.0) + e.get("trabajo_en_curso", 0.0), e["ventas_anuales"])
    m = e["margen"]
    return {"caja_que_pide_crecer": ct * e.get("aumento_ventas", 0.0) if ct is not None else None,
            "capital_de_trabajo_sobre_ventas": ct,
            "meses_para_recuperar": 12 * ct / m if ct is not None and m > 0 else None,
            "rendimiento_anual_del_capital": _div(m, ct) if ct else None}


def crecimiento_sostenible(e):
    neto = e["activos_sobre_ventas"] - e.get("pasivos_espontaneos_sobre_ventas", 0.0)  # capital que pide cada $1 de venta nueva
    autofinanciado = e["margen_neto"] * e["retencion"]
    g, v0 = e.get("crecimiento_planeado", 0.0), e["ventas"]
    necesidad = neto * g * v0 - autofinanciado * v0 * (1 + g)
    sostenible = _div(autofinanciado, neto - autofinanciado) if neto - autofinanciado > 0 else None
    return {"necesidad_de_financiamiento": necesidad, "crecimiento_sostenible": sostenible,
            "holgura_de_crecimiento": sostenible - g if sostenible is not None else None}


def _en(que, unidad="", opcional=False):
    return {"que": que, "unidad": unidad, "opcional": opcional}


MODELOS = {
    "precio-volumen": {
        "nombre": "Precio y volumen", "calcular": precio_volumen, "principal": "cambio_margen_total",
        "para_que": "¿Conviene cambiar el precio? Cuánto volumen se puede perder (o hay que ganar) para quedar igual, y cómo "
                    "queda el margen bruto total si se pierde una parte de las ventas.",
        "entradas": {"margen": _en("Margen bruto actual sobre el precio", "fracción"),
                     "cambio_precio": _en("Cambio de precio: positivo sube, negativo baja", "fracción"),
                     "perdida_volumen": _en("Parte del volumen que se pierde por el cambio (negativa si se gana)", "fracción", True),
                     "ventas": _en("Ventas actuales, para ver el margen en dinero", "monto", True)},
        "resultados": {"cambio_margen_total": ("Cambio del margen bruto total", "fracción"),
                       "volumen_de_equilibrio": ("Cambio de volumen que deja el margen bruto igual", "fracción"),
                       "clientes_a_reponer": ("Clientes nuevos necesarios para quedar igual, como parte de la base", "fracción"),
                       "margen_bruto_nuevo": ("Margen bruto total después del cambio", "monto")},
        "notas": ["Supone que el costo por unidad no cambia con el volumen.",
                  "La pérdida de volumen es el supuesto que decide: conviene medirla con una prueba en un segmento antes de aplicarla a todos."]},
    "equilibrio": {
        "nombre": "Punto de equilibrio con meta", "calcular": equilibrio, "principal": "holgura",
        "para_que": "Cuánto hay que vender para cubrir los gastos más lo que se quiere retirar, contratar o gastar de nuevo; "
                    "con las ventas esperadas, qué tan probable es cubrirlo.",
        "entradas": {"gastos_fijos": _en("Gastos fijos del período", "monto"),
                     "margen": _en("Margen bruto sobre las ventas", "fracción"),
                     "retiro_objetivo": _en("Retiro o sueldo de los dueños que se quiere cubrir", "monto", True),
                     "contrataciones": _en("Costo de las contrataciones planeadas", "monto", True),
                     "gastos_nuevos": _en("Otros gastos nuevos", "monto", True),
                     "ventas_esperadas": _en("Ventas esperadas del período (para la holgura)", "monto", True),
                     "margen_por_transaccion": _en("Margen bruto promedio por venta", "monto", True),
                     "frecuencia": _en("Ventas por cliente en el período", "veces", True)},
        "resultados": {"holgura": ("Margen bruto esperado menos el gasto meta", "monto"),
                       "gasto_meta": ("Gasto total a cubrir", "monto"),
                       "ventas_necesarias": ("Ventas que cubren el gasto meta", "monto"),
                       "transacciones_necesarias": ("Ventas (en número) que cubren el gasto meta", "veces"),
                       "clientes_necesarios": ("Clientes activos que cubren el gasto meta", "clientes")},
        "notas": ["Si el volumen crece, parte de los gastos fijos sube por escalones: revísalos antes de dar por buena la meta."]},
    "palancas": {
        "nombre": "Palancas del margen", "calcular": palancas, "principal": "margen_bruto",
        "para_que": "El margen bruto como clientes × frecuencia × margen por venta: cuál de las tres pesa más y cuánto "
                    "tendría que moverse cada una sola para llegar a una meta.",
        "entradas": {"clientes": _en("Clientes activos", "clientes"),
                     "frecuencia": _en("Ventas por cliente en el período", "veces"),
                     "margen_por_transaccion": _en("Margen bruto promedio por venta", "monto"),
                     "gastos_fijos": _en("Gastos fijos, para ver el resultado", "monto", True)},
        "resultados": {"margen_bruto": ("Margen bruto total", "monto"), "resultado": ("Margen bruto menos gastos fijos", "monto")},
        "notas": ["Más clientes o más frecuencia suelen pedir más gasto y más capital de trabajo; subir el margen por venta no, "
                  "pero puede bajar las otras dos."]},
    "caja-crecimiento": {
        "nombre": "Caja que pide crecer", "calcular": caja_crecimiento, "principal": "caja_que_pide_crecer",
        "para_que": "Cuánta caja hay que poner por adelantado para vender más, en cuántos meses vuelve y cuánto rinde después.",
        "entradas": {"ventas_anuales": _en("Ventas de doce meses", "monto"),
                     "margen": _en("Margen bruto (o de contribución) sobre las ventas", "fracción"),
                     "cuentas_por_cobrar": _en("Cuentas por cobrar promedio", "monto", True),
                     "inventario": _en("Inventario promedio", "monto", True),
                     "trabajo_en_curso": _en("Trabajo hecho y aún no facturado, promedio", "monto", True),
                     "aumento_ventas": _en("Aumento de ventas anuales que se busca", "monto", True)},
        "resultados": {"caja_que_pide_crecer": ("Caja inicial que pide ese aumento de ventas", "monto"),
                       "capital_de_trabajo_sobre_ventas": ("Capital de trabajo por cada $1 de venta anual", "fracción"),
                       "meses_para_recuperar": ("Meses de margen que devuelven ese capital", "meses"),
                       "rendimiento_anual_del_capital": ("Margen anual por cada $1 de capital de trabajo", "fracción")},
        "notas": ["El capital de trabajo es un saldo y el margen es un flujo anual: se comparan en meses para recuperar, no uno contra otro."]},
    "crecimiento-sostenible": {
        "nombre": "Crecimiento sostenible", "calcular": crecimiento_sostenible, "principal": "necesidad_de_financiamiento",
        "para_que": "Cuánto puede crecer la empresa con lo que ella misma genera, y cuánto financiamiento pide el crecimiento planeado.",
        "entradas": {"ventas": _en("Ventas del último año", "monto"),
                     "activos_sobre_ventas": _en("Activos que crecen con la venta, por cada $1 de venta", "fracción"),
                     "margen_neto": _en("Utilidad neta sobre ventas", "fracción"),
                     "retencion": _en("Parte de la utilidad que queda en la empresa después de retiros y amortización de deuda", "fracción"),
                     "pasivos_espontaneos_sobre_ventas": _en("Pasivos que crecen solos con la venta (proveedores), por cada $1 de venta", "fracción", True),
                     "crecimiento_planeado": _en("Crecimiento de ventas que se quiere", "fracción", True)},
        "resultados": {"necesidad_de_financiamiento": ("Financiamiento externo que pide el crecimiento planeado (negativo = sobra)", "monto"),
                       "crecimiento_sostenible": ("Crecimiento que se financia solo", "fracción"),
                       "holgura_de_crecimiento": ("Crecimiento sostenible menos el planeado", "fracción")},
        "notas": ["Supone que activos, pasivos espontáneos y margen mantienen su proporción con las ventas."]},
}


def calcular(modelo, entradas):
    """Resultados de un modelo de la biblioteca con esas entradas (las opcionales que falten usan su valor neutro)."""
    return MODELOS[modelo]["calcular"](entradas)

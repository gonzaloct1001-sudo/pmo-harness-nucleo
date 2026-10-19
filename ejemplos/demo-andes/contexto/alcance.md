# Alcance del programa (FICTICIO)

## Objetivo
Reemplazar el sistema de gestión actual y digitalizar el despacho, para reducir errores de facturación y
dar visibilidad en línea del estado de los pedidos a clientes y gerencia.

## Subproyectos / módulos
| Código | Nombre | Descripción | Responsable |
|---|---|---|---|
| SP0 | Gestión | Gestión transversal del programa | Jefa de Programa (demo) |
| SP1 | ERP | Implementación y migración al nuevo ERP | Andrés Muñoz |
| SP2 | App de despacho | App móvil para choferes y control de entregas | Tomás Fuentes |
| SP3 | Integración y BI | Integraciones ERP–app y tableros de gestión | Andrés Muñoz |
| SP4 | Portal de clientes | Seguimiento de pedidos para clientes (incorporado por enmienda E01) | Tomás Fuentes |

## Dependencias entre subproyectos
- SP3 (desarrollo de integraciones) requiere ERP en producción (SP1) y piloto de la app terminado (SP2).
- SP4 requiere el diseño de integración de SP3.

## Entregables principales
- ERP en producción (hito, 15-01-2027).
- App móvil en piloto con 20 choferes.
- Tableros BI de ventas y despacho.
- Portal de clientes en producción.

## Fuera de alcance
- Migración de datos históricos anteriores a 2022.
- Integración con sistemas de proveedores.

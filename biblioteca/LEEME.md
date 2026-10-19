# Biblioteca de perfiles

Un **perfil** es el diseño de un tipo de proyecto que ya hiciste y quieres reutilizar
(ej.: "obra de vivienda", "granja de bots", "evaluación de fondo X"). No es parte del núcleo: es tu biblioteca.

## Estructura
```
biblioteca/perfiles/<nombre>/
├── PERFIL.md       qué es, arquetipos que usa, cuándo usarlo, preguntas a hacer al crear un proyecto
└── estructura/     archivos que se copian al proyecto nuevo (sin sobrescribir)
    ├── metricas/metricas.yaml
    ├── items/etapas.yaml
    ├── scripts/...
    └── reportes/catalogo/...
```
Los perfiles **no** llevan datos de un proyecto real (ni mediciones, ni ítems, ni documentos): solo el diseño.

## Uso
- Crear: al terminar `nuevo-proyecto`, pide "guarda este diseño como perfil <nombre>".
- Usar: `nuevo-proyecto` ofrece los perfiles que calcen con lo que describes, o
  `python herramientas/crear_proyecto.py <slug> --arquetipos <a> --perfil biblioteca/perfiles/<nombre>`.

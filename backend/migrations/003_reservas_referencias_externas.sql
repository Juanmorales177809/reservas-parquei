-- Ejecutar DESPUÉS de que los módulos Resources y Researchs creen sus tablas.
-- Solo altera tablas de reservas. Ante una dependencia ausente revierte todo.
BEGIN;
SET LOCAL lock_timeout = '5s';
ALTER TABLE reservas.reserva_recursos
  ADD CONSTRAINT fk_reserva_recursos_catalogo FOREIGN KEY (recurso_id) REFERENCES recursos.recursos(id),
  DROP CONSTRAINT pendiente_fk_recursos;
ALTER TABLE reservas.espacio_recursos
  ADD CONSTRAINT fk_espacio_recursos_catalogo FOREIGN KEY (recurso_id) REFERENCES recursos.recursos(id),
  DROP CONSTRAINT pendiente_fk_recursos;
ALTER TABLE reservas.reserva_contexto
  ADD CONSTRAINT fk_reserva_contexto_pasantia FOREIGN KEY (pasantia_id) REFERENCES investigacion.pasantias(id_pasantia),
  ADD CONSTRAINT fk_reserva_contexto_trabajo FOREIGN KEY (trabajo_grado_id) REFERENCES investigacion.trabajos_grado(id_trabajo_grado),
  ADD CONSTRAINT fk_reserva_contexto_actividad FOREIGN KEY (actividad_institucional_id) REFERENCES investigacion.actividades_institucionales(id_actividad),
  DROP CONSTRAINT pendiente_fk_pasantias,
  DROP CONSTRAINT pendiente_fk_trabajos_grado,
  DROP CONSTRAINT pendiente_fk_actividades;
COMMIT;

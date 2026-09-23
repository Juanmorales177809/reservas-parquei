-- Ejecutar dentro de una transacción y revertir al terminar.
DO $$
DECLARE t text; actual text[];
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'tipos_reserva','estados_reserva','laboratorio_tipos_reserva','reservas',
    'reserva_espacio','reserva_acompanantes','reserva_recurso_interno',
    'reserva_recurso_campus','reserva_recurso_externo','reserva_lista_espera',
    'reserva_lista_espera_formulario','reserva_recursos','reserva_contexto',
    'reserva_campos_valores','reserva_adjuntos','reserva_ejecucion_recursos',
    'reserva_datos_salida','ordenes_salida','orden_salida_actividades',
    'orden_salida_items','reserva_propuestas','reserva_historial_estado',
    'espacios','espacio_campos','espacio_campo_opciones','espacio_recursos',
    'laboratorios_config','laboratorios_config_historico'
  ] LOOP
    IF to_regclass('reservas.' || t) IS NULL THEN RAISE EXCEPTION 'Falta tabla %', t; END IF;
  END LOOP;
  FOREACH t IN ARRAY ARRAY['motivos_solicitud','reserva_equipos','reserva_mobiliarios',
    'reserva_otros','control_cambios','notificaciones','mobiliarios','otros'] LOOP
    IF to_regclass('reservas.' || t) IS NOT NULL THEN RAISE EXCEPTION 'Sobra tabla %', t; END IF;
  END LOOP;
  SELECT array_agg(column_name::text ORDER BY column_name) INTO actual
    FROM information_schema.columns WHERE table_schema='reservas' AND table_name='reservas';
  IF actual <> ARRAY['created_at','created_by','estado_id','fecha_aprobacion','fecha_cancelacion',
    'id','id_cuenta','id_unidad','motivo_cancelacion','observacion','requiere_apoyo','tipo_reserva_id','updated_at']
    THEN RAISE EXCEPTION 'Cabecera incorrecta: %', actual; END IF;
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE connamespace='reservas'::regnamespace AND contype='f' AND confdeltype <> 'a')
    THEN RAISE EXCEPTION 'Hay FK que eliminan/modifican referencias históricas'; END IF;
  IF (SELECT count(*) FROM pg_constraint WHERE connamespace='reservas'::regnamespace AND conname LIKE 'pendiente_fk_%') <> 5
    THEN RAISE EXCEPTION 'Faltan restricciones de dependencias externas'; END IF;

  BEGIN
    INSERT INTO reservas.reserva_recurso_interno VALUES (-1, current_date, '12:00', '11:00');
    RAISE EXCEPTION 'Se aceptó horario invertido';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
    INSERT INTO reservas.reserva_recurso_campus VALUES (-1, current_date, current_date - 1);
    RAISE EXCEPTION 'Se aceptó devolución anterior a salida';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
    INSERT INTO reservas.reserva_contexto(reserva_id) VALUES (-1);
    RAISE EXCEPTION 'Se aceptó contexto vacío';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
    INSERT INTO reservas.reserva_contexto(reserva_id, proyecto_id, actividad_institucional_id) VALUES (-1,-1,-1);
    RAISE EXCEPTION 'Se aceptó contexto incompatible';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
    INSERT INTO reservas.reserva_recursos(id,reserva_id,recurso_id,rol,estado_asignacion) VALUES (-1,-1,-1,'PRINCIPAL','ASIGNADO');
    RAISE EXCEPTION 'Se aceptó recurso sin catálogo externo';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
    INSERT INTO reservas.reserva_adjuntos(id,reserva_id,tipo_adjunto,nombre_original,storage_key,content_type,size_bytes,uploaded_by)
      VALUES (-1,-1,'DOCUMENTO','prueba.pdf','prueba','application/pdf',5242881,-1);
    RAISE EXCEPTION 'Se aceptó adjunto mayor de 5 MB';
  EXCEPTION WHEN check_violation THEN NULL; END;
  INSERT INTO reservas.estados_reserva(id,codigo,nombre,habilitado) VALUES (-1,'PRUEBA','Prueba temporal',true);
  BEGIN
    INSERT INTO reservas.estados_reserva(id,codigo,nombre,habilitado) VALUES (-2,'PRUEBA','Duplicado',true);
    RAISE EXCEPTION 'Se aceptó código de estado duplicado';
  EXCEPTION WHEN unique_violation THEN NULL; END;
  RAISE NOTICE 'Verificados: 28 tablas, cabecera, FK, dependencias y restricciones básicas';
END $$;

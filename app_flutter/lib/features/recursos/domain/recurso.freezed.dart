// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'recurso.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Recurso {

 int get id; String get nombre; int get laboratorioId; int get tipoRecursoId; String? get descripcion; int get capacidad; EstadoEntidad get estado; Laboratorio get laboratorio; TipoRecurso get tipo; bool get esPrestacionServicio; bool get requiereApoyoAuxiliar;
/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecursoCopyWith<Recurso> get copyWith => _$RecursoCopyWithImpl<Recurso>(this as Recurso, _$identity);

  /// Serializes this Recurso to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Recurso&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.tipoRecursoId, tipoRecursoId) || other.tipoRecursoId == tipoRecursoId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.esPrestacionServicio, esPrestacionServicio) || other.esPrestacionServicio == esPrestacionServicio)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,laboratorioId,tipoRecursoId,descripcion,capacidad,estado,laboratorio,tipo,esPrestacionServicio,requiereApoyoAuxiliar);

@override
String toString() {
  return 'Recurso(id: $id, nombre: $nombre, laboratorioId: $laboratorioId, tipoRecursoId: $tipoRecursoId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado, laboratorio: $laboratorio, tipo: $tipo, esPrestacionServicio: $esPrestacionServicio, requiereApoyoAuxiliar: $requiereApoyoAuxiliar)';
}


}

/// @nodoc
abstract mixin class $RecursoCopyWith<$Res>  {
  factory $RecursoCopyWith(Recurso value, $Res Function(Recurso) _then) = _$RecursoCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int laboratorioId, int tipoRecursoId, String? descripcion, int capacidad, EstadoEntidad estado, Laboratorio laboratorio, TipoRecurso tipo, bool esPrestacionServicio, bool requiereApoyoAuxiliar
});


$LaboratorioCopyWith<$Res> get laboratorio;$TipoRecursoCopyWith<$Res> get tipo;

}
/// @nodoc
class _$RecursoCopyWithImpl<$Res>
    implements $RecursoCopyWith<$Res> {
  _$RecursoCopyWithImpl(this._self, this._then);

  final Recurso _self;
  final $Res Function(Recurso) _then;

/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? laboratorioId = null,Object? tipoRecursoId = null,Object? descripcion = freezed,Object? capacidad = null,Object? estado = null,Object? laboratorio = null,Object? tipo = null,Object? esPrestacionServicio = null,Object? requiereApoyoAuxiliar = null,}) {
  return _then(Recurso(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,tipoRecursoId: null == tipoRecursoId ? _self.tipoRecursoId : tipoRecursoId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: null == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as Laboratorio,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoRecurso,esPrestacionServicio: null == esPrestacionServicio ? _self.esPrestacionServicio : esPrestacionServicio // ignore: cast_nullable_to_non_nullable
as bool,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioCopyWith<$Res> get laboratorio {
  
  return $LaboratorioCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TipoRecursoCopyWith<$Res> get tipo {
  
  return $TipoRecursoCopyWith<$Res>(_self.tipo, (value) {
    return _then(_self.copyWith(tipo: value));
  });
}
}


/// Adds pattern-matching-related methods to [Recurso].
extension RecursoPatterns on Recurso {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Recurso value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Recurso() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Recurso value)  $default,){
final _that = this;
switch (_that) {
case _Recurso():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Recurso value)?  $default,){
final _that = this;
switch (_that) {
case _Recurso() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int laboratorioId,  int tipoRecursoId,  String? descripcion,  int capacidad,  EstadoEntidad estado,  Laboratorio laboratorio,  TipoRecurso tipo,  bool esPrestacionServicio,  bool requiereApoyoAuxiliar)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Recurso() when $default != null:
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.tipoRecursoId,_that.descripcion,_that.capacidad,_that.estado,_that.laboratorio,_that.tipo,_that.esPrestacionServicio,_that.requiereApoyoAuxiliar);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int laboratorioId,  int tipoRecursoId,  String? descripcion,  int capacidad,  EstadoEntidad estado,  Laboratorio laboratorio,  TipoRecurso tipo,  bool esPrestacionServicio,  bool requiereApoyoAuxiliar)  $default,) {final _that = this;
switch (_that) {
case _Recurso():
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.tipoRecursoId,_that.descripcion,_that.capacidad,_that.estado,_that.laboratorio,_that.tipo,_that.esPrestacionServicio,_that.requiereApoyoAuxiliar);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int laboratorioId,  int tipoRecursoId,  String? descripcion,  int capacidad,  EstadoEntidad estado,  Laboratorio laboratorio,  TipoRecurso tipo,  bool esPrestacionServicio,  bool requiereApoyoAuxiliar)?  $default,) {final _that = this;
switch (_that) {
case _Recurso() when $default != null:
return $default(_that.id,_that.nombre,_that.laboratorioId,_that.tipoRecursoId,_that.descripcion,_that.capacidad,_that.estado,_that.laboratorio,_that.tipo,_that.esPrestacionServicio,_that.requiereApoyoAuxiliar);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Recurso implements Recurso {
  const _Recurso({required this.id, required this.nombre, required this.laboratorioId, required this.tipoRecursoId, this.descripcion, required this.capacidad, required this.estado, required this.laboratorio, required this.tipo, required this.esPrestacionServicio, this.requiereApoyoAuxiliar = false});
  factory _Recurso.fromJson(Map<String, dynamic> json) => _$RecursoFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int laboratorioId;
@override final  int tipoRecursoId;
@override final  String? descripcion;
@override final  int capacidad;
@override final  EstadoEntidad estado;
@override final  Laboratorio laboratorio;
@override final  TipoRecurso tipo;
@override final  bool esPrestacionServicio;
@override@JsonKey() final  bool requiereApoyoAuxiliar;

/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecursoCopyWith<_Recurso> get copyWith => __$RecursoCopyWithImpl<_Recurso>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecursoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Recurso&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.tipoRecursoId, tipoRecursoId) || other.tipoRecursoId == tipoRecursoId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.laboratorio, laboratorio) || other.laboratorio == laboratorio)&&(identical(other.tipo, tipo) || other.tipo == tipo)&&(identical(other.esPrestacionServicio, esPrestacionServicio) || other.esPrestacionServicio == esPrestacionServicio)&&(identical(other.requiereApoyoAuxiliar, requiereApoyoAuxiliar) || other.requiereApoyoAuxiliar == requiereApoyoAuxiliar));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,laboratorioId,tipoRecursoId,descripcion,capacidad,estado,laboratorio,tipo,esPrestacionServicio,requiereApoyoAuxiliar);

@override
String toString() {
  return 'Recurso(id: $id, nombre: $nombre, laboratorioId: $laboratorioId, tipoRecursoId: $tipoRecursoId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado, laboratorio: $laboratorio, tipo: $tipo, esPrestacionServicio: $esPrestacionServicio, requiereApoyoAuxiliar: $requiereApoyoAuxiliar)';
}


}

/// @nodoc
abstract mixin class _$RecursoCopyWith<$Res> implements $RecursoCopyWith<$Res> {
  factory _$RecursoCopyWith(_Recurso value, $Res Function(_Recurso) _then) = __$RecursoCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int laboratorioId, int tipoRecursoId, String? descripcion, int capacidad, EstadoEntidad estado, Laboratorio laboratorio, TipoRecurso tipo, bool esPrestacionServicio, bool requiereApoyoAuxiliar
});


@override $LaboratorioCopyWith<$Res> get laboratorio;@override $TipoRecursoCopyWith<$Res> get tipo;

}
/// @nodoc
class __$RecursoCopyWithImpl<$Res>
    implements _$RecursoCopyWith<$Res> {
  __$RecursoCopyWithImpl(this._self, this._then);

  final _Recurso _self;
  final $Res Function(_Recurso) _then;

/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? laboratorioId = null,Object? tipoRecursoId = null,Object? descripcion = freezed,Object? capacidad = null,Object? estado = null,Object? laboratorio = null,Object? tipo = null,Object? esPrestacionServicio = null,Object? requiereApoyoAuxiliar = null,}) {
  return _then(_Recurso(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,tipoRecursoId: null == tipoRecursoId ? _self.tipoRecursoId : tipoRecursoId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: null == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,laboratorio: null == laboratorio ? _self.laboratorio : laboratorio // ignore: cast_nullable_to_non_nullable
as Laboratorio,tipo: null == tipo ? _self.tipo : tipo // ignore: cast_nullable_to_non_nullable
as TipoRecurso,esPrestacionServicio: null == esPrestacionServicio ? _self.esPrestacionServicio : esPrestacionServicio // ignore: cast_nullable_to_non_nullable
as bool,requiereApoyoAuxiliar: null == requiereApoyoAuxiliar ? _self.requiereApoyoAuxiliar : requiereApoyoAuxiliar // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$LaboratorioCopyWith<$Res> get laboratorio {
  
  return $LaboratorioCopyWith<$Res>(_self.laboratorio, (value) {
    return _then(_self.copyWith(laboratorio: value));
  });
}/// Create a copy of Recurso
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TipoRecursoCopyWith<$Res> get tipo {
  
  return $TipoRecursoCopyWith<$Res>(_self.tipo, (value) {
    return _then(_self.copyWith(tipo: value));
  });
}
}

// dart format on

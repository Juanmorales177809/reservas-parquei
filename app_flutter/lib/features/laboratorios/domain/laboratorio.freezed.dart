// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'laboratorio.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Laboratorio {

 int get id; String get nombre; String get ubicacion; int get capacidad; EstadoEntidad get estado; List<int> get diasAtencion; String get horaApertura; String get horaCierre; Map<String, List<int>> get horarioAtencion; int get horasAntelacion; String? get correo;
/// Create a copy of Laboratorio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LaboratorioCopyWith<Laboratorio> get copyWith => _$LaboratorioCopyWithImpl<Laboratorio>(this as Laboratorio, _$identity);

  /// Serializes this Laboratorio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Laboratorio&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&const DeepCollectionEquality().equals(other.diasAtencion, diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other.horarioAtencion, horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion,capacidad,estado,const DeepCollectionEquality().hash(diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(horarioAtencion),horasAntelacion,correo);

@override
String toString() {
  return 'Laboratorio(id: $id, nombre: $nombre, ubicacion: $ubicacion, capacidad: $capacidad, estado: $estado, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, correo: $correo)';
}


}

/// @nodoc
abstract mixin class $LaboratorioCopyWith<$Res>  {
  factory $LaboratorioCopyWith(Laboratorio value, $Res Function(Laboratorio) _then) = _$LaboratorioCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, String ubicacion, int capacidad, EstadoEntidad estado, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, String? correo
});




}
/// @nodoc
class _$LaboratorioCopyWithImpl<$Res>
    implements $LaboratorioCopyWith<$Res> {
  _$LaboratorioCopyWithImpl(this._self, this._then);

  final Laboratorio _self;
  final $Res Function(Laboratorio) _then;

/// Create a copy of Laboratorio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,Object? capacidad = null,Object? estado = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? correo = freezed,}) {
  return _then(Laboratorio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,ubicacion: null == ubicacion ? _self.ubicacion : ubicacion // ignore: cast_nullable_to_non_nullable
as String,capacidad: null == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,diasAtencion: null == diasAtencion ? _self.diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self.horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,correo: freezed == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Laboratorio].
extension LaboratorioPatterns on Laboratorio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Laboratorio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Laboratorio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Laboratorio value)  $default,){
final _that = this;
switch (_that) {
case _Laboratorio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Laboratorio value)?  $default,){
final _that = this;
switch (_that) {
case _Laboratorio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  String? correo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Laboratorio() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.correo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  String? correo)  $default,) {final _that = this;
switch (_that) {
case _Laboratorio():
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.correo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  String? correo)?  $default,) {final _that = this;
switch (_that) {
case _Laboratorio() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.correo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Laboratorio extends Laboratorio {
  const _Laboratorio({required this.id, required this.nombre, required this.ubicacion, required this.capacidad, required this.estado, required  List<int> diasAtencion, required this.horaApertura, required this.horaCierre, required  Map<String, List<int>> horarioAtencion, required this.horasAntelacion, this.correo}): _diasAtencion = diasAtencion,_horarioAtencion = horarioAtencion,super._();
  factory _Laboratorio.fromJson(Map<String, dynamic> json) => _$LaboratorioFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  String ubicacion;
@override final  int capacidad;
@override final  EstadoEntidad estado;
 final  List<int> _diasAtencion;
@override List<int> get diasAtencion {
  if (_diasAtencion is EqualUnmodifiableListView) return _diasAtencion;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_diasAtencion);
}

@override final  String horaApertura;
@override final  String horaCierre;
 final  Map<String, List<int>> _horarioAtencion;
@override Map<String, List<int>> get horarioAtencion {
  if (_horarioAtencion is EqualUnmodifiableMapView) return _horarioAtencion;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_horarioAtencion);
}

@override final  int horasAntelacion;
@override final  String? correo;

/// Create a copy of Laboratorio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LaboratorioCopyWith<_Laboratorio> get copyWith => __$LaboratorioCopyWithImpl<_Laboratorio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LaboratorioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Laboratorio&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&const DeepCollectionEquality().equals(other._diasAtencion, _diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other._horarioAtencion, _horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion,capacidad,estado,const DeepCollectionEquality().hash(_diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(_horarioAtencion),horasAntelacion,correo);

@override
String toString() {
  return 'Laboratorio(id: $id, nombre: $nombre, ubicacion: $ubicacion, capacidad: $capacidad, estado: $estado, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, correo: $correo)';
}


}

/// @nodoc
abstract mixin class _$LaboratorioCopyWith<$Res> implements $LaboratorioCopyWith<$Res> {
  factory _$LaboratorioCopyWith(_Laboratorio value, $Res Function(_Laboratorio) _then) = __$LaboratorioCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, String ubicacion, int capacidad, EstadoEntidad estado, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, String? correo
});




}
/// @nodoc
class __$LaboratorioCopyWithImpl<$Res>
    implements _$LaboratorioCopyWith<$Res> {
  __$LaboratorioCopyWithImpl(this._self, this._then);

  final _Laboratorio _self;
  final $Res Function(_Laboratorio) _then;

/// Create a copy of Laboratorio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,Object? capacidad = null,Object? estado = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? correo = freezed,}) {
  return _then(_Laboratorio(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,ubicacion: null == ubicacion ? _self.ubicacion : ubicacion // ignore: cast_nullable_to_non_nullable
as String,capacidad: null == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,diasAtencion: null == diasAtencion ? _self._diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self._horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,correo: freezed == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on

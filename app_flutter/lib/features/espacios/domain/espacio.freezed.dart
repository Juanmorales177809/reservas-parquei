// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'espacio.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Espacio {

 int get id; String get nombre; String get ubicacion; int get capacidad; EstadoEntidad get estado; List<int> get diasAtencion; String get horaApertura; String get horaCierre; Map<String, List<int>> get horarioAtencion; int get horasAntelacion; ModalidadEspacio get modalidadReserva; String? get correo;
/// Create a copy of Espacio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EspacioCopyWith<Espacio> get copyWith => _$EspacioCopyWithImpl<Espacio>(this as Espacio, _$identity);

  /// Serializes this Espacio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Espacio&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&const DeepCollectionEquality().equals(other.diasAtencion, diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other.horarioAtencion, horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.modalidadReserva, modalidadReserva) || other.modalidadReserva == modalidadReserva)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion,capacidad,estado,const DeepCollectionEquality().hash(diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(horarioAtencion),horasAntelacion,modalidadReserva,correo);

@override
String toString() {
  return 'Espacio(id: $id, nombre: $nombre, ubicacion: $ubicacion, capacidad: $capacidad, estado: $estado, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, modalidadReserva: $modalidadReserva, correo: $correo)';
}


}

/// @nodoc
abstract mixin class $EspacioCopyWith<$Res>  {
  factory $EspacioCopyWith(Espacio value, $Res Function(Espacio) _then) = _$EspacioCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, String ubicacion, int capacidad, EstadoEntidad estado, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, ModalidadEspacio modalidadReserva, String? correo
});




}
/// @nodoc
class _$EspacioCopyWithImpl<$Res>
    implements $EspacioCopyWith<$Res> {
  _$EspacioCopyWithImpl(this._self, this._then);

  final Espacio _self;
  final $Res Function(Espacio) _then;

/// Create a copy of Espacio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,Object? capacidad = null,Object? estado = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? modalidadReserva = null,Object? correo = freezed,}) {
  return _then(Espacio(
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
as int,modalidadReserva: null == modalidadReserva ? _self.modalidadReserva : modalidadReserva // ignore: cast_nullable_to_non_nullable
as ModalidadEspacio,correo: freezed == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [Espacio].
extension EspacioPatterns on Espacio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Espacio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Espacio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Espacio value)  $default,){
final _that = this;
switch (_that) {
case _Espacio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Espacio value)?  $default,){
final _that = this;
switch (_that) {
case _Espacio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  ModalidadEspacio modalidadReserva,  String? correo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Espacio() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.modalidadReserva,_that.correo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  ModalidadEspacio modalidadReserva,  String? correo)  $default,) {final _that = this;
switch (_that) {
case _Espacio():
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.modalidadReserva,_that.correo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  String ubicacion,  int capacidad,  EstadoEntidad estado,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  ModalidadEspacio modalidadReserva,  String? correo)?  $default,) {final _that = this;
switch (_that) {
case _Espacio() when $default != null:
return $default(_that.id,_that.nombre,_that.ubicacion,_that.capacidad,_that.estado,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.modalidadReserva,_that.correo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Espacio extends Espacio {
  const _Espacio({required this.id, required this.nombre, required this.ubicacion, required this.capacidad, required this.estado, required  List<int> diasAtencion, required this.horaApertura, required this.horaCierre, required  Map<String, List<int>> horarioAtencion, required this.horasAntelacion, required this.modalidadReserva, this.correo}): _diasAtencion = diasAtencion,_horarioAtencion = horarioAtencion,super._();
  factory _Espacio.fromJson(Map<String, dynamic> json) => _$EspacioFromJson(json);

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
@override final  ModalidadEspacio modalidadReserva;
@override final  String? correo;

/// Create a copy of Espacio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EspacioCopyWith<_Espacio> get copyWith => __$EspacioCopyWithImpl<_Espacio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EspacioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Espacio&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.ubicacion, ubicacion) || other.ubicacion == ubicacion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&const DeepCollectionEquality().equals(other._diasAtencion, _diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other._horarioAtencion, _horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.modalidadReserva, modalidadReserva) || other.modalidadReserva == modalidadReserva)&&(identical(other.correo, correo) || other.correo == correo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,ubicacion,capacidad,estado,const DeepCollectionEquality().hash(_diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(_horarioAtencion),horasAntelacion,modalidadReserva,correo);

@override
String toString() {
  return 'Espacio(id: $id, nombre: $nombre, ubicacion: $ubicacion, capacidad: $capacidad, estado: $estado, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, modalidadReserva: $modalidadReserva, correo: $correo)';
}


}

/// @nodoc
abstract mixin class _$EspacioCopyWith<$Res> implements $EspacioCopyWith<$Res> {
  factory _$EspacioCopyWith(_Espacio value, $Res Function(_Espacio) _then) = __$EspacioCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, String ubicacion, int capacidad, EstadoEntidad estado, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, ModalidadEspacio modalidadReserva, String? correo
});




}
/// @nodoc
class __$EspacioCopyWithImpl<$Res>
    implements _$EspacioCopyWith<$Res> {
  __$EspacioCopyWithImpl(this._self, this._then);

  final _Espacio _self;
  final $Res Function(_Espacio) _then;

/// Create a copy of Espacio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? ubicacion = null,Object? capacidad = null,Object? estado = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? modalidadReserva = null,Object? correo = freezed,}) {
  return _then(_Espacio(
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
as int,modalidadReserva: null == modalidadReserva ? _self.modalidadReserva : modalidadReserva // ignore: cast_nullable_to_non_nullable
as ModalidadEspacio,correo: freezed == correo ? _self.correo : correo // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on

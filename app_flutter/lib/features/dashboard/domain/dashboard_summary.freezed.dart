// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dashboard_summary.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReservasPorEstado {

 int get pendientes; int get aprobadas; int get rechazadas; int get canceladas;
/// Create a copy of ReservasPorEstado
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservasPorEstadoCopyWith<ReservasPorEstado> get copyWith => _$ReservasPorEstadoCopyWithImpl<ReservasPorEstado>(this as ReservasPorEstado, _$identity);

  /// Serializes this ReservasPorEstado to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservasPorEstado&&(identical(other.pendientes, pendientes) || other.pendientes == pendientes)&&(identical(other.aprobadas, aprobadas) || other.aprobadas == aprobadas)&&(identical(other.rechazadas, rechazadas) || other.rechazadas == rechazadas)&&(identical(other.canceladas, canceladas) || other.canceladas == canceladas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,pendientes,aprobadas,rechazadas,canceladas);

@override
String toString() {
  return 'ReservasPorEstado(pendientes: $pendientes, aprobadas: $aprobadas, rechazadas: $rechazadas, canceladas: $canceladas)';
}


}

/// @nodoc
abstract mixin class $ReservasPorEstadoCopyWith<$Res>  {
  factory $ReservasPorEstadoCopyWith(ReservasPorEstado value, $Res Function(ReservasPorEstado) _then) = _$ReservasPorEstadoCopyWithImpl;
@useResult
$Res call({
 int pendientes, int aprobadas, int rechazadas, int canceladas
});




}
/// @nodoc
class _$ReservasPorEstadoCopyWithImpl<$Res>
    implements $ReservasPorEstadoCopyWith<$Res> {
  _$ReservasPorEstadoCopyWithImpl(this._self, this._then);

  final ReservasPorEstado _self;
  final $Res Function(ReservasPorEstado) _then;

/// Create a copy of ReservasPorEstado
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? pendientes = null,Object? aprobadas = null,Object? rechazadas = null,Object? canceladas = null,}) {
  return _then(ReservasPorEstado(
pendientes: null == pendientes ? _self.pendientes : pendientes // ignore: cast_nullable_to_non_nullable
as int,aprobadas: null == aprobadas ? _self.aprobadas : aprobadas // ignore: cast_nullable_to_non_nullable
as int,rechazadas: null == rechazadas ? _self.rechazadas : rechazadas // ignore: cast_nullable_to_non_nullable
as int,canceladas: null == canceladas ? _self.canceladas : canceladas // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservasPorEstado].
extension ReservasPorEstadoPatterns on ReservasPorEstado {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservasPorEstado value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservasPorEstado() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservasPorEstado value)  $default,){
final _that = this;
switch (_that) {
case _ReservasPorEstado():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservasPorEstado value)?  $default,){
final _that = this;
switch (_that) {
case _ReservasPorEstado() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int pendientes,  int aprobadas,  int rechazadas,  int canceladas)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservasPorEstado() when $default != null:
return $default(_that.pendientes,_that.aprobadas,_that.rechazadas,_that.canceladas);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int pendientes,  int aprobadas,  int rechazadas,  int canceladas)  $default,) {final _that = this;
switch (_that) {
case _ReservasPorEstado():
return $default(_that.pendientes,_that.aprobadas,_that.rechazadas,_that.canceladas);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int pendientes,  int aprobadas,  int rechazadas,  int canceladas)?  $default,) {final _that = this;
switch (_that) {
case _ReservasPorEstado() when $default != null:
return $default(_that.pendientes,_that.aprobadas,_that.rechazadas,_that.canceladas);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservasPorEstado implements ReservasPorEstado {
  const _ReservasPorEstado({required this.pendientes, required this.aprobadas, required this.rechazadas, required this.canceladas});
  factory _ReservasPorEstado.fromJson(Map<String, dynamic> json) => _$ReservasPorEstadoFromJson(json);

@override final  int pendientes;
@override final  int aprobadas;
@override final  int rechazadas;
@override final  int canceladas;

/// Create a copy of ReservasPorEstado
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservasPorEstadoCopyWith<_ReservasPorEstado> get copyWith => __$ReservasPorEstadoCopyWithImpl<_ReservasPorEstado>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservasPorEstadoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservasPorEstado&&(identical(other.pendientes, pendientes) || other.pendientes == pendientes)&&(identical(other.aprobadas, aprobadas) || other.aprobadas == aprobadas)&&(identical(other.rechazadas, rechazadas) || other.rechazadas == rechazadas)&&(identical(other.canceladas, canceladas) || other.canceladas == canceladas));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,pendientes,aprobadas,rechazadas,canceladas);

@override
String toString() {
  return 'ReservasPorEstado(pendientes: $pendientes, aprobadas: $aprobadas, rechazadas: $rechazadas, canceladas: $canceladas)';
}


}

/// @nodoc
abstract mixin class _$ReservasPorEstadoCopyWith<$Res> implements $ReservasPorEstadoCopyWith<$Res> {
  factory _$ReservasPorEstadoCopyWith(_ReservasPorEstado value, $Res Function(_ReservasPorEstado) _then) = __$ReservasPorEstadoCopyWithImpl;
@override @useResult
$Res call({
 int pendientes, int aprobadas, int rechazadas, int canceladas
});




}
/// @nodoc
class __$ReservasPorEstadoCopyWithImpl<$Res>
    implements _$ReservasPorEstadoCopyWith<$Res> {
  __$ReservasPorEstadoCopyWithImpl(this._self, this._then);

  final _ReservasPorEstado _self;
  final $Res Function(_ReservasPorEstado) _then;

/// Create a copy of ReservasPorEstado
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? pendientes = null,Object? aprobadas = null,Object? rechazadas = null,Object? canceladas = null,}) {
  return _then(_ReservasPorEstado(
pendientes: null == pendientes ? _self.pendientes : pendientes // ignore: cast_nullable_to_non_nullable
as int,aprobadas: null == aprobadas ? _self.aprobadas : aprobadas // ignore: cast_nullable_to_non_nullable
as int,rechazadas: null == rechazadas ? _self.rechazadas : rechazadas // ignore: cast_nullable_to_non_nullable
as int,canceladas: null == canceladas ? _self.canceladas : canceladas // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$ReservasPorFecha {

 String get fecha; int get cantidad;
/// Create a copy of ReservasPorFecha
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservasPorFechaCopyWith<ReservasPorFecha> get copyWith => _$ReservasPorFechaCopyWithImpl<ReservasPorFecha>(this as ReservasPorFecha, _$identity);

  /// Serializes this ReservasPorFecha to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservasPorFecha&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,fecha,cantidad);

@override
String toString() {
  return 'ReservasPorFecha(fecha: $fecha, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class $ReservasPorFechaCopyWith<$Res>  {
  factory $ReservasPorFechaCopyWith(ReservasPorFecha value, $Res Function(ReservasPorFecha) _then) = _$ReservasPorFechaCopyWithImpl;
@useResult
$Res call({
 String fecha, int cantidad
});




}
/// @nodoc
class _$ReservasPorFechaCopyWithImpl<$Res>
    implements $ReservasPorFechaCopyWith<$Res> {
  _$ReservasPorFechaCopyWithImpl(this._self, this._then);

  final ReservasPorFecha _self;
  final $Res Function(ReservasPorFecha) _then;

/// Create a copy of ReservasPorFecha
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? fecha = null,Object? cantidad = null,}) {
  return _then(ReservasPorFecha(
fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservasPorFecha].
extension ReservasPorFechaPatterns on ReservasPorFecha {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservasPorFecha value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservasPorFecha() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservasPorFecha value)  $default,){
final _that = this;
switch (_that) {
case _ReservasPorFecha():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservasPorFecha value)?  $default,){
final _that = this;
switch (_that) {
case _ReservasPorFecha() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String fecha,  int cantidad)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservasPorFecha() when $default != null:
return $default(_that.fecha,_that.cantidad);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String fecha,  int cantidad)  $default,) {final _that = this;
switch (_that) {
case _ReservasPorFecha():
return $default(_that.fecha,_that.cantidad);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String fecha,  int cantidad)?  $default,) {final _that = this;
switch (_that) {
case _ReservasPorFecha() when $default != null:
return $default(_that.fecha,_that.cantidad);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservasPorFecha implements ReservasPorFecha {
  const _ReservasPorFecha({required this.fecha, required this.cantidad});
  factory _ReservasPorFecha.fromJson(Map<String, dynamic> json) => _$ReservasPorFechaFromJson(json);

@override final  String fecha;
@override final  int cantidad;

/// Create a copy of ReservasPorFecha
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservasPorFechaCopyWith<_ReservasPorFecha> get copyWith => __$ReservasPorFechaCopyWithImpl<_ReservasPorFecha>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservasPorFechaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservasPorFecha&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,fecha,cantidad);

@override
String toString() {
  return 'ReservasPorFecha(fecha: $fecha, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class _$ReservasPorFechaCopyWith<$Res> implements $ReservasPorFechaCopyWith<$Res> {
  factory _$ReservasPorFechaCopyWith(_ReservasPorFecha value, $Res Function(_ReservasPorFecha) _then) = __$ReservasPorFechaCopyWithImpl;
@override @useResult
$Res call({
 String fecha, int cantidad
});




}
/// @nodoc
class __$ReservasPorFechaCopyWithImpl<$Res>
    implements _$ReservasPorFechaCopyWith<$Res> {
  __$ReservasPorFechaCopyWithImpl(this._self, this._then);

  final _ReservasPorFecha _self;
  final $Res Function(_ReservasPorFecha) _then;

/// Create a copy of ReservasPorFecha
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? fecha = null,Object? cantidad = null,}) {
  return _then(_ReservasPorFecha(
fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$ReservasPorEspacio {

 int get espacioId; String get nombre; int get cantidad;
/// Create a copy of ReservasPorEspacio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReservasPorEspacioCopyWith<ReservasPorEspacio> get copyWith => _$ReservasPorEspacioCopyWithImpl<ReservasPorEspacio>(this as ReservasPorEspacio, _$identity);

  /// Serializes this ReservasPorEspacio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReservasPorEspacio&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,espacioId,nombre,cantidad);

@override
String toString() {
  return 'ReservasPorEspacio(espacioId: $espacioId, nombre: $nombre, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class $ReservasPorEspacioCopyWith<$Res>  {
  factory $ReservasPorEspacioCopyWith(ReservasPorEspacio value, $Res Function(ReservasPorEspacio) _then) = _$ReservasPorEspacioCopyWithImpl;
@useResult
$Res call({
 int espacioId, String nombre, int cantidad
});




}
/// @nodoc
class _$ReservasPorEspacioCopyWithImpl<$Res>
    implements $ReservasPorEspacioCopyWith<$Res> {
  _$ReservasPorEspacioCopyWithImpl(this._self, this._then);

  final ReservasPorEspacio _self;
  final $Res Function(ReservasPorEspacio) _then;

/// Create a copy of ReservasPorEspacio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? espacioId = null,Object? nombre = null,Object? cantidad = null,}) {
  return _then(ReservasPorEspacio(
espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [ReservasPorEspacio].
extension ReservasPorEspacioPatterns on ReservasPorEspacio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReservasPorEspacio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReservasPorEspacio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReservasPorEspacio value)  $default,){
final _that = this;
switch (_that) {
case _ReservasPorEspacio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReservasPorEspacio value)?  $default,){
final _that = this;
switch (_that) {
case _ReservasPorEspacio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int espacioId,  String nombre,  int cantidad)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReservasPorEspacio() when $default != null:
return $default(_that.espacioId,_that.nombre,_that.cantidad);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int espacioId,  String nombre,  int cantidad)  $default,) {final _that = this;
switch (_that) {
case _ReservasPorEspacio():
return $default(_that.espacioId,_that.nombre,_that.cantidad);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int espacioId,  String nombre,  int cantidad)?  $default,) {final _that = this;
switch (_that) {
case _ReservasPorEspacio() when $default != null:
return $default(_that.espacioId,_that.nombre,_that.cantidad);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ReservasPorEspacio implements ReservasPorEspacio {
  const _ReservasPorEspacio({required this.espacioId, required this.nombre, required this.cantidad});
  factory _ReservasPorEspacio.fromJson(Map<String, dynamic> json) => _$ReservasPorEspacioFromJson(json);

@override final  int espacioId;
@override final  String nombre;
@override final  int cantidad;

/// Create a copy of ReservasPorEspacio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReservasPorEspacioCopyWith<_ReservasPorEspacio> get copyWith => __$ReservasPorEspacioCopyWithImpl<_ReservasPorEspacio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReservasPorEspacioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReservasPorEspacio&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,espacioId,nombre,cantidad);

@override
String toString() {
  return 'ReservasPorEspacio(espacioId: $espacioId, nombre: $nombre, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class _$ReservasPorEspacioCopyWith<$Res> implements $ReservasPorEspacioCopyWith<$Res> {
  factory _$ReservasPorEspacioCopyWith(_ReservasPorEspacio value, $Res Function(_ReservasPorEspacio) _then) = __$ReservasPorEspacioCopyWithImpl;
@override @useResult
$Res call({
 int espacioId, String nombre, int cantidad
});




}
/// @nodoc
class __$ReservasPorEspacioCopyWithImpl<$Res>
    implements _$ReservasPorEspacioCopyWith<$Res> {
  __$ReservasPorEspacioCopyWithImpl(this._self, this._then);

  final _ReservasPorEspacio _self;
  final $Res Function(_ReservasPorEspacio) _then;

/// Create a copy of ReservasPorEspacio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? espacioId = null,Object? nombre = null,Object? cantidad = null,}) {
  return _then(_ReservasPorEspacio(
espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$RecursoMasReservado {

 int get recursoId; String get nombre; int get cantidad;
/// Create a copy of RecursoMasReservado
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RecursoMasReservadoCopyWith<RecursoMasReservado> get copyWith => _$RecursoMasReservadoCopyWithImpl<RecursoMasReservado>(this as RecursoMasReservado, _$identity);

  /// Serializes this RecursoMasReservado to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RecursoMasReservado&&(identical(other.recursoId, recursoId) || other.recursoId == recursoId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recursoId,nombre,cantidad);

@override
String toString() {
  return 'RecursoMasReservado(recursoId: $recursoId, nombre: $nombre, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class $RecursoMasReservadoCopyWith<$Res>  {
  factory $RecursoMasReservadoCopyWith(RecursoMasReservado value, $Res Function(RecursoMasReservado) _then) = _$RecursoMasReservadoCopyWithImpl;
@useResult
$Res call({
 int recursoId, String nombre, int cantidad
});




}
/// @nodoc
class _$RecursoMasReservadoCopyWithImpl<$Res>
    implements $RecursoMasReservadoCopyWith<$Res> {
  _$RecursoMasReservadoCopyWithImpl(this._self, this._then);

  final RecursoMasReservado _self;
  final $Res Function(RecursoMasReservado) _then;

/// Create a copy of RecursoMasReservado
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? recursoId = null,Object? nombre = null,Object? cantidad = null,}) {
  return _then(RecursoMasReservado(
recursoId: null == recursoId ? _self.recursoId : recursoId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [RecursoMasReservado].
extension RecursoMasReservadoPatterns on RecursoMasReservado {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RecursoMasReservado value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RecursoMasReservado() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RecursoMasReservado value)  $default,){
final _that = this;
switch (_that) {
case _RecursoMasReservado():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RecursoMasReservado value)?  $default,){
final _that = this;
switch (_that) {
case _RecursoMasReservado() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int recursoId,  String nombre,  int cantidad)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RecursoMasReservado() when $default != null:
return $default(_that.recursoId,_that.nombre,_that.cantidad);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int recursoId,  String nombre,  int cantidad)  $default,) {final _that = this;
switch (_that) {
case _RecursoMasReservado():
return $default(_that.recursoId,_that.nombre,_that.cantidad);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int recursoId,  String nombre,  int cantidad)?  $default,) {final _that = this;
switch (_that) {
case _RecursoMasReservado() when $default != null:
return $default(_that.recursoId,_that.nombre,_that.cantidad);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _RecursoMasReservado implements RecursoMasReservado {
  const _RecursoMasReservado({required this.recursoId, required this.nombre, required this.cantidad});
  factory _RecursoMasReservado.fromJson(Map<String, dynamic> json) => _$RecursoMasReservadoFromJson(json);

@override final  int recursoId;
@override final  String nombre;
@override final  int cantidad;

/// Create a copy of RecursoMasReservado
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RecursoMasReservadoCopyWith<_RecursoMasReservado> get copyWith => __$RecursoMasReservadoCopyWithImpl<_RecursoMasReservado>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RecursoMasReservadoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RecursoMasReservado&&(identical(other.recursoId, recursoId) || other.recursoId == recursoId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,recursoId,nombre,cantidad);

@override
String toString() {
  return 'RecursoMasReservado(recursoId: $recursoId, nombre: $nombre, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class _$RecursoMasReservadoCopyWith<$Res> implements $RecursoMasReservadoCopyWith<$Res> {
  factory _$RecursoMasReservadoCopyWith(_RecursoMasReservado value, $Res Function(_RecursoMasReservado) _then) = __$RecursoMasReservadoCopyWithImpl;
@override @useResult
$Res call({
 int recursoId, String nombre, int cantidad
});




}
/// @nodoc
class __$RecursoMasReservadoCopyWithImpl<$Res>
    implements _$RecursoMasReservadoCopyWith<$Res> {
  __$RecursoMasReservadoCopyWithImpl(this._self, this._then);

  final _RecursoMasReservado _self;
  final $Res Function(_RecursoMasReservado) _then;

/// Create a copy of RecursoMasReservado
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? recursoId = null,Object? nombre = null,Object? cantidad = null,}) {
  return _then(_RecursoMasReservado(
recursoId: null == recursoId ? _self.recursoId : recursoId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$OcupacionDiaHora {

 String get dia; int get diaOrden; int get hora; int get cantidad;
/// Create a copy of OcupacionDiaHora
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OcupacionDiaHoraCopyWith<OcupacionDiaHora> get copyWith => _$OcupacionDiaHoraCopyWithImpl<OcupacionDiaHora>(this as OcupacionDiaHora, _$identity);

  /// Serializes this OcupacionDiaHora to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OcupacionDiaHora&&(identical(other.dia, dia) || other.dia == dia)&&(identical(other.diaOrden, diaOrden) || other.diaOrden == diaOrden)&&(identical(other.hora, hora) || other.hora == hora)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dia,diaOrden,hora,cantidad);

@override
String toString() {
  return 'OcupacionDiaHora(dia: $dia, diaOrden: $diaOrden, hora: $hora, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class $OcupacionDiaHoraCopyWith<$Res>  {
  factory $OcupacionDiaHoraCopyWith(OcupacionDiaHora value, $Res Function(OcupacionDiaHora) _then) = _$OcupacionDiaHoraCopyWithImpl;
@useResult
$Res call({
 String dia, int diaOrden, int hora, int cantidad
});




}
/// @nodoc
class _$OcupacionDiaHoraCopyWithImpl<$Res>
    implements $OcupacionDiaHoraCopyWith<$Res> {
  _$OcupacionDiaHoraCopyWithImpl(this._self, this._then);

  final OcupacionDiaHora _self;
  final $Res Function(OcupacionDiaHora) _then;

/// Create a copy of OcupacionDiaHora
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dia = null,Object? diaOrden = null,Object? hora = null,Object? cantidad = null,}) {
  return _then(OcupacionDiaHora(
dia: null == dia ? _self.dia : dia // ignore: cast_nullable_to_non_nullable
as String,diaOrden: null == diaOrden ? _self.diaOrden : diaOrden // ignore: cast_nullable_to_non_nullable
as int,hora: null == hora ? _self.hora : hora // ignore: cast_nullable_to_non_nullable
as int,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [OcupacionDiaHora].
extension OcupacionDiaHoraPatterns on OcupacionDiaHora {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OcupacionDiaHora value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OcupacionDiaHora() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OcupacionDiaHora value)  $default,){
final _that = this;
switch (_that) {
case _OcupacionDiaHora():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OcupacionDiaHora value)?  $default,){
final _that = this;
switch (_that) {
case _OcupacionDiaHora() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String dia,  int diaOrden,  int hora,  int cantidad)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OcupacionDiaHora() when $default != null:
return $default(_that.dia,_that.diaOrden,_that.hora,_that.cantidad);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String dia,  int diaOrden,  int hora,  int cantidad)  $default,) {final _that = this;
switch (_that) {
case _OcupacionDiaHora():
return $default(_that.dia,_that.diaOrden,_that.hora,_that.cantidad);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String dia,  int diaOrden,  int hora,  int cantidad)?  $default,) {final _that = this;
switch (_that) {
case _OcupacionDiaHora() when $default != null:
return $default(_that.dia,_that.diaOrden,_that.hora,_that.cantidad);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OcupacionDiaHora implements OcupacionDiaHora {
  const _OcupacionDiaHora({required this.dia, required this.diaOrden, required this.hora, required this.cantidad});
  factory _OcupacionDiaHora.fromJson(Map<String, dynamic> json) => _$OcupacionDiaHoraFromJson(json);

@override final  String dia;
@override final  int diaOrden;
@override final  int hora;
@override final  int cantidad;

/// Create a copy of OcupacionDiaHora
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OcupacionDiaHoraCopyWith<_OcupacionDiaHora> get copyWith => __$OcupacionDiaHoraCopyWithImpl<_OcupacionDiaHora>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OcupacionDiaHoraToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OcupacionDiaHora&&(identical(other.dia, dia) || other.dia == dia)&&(identical(other.diaOrden, diaOrden) || other.diaOrden == diaOrden)&&(identical(other.hora, hora) || other.hora == hora)&&(identical(other.cantidad, cantidad) || other.cantidad == cantidad));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dia,diaOrden,hora,cantidad);

@override
String toString() {
  return 'OcupacionDiaHora(dia: $dia, diaOrden: $diaOrden, hora: $hora, cantidad: $cantidad)';
}


}

/// @nodoc
abstract mixin class _$OcupacionDiaHoraCopyWith<$Res> implements $OcupacionDiaHoraCopyWith<$Res> {
  factory _$OcupacionDiaHoraCopyWith(_OcupacionDiaHora value, $Res Function(_OcupacionDiaHora) _then) = __$OcupacionDiaHoraCopyWithImpl;
@override @useResult
$Res call({
 String dia, int diaOrden, int hora, int cantidad
});




}
/// @nodoc
class __$OcupacionDiaHoraCopyWithImpl<$Res>
    implements _$OcupacionDiaHoraCopyWith<$Res> {
  __$OcupacionDiaHoraCopyWithImpl(this._self, this._then);

  final _OcupacionDiaHora _self;
  final $Res Function(_OcupacionDiaHora) _then;

/// Create a copy of OcupacionDiaHora
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dia = null,Object? diaOrden = null,Object? hora = null,Object? cantidad = null,}) {
  return _then(_OcupacionDiaHora(
dia: null == dia ? _self.dia : dia // ignore: cast_nullable_to_non_nullable
as String,diaOrden: null == diaOrden ? _self.diaOrden : diaOrden // ignore: cast_nullable_to_non_nullable
as int,hora: null == hora ? _self.hora : hora // ignore: cast_nullable_to_non_nullable
as int,cantidad: null == cantidad ? _self.cantidad : cantidad // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$OcupacionGlobal {

 double get horasOcupadas; double get horasDisponibles; double get porcentaje;
/// Create a copy of OcupacionGlobal
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OcupacionGlobalCopyWith<OcupacionGlobal> get copyWith => _$OcupacionGlobalCopyWithImpl<OcupacionGlobal>(this as OcupacionGlobal, _$identity);

  /// Serializes this OcupacionGlobal to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OcupacionGlobal&&(identical(other.horasOcupadas, horasOcupadas) || other.horasOcupadas == horasOcupadas)&&(identical(other.horasDisponibles, horasDisponibles) || other.horasDisponibles == horasDisponibles)&&(identical(other.porcentaje, porcentaje) || other.porcentaje == porcentaje));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,horasOcupadas,horasDisponibles,porcentaje);

@override
String toString() {
  return 'OcupacionGlobal(horasOcupadas: $horasOcupadas, horasDisponibles: $horasDisponibles, porcentaje: $porcentaje)';
}


}

/// @nodoc
abstract mixin class $OcupacionGlobalCopyWith<$Res>  {
  factory $OcupacionGlobalCopyWith(OcupacionGlobal value, $Res Function(OcupacionGlobal) _then) = _$OcupacionGlobalCopyWithImpl;
@useResult
$Res call({
 double horasOcupadas, double horasDisponibles, double porcentaje
});




}
/// @nodoc
class _$OcupacionGlobalCopyWithImpl<$Res>
    implements $OcupacionGlobalCopyWith<$Res> {
  _$OcupacionGlobalCopyWithImpl(this._self, this._then);

  final OcupacionGlobal _self;
  final $Res Function(OcupacionGlobal) _then;

/// Create a copy of OcupacionGlobal
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? horasOcupadas = null,Object? horasDisponibles = null,Object? porcentaje = null,}) {
  return _then(OcupacionGlobal(
horasOcupadas: null == horasOcupadas ? _self.horasOcupadas : horasOcupadas // ignore: cast_nullable_to_non_nullable
as double,horasDisponibles: null == horasDisponibles ? _self.horasDisponibles : horasDisponibles // ignore: cast_nullable_to_non_nullable
as double,porcentaje: null == porcentaje ? _self.porcentaje : porcentaje // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [OcupacionGlobal].
extension OcupacionGlobalPatterns on OcupacionGlobal {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OcupacionGlobal value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OcupacionGlobal() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OcupacionGlobal value)  $default,){
final _that = this;
switch (_that) {
case _OcupacionGlobal():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OcupacionGlobal value)?  $default,){
final _that = this;
switch (_that) {
case _OcupacionGlobal() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( double horasOcupadas,  double horasDisponibles,  double porcentaje)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OcupacionGlobal() when $default != null:
return $default(_that.horasOcupadas,_that.horasDisponibles,_that.porcentaje);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( double horasOcupadas,  double horasDisponibles,  double porcentaje)  $default,) {final _that = this;
switch (_that) {
case _OcupacionGlobal():
return $default(_that.horasOcupadas,_that.horasDisponibles,_that.porcentaje);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( double horasOcupadas,  double horasDisponibles,  double porcentaje)?  $default,) {final _that = this;
switch (_that) {
case _OcupacionGlobal() when $default != null:
return $default(_that.horasOcupadas,_that.horasDisponibles,_that.porcentaje);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OcupacionGlobal implements OcupacionGlobal {
  const _OcupacionGlobal({required this.horasOcupadas, required this.horasDisponibles, required this.porcentaje});
  factory _OcupacionGlobal.fromJson(Map<String, dynamic> json) => _$OcupacionGlobalFromJson(json);

@override final  double horasOcupadas;
@override final  double horasDisponibles;
@override final  double porcentaje;

/// Create a copy of OcupacionGlobal
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OcupacionGlobalCopyWith<_OcupacionGlobal> get copyWith => __$OcupacionGlobalCopyWithImpl<_OcupacionGlobal>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OcupacionGlobalToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OcupacionGlobal&&(identical(other.horasOcupadas, horasOcupadas) || other.horasOcupadas == horasOcupadas)&&(identical(other.horasDisponibles, horasDisponibles) || other.horasDisponibles == horasDisponibles)&&(identical(other.porcentaje, porcentaje) || other.porcentaje == porcentaje));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,horasOcupadas,horasDisponibles,porcentaje);

@override
String toString() {
  return 'OcupacionGlobal(horasOcupadas: $horasOcupadas, horasDisponibles: $horasDisponibles, porcentaje: $porcentaje)';
}


}

/// @nodoc
abstract mixin class _$OcupacionGlobalCopyWith<$Res> implements $OcupacionGlobalCopyWith<$Res> {
  factory _$OcupacionGlobalCopyWith(_OcupacionGlobal value, $Res Function(_OcupacionGlobal) _then) = __$OcupacionGlobalCopyWithImpl;
@override @useResult
$Res call({
 double horasOcupadas, double horasDisponibles, double porcentaje
});




}
/// @nodoc
class __$OcupacionGlobalCopyWithImpl<$Res>
    implements _$OcupacionGlobalCopyWith<$Res> {
  __$OcupacionGlobalCopyWithImpl(this._self, this._then);

  final _OcupacionGlobal _self;
  final $Res Function(_OcupacionGlobal) _then;

/// Create a copy of OcupacionGlobal
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? horasOcupadas = null,Object? horasDisponibles = null,Object? porcentaje = null,}) {
  return _then(_OcupacionGlobal(
horasOcupadas: null == horasOcupadas ? _self.horasOcupadas : horasOcupadas // ignore: cast_nullable_to_non_nullable
as double,horasDisponibles: null == horasDisponibles ? _self.horasDisponibles : horasDisponibles // ignore: cast_nullable_to_non_nullable
as double,porcentaje: null == porcentaje ? _self.porcentaje : porcentaje // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}


/// @nodoc
mixin _$DashboardSummary {

 int get totalReservas; int get reservasPendientes; int get recursosActivos; int get usuarios; String? get espacioNombre; ReservasPorEstado get reservasPorEstado; List<ReservasPorFecha> get reservasPorFecha; List<ReservasPorEspacio> get reservasPorEspacio; List<RecursoMasReservado> get recursosMasReservados; List<OcupacionDiaHora> get ocupacionPorDiaHora; OcupacionGlobal get ocupacionGlobal;
/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DashboardSummaryCopyWith<DashboardSummary> get copyWith => _$DashboardSummaryCopyWithImpl<DashboardSummary>(this as DashboardSummary, _$identity);

  /// Serializes this DashboardSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DashboardSummary&&(identical(other.totalReservas, totalReservas) || other.totalReservas == totalReservas)&&(identical(other.reservasPendientes, reservasPendientes) || other.reservasPendientes == reservasPendientes)&&(identical(other.recursosActivos, recursosActivos) || other.recursosActivos == recursosActivos)&&(identical(other.usuarios, usuarios) || other.usuarios == usuarios)&&(identical(other.espacioNombre, espacioNombre) || other.espacioNombre == espacioNombre)&&(identical(other.reservasPorEstado, reservasPorEstado) || other.reservasPorEstado == reservasPorEstado)&&const DeepCollectionEquality().equals(other.reservasPorFecha, reservasPorFecha)&&const DeepCollectionEquality().equals(other.reservasPorEspacio, reservasPorEspacio)&&const DeepCollectionEquality().equals(other.recursosMasReservados, recursosMasReservados)&&const DeepCollectionEquality().equals(other.ocupacionPorDiaHora, ocupacionPorDiaHora)&&(identical(other.ocupacionGlobal, ocupacionGlobal) || other.ocupacionGlobal == ocupacionGlobal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalReservas,reservasPendientes,recursosActivos,usuarios,espacioNombre,reservasPorEstado,const DeepCollectionEquality().hash(reservasPorFecha),const DeepCollectionEquality().hash(reservasPorEspacio),const DeepCollectionEquality().hash(recursosMasReservados),const DeepCollectionEquality().hash(ocupacionPorDiaHora),ocupacionGlobal);

@override
String toString() {
  return 'DashboardSummary(totalReservas: $totalReservas, reservasPendientes: $reservasPendientes, recursosActivos: $recursosActivos, usuarios: $usuarios, espacioNombre: $espacioNombre, reservasPorEstado: $reservasPorEstado, reservasPorFecha: $reservasPorFecha, reservasPorEspacio: $reservasPorEspacio, recursosMasReservados: $recursosMasReservados, ocupacionPorDiaHora: $ocupacionPorDiaHora, ocupacionGlobal: $ocupacionGlobal)';
}


}

/// @nodoc
abstract mixin class $DashboardSummaryCopyWith<$Res>  {
  factory $DashboardSummaryCopyWith(DashboardSummary value, $Res Function(DashboardSummary) _then) = _$DashboardSummaryCopyWithImpl;
@useResult
$Res call({
 int totalReservas, int reservasPendientes, int recursosActivos, int usuarios, String? espacioNombre, ReservasPorEstado reservasPorEstado, List<ReservasPorFecha> reservasPorFecha, List<ReservasPorEspacio> reservasPorEspacio, List<RecursoMasReservado> recursosMasReservados, List<OcupacionDiaHora> ocupacionPorDiaHora, OcupacionGlobal ocupacionGlobal
});


$ReservasPorEstadoCopyWith<$Res> get reservasPorEstado;$OcupacionGlobalCopyWith<$Res> get ocupacionGlobal;

}
/// @nodoc
class _$DashboardSummaryCopyWithImpl<$Res>
    implements $DashboardSummaryCopyWith<$Res> {
  _$DashboardSummaryCopyWithImpl(this._self, this._then);

  final DashboardSummary _self;
  final $Res Function(DashboardSummary) _then;

/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? totalReservas = null,Object? reservasPendientes = null,Object? recursosActivos = null,Object? usuarios = null,Object? espacioNombre = freezed,Object? reservasPorEstado = null,Object? reservasPorFecha = null,Object? reservasPorEspacio = null,Object? recursosMasReservados = null,Object? ocupacionPorDiaHora = null,Object? ocupacionGlobal = null,}) {
  return _then(DashboardSummary(
totalReservas: null == totalReservas ? _self.totalReservas : totalReservas // ignore: cast_nullable_to_non_nullable
as int,reservasPendientes: null == reservasPendientes ? _self.reservasPendientes : reservasPendientes // ignore: cast_nullable_to_non_nullable
as int,recursosActivos: null == recursosActivos ? _self.recursosActivos : recursosActivos // ignore: cast_nullable_to_non_nullable
as int,usuarios: null == usuarios ? _self.usuarios : usuarios // ignore: cast_nullable_to_non_nullable
as int,espacioNombre: freezed == espacioNombre ? _self.espacioNombre : espacioNombre // ignore: cast_nullable_to_non_nullable
as String?,reservasPorEstado: null == reservasPorEstado ? _self.reservasPorEstado : reservasPorEstado // ignore: cast_nullable_to_non_nullable
as ReservasPorEstado,reservasPorFecha: null == reservasPorFecha ? _self.reservasPorFecha : reservasPorFecha // ignore: cast_nullable_to_non_nullable
as List<ReservasPorFecha>,reservasPorEspacio: null == reservasPorEspacio ? _self.reservasPorEspacio : reservasPorEspacio // ignore: cast_nullable_to_non_nullable
as List<ReservasPorEspacio>,recursosMasReservados: null == recursosMasReservados ? _self.recursosMasReservados : recursosMasReservados // ignore: cast_nullable_to_non_nullable
as List<RecursoMasReservado>,ocupacionPorDiaHora: null == ocupacionPorDiaHora ? _self.ocupacionPorDiaHora : ocupacionPorDiaHora // ignore: cast_nullable_to_non_nullable
as List<OcupacionDiaHora>,ocupacionGlobal: null == ocupacionGlobal ? _self.ocupacionGlobal : ocupacionGlobal // ignore: cast_nullable_to_non_nullable
as OcupacionGlobal,
  ));
}
/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReservasPorEstadoCopyWith<$Res> get reservasPorEstado {
  
  return $ReservasPorEstadoCopyWith<$Res>(_self.reservasPorEstado, (value) {
    return _then(_self.copyWith(reservasPorEstado: value));
  });
}/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$OcupacionGlobalCopyWith<$Res> get ocupacionGlobal {
  
  return $OcupacionGlobalCopyWith<$Res>(_self.ocupacionGlobal, (value) {
    return _then(_self.copyWith(ocupacionGlobal: value));
  });
}
}


/// Adds pattern-matching-related methods to [DashboardSummary].
extension DashboardSummaryPatterns on DashboardSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DashboardSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DashboardSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DashboardSummary value)  $default,){
final _that = this;
switch (_that) {
case _DashboardSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DashboardSummary value)?  $default,){
final _that = this;
switch (_that) {
case _DashboardSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int totalReservas,  int reservasPendientes,  int recursosActivos,  int usuarios,  String? espacioNombre,  ReservasPorEstado reservasPorEstado,  List<ReservasPorFecha> reservasPorFecha,  List<ReservasPorEspacio> reservasPorEspacio,  List<RecursoMasReservado> recursosMasReservados,  List<OcupacionDiaHora> ocupacionPorDiaHora,  OcupacionGlobal ocupacionGlobal)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DashboardSummary() when $default != null:
return $default(_that.totalReservas,_that.reservasPendientes,_that.recursosActivos,_that.usuarios,_that.espacioNombre,_that.reservasPorEstado,_that.reservasPorFecha,_that.reservasPorEspacio,_that.recursosMasReservados,_that.ocupacionPorDiaHora,_that.ocupacionGlobal);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int totalReservas,  int reservasPendientes,  int recursosActivos,  int usuarios,  String? espacioNombre,  ReservasPorEstado reservasPorEstado,  List<ReservasPorFecha> reservasPorFecha,  List<ReservasPorEspacio> reservasPorEspacio,  List<RecursoMasReservado> recursosMasReservados,  List<OcupacionDiaHora> ocupacionPorDiaHora,  OcupacionGlobal ocupacionGlobal)  $default,) {final _that = this;
switch (_that) {
case _DashboardSummary():
return $default(_that.totalReservas,_that.reservasPendientes,_that.recursosActivos,_that.usuarios,_that.espacioNombre,_that.reservasPorEstado,_that.reservasPorFecha,_that.reservasPorEspacio,_that.recursosMasReservados,_that.ocupacionPorDiaHora,_that.ocupacionGlobal);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int totalReservas,  int reservasPendientes,  int recursosActivos,  int usuarios,  String? espacioNombre,  ReservasPorEstado reservasPorEstado,  List<ReservasPorFecha> reservasPorFecha,  List<ReservasPorEspacio> reservasPorEspacio,  List<RecursoMasReservado> recursosMasReservados,  List<OcupacionDiaHora> ocupacionPorDiaHora,  OcupacionGlobal ocupacionGlobal)?  $default,) {final _that = this;
switch (_that) {
case _DashboardSummary() when $default != null:
return $default(_that.totalReservas,_that.reservasPendientes,_that.recursosActivos,_that.usuarios,_that.espacioNombre,_that.reservasPorEstado,_that.reservasPorFecha,_that.reservasPorEspacio,_that.recursosMasReservados,_that.ocupacionPorDiaHora,_that.ocupacionGlobal);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DashboardSummary implements DashboardSummary {
  const _DashboardSummary({required this.totalReservas, required this.reservasPendientes, required this.recursosActivos, required this.usuarios, this.espacioNombre, required this.reservasPorEstado, required  List<ReservasPorFecha> reservasPorFecha, required  List<ReservasPorEspacio> reservasPorEspacio, required  List<RecursoMasReservado> recursosMasReservados, required  List<OcupacionDiaHora> ocupacionPorDiaHora, required this.ocupacionGlobal}): _reservasPorFecha = reservasPorFecha,_reservasPorEspacio = reservasPorEspacio,_recursosMasReservados = recursosMasReservados,_ocupacionPorDiaHora = ocupacionPorDiaHora;
  factory _DashboardSummary.fromJson(Map<String, dynamic> json) => _$DashboardSummaryFromJson(json);

@override final  int totalReservas;
@override final  int reservasPendientes;
@override final  int recursosActivos;
@override final  int usuarios;
@override final  String? espacioNombre;
@override final  ReservasPorEstado reservasPorEstado;
 final  List<ReservasPorFecha> _reservasPorFecha;
@override List<ReservasPorFecha> get reservasPorFecha {
  if (_reservasPorFecha is EqualUnmodifiableListView) return _reservasPorFecha;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_reservasPorFecha);
}

 final  List<ReservasPorEspacio> _reservasPorEspacio;
@override List<ReservasPorEspacio> get reservasPorEspacio {
  if (_reservasPorEspacio is EqualUnmodifiableListView) return _reservasPorEspacio;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_reservasPorEspacio);
}

 final  List<RecursoMasReservado> _recursosMasReservados;
@override List<RecursoMasReservado> get recursosMasReservados {
  if (_recursosMasReservados is EqualUnmodifiableListView) return _recursosMasReservados;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recursosMasReservados);
}

 final  List<OcupacionDiaHora> _ocupacionPorDiaHora;
@override List<OcupacionDiaHora> get ocupacionPorDiaHora {
  if (_ocupacionPorDiaHora is EqualUnmodifiableListView) return _ocupacionPorDiaHora;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_ocupacionPorDiaHora);
}

@override final  OcupacionGlobal ocupacionGlobal;

/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DashboardSummaryCopyWith<_DashboardSummary> get copyWith => __$DashboardSummaryCopyWithImpl<_DashboardSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DashboardSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DashboardSummary&&(identical(other.totalReservas, totalReservas) || other.totalReservas == totalReservas)&&(identical(other.reservasPendientes, reservasPendientes) || other.reservasPendientes == reservasPendientes)&&(identical(other.recursosActivos, recursosActivos) || other.recursosActivos == recursosActivos)&&(identical(other.usuarios, usuarios) || other.usuarios == usuarios)&&(identical(other.espacioNombre, espacioNombre) || other.espacioNombre == espacioNombre)&&(identical(other.reservasPorEstado, reservasPorEstado) || other.reservasPorEstado == reservasPorEstado)&&const DeepCollectionEquality().equals(other._reservasPorFecha, _reservasPorFecha)&&const DeepCollectionEquality().equals(other._reservasPorEspacio, _reservasPorEspacio)&&const DeepCollectionEquality().equals(other._recursosMasReservados, _recursosMasReservados)&&const DeepCollectionEquality().equals(other._ocupacionPorDiaHora, _ocupacionPorDiaHora)&&(identical(other.ocupacionGlobal, ocupacionGlobal) || other.ocupacionGlobal == ocupacionGlobal));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,totalReservas,reservasPendientes,recursosActivos,usuarios,espacioNombre,reservasPorEstado,const DeepCollectionEquality().hash(_reservasPorFecha),const DeepCollectionEquality().hash(_reservasPorEspacio),const DeepCollectionEquality().hash(_recursosMasReservados),const DeepCollectionEquality().hash(_ocupacionPorDiaHora),ocupacionGlobal);

@override
String toString() {
  return 'DashboardSummary(totalReservas: $totalReservas, reservasPendientes: $reservasPendientes, recursosActivos: $recursosActivos, usuarios: $usuarios, espacioNombre: $espacioNombre, reservasPorEstado: $reservasPorEstado, reservasPorFecha: $reservasPorFecha, reservasPorEspacio: $reservasPorEspacio, recursosMasReservados: $recursosMasReservados, ocupacionPorDiaHora: $ocupacionPorDiaHora, ocupacionGlobal: $ocupacionGlobal)';
}


}

/// @nodoc
abstract mixin class _$DashboardSummaryCopyWith<$Res> implements $DashboardSummaryCopyWith<$Res> {
  factory _$DashboardSummaryCopyWith(_DashboardSummary value, $Res Function(_DashboardSummary) _then) = __$DashboardSummaryCopyWithImpl;
@override @useResult
$Res call({
 int totalReservas, int reservasPendientes, int recursosActivos, int usuarios, String? espacioNombre, ReservasPorEstado reservasPorEstado, List<ReservasPorFecha> reservasPorFecha, List<ReservasPorEspacio> reservasPorEspacio, List<RecursoMasReservado> recursosMasReservados, List<OcupacionDiaHora> ocupacionPorDiaHora, OcupacionGlobal ocupacionGlobal
});


@override $ReservasPorEstadoCopyWith<$Res> get reservasPorEstado;@override $OcupacionGlobalCopyWith<$Res> get ocupacionGlobal;

}
/// @nodoc
class __$DashboardSummaryCopyWithImpl<$Res>
    implements _$DashboardSummaryCopyWith<$Res> {
  __$DashboardSummaryCopyWithImpl(this._self, this._then);

  final _DashboardSummary _self;
  final $Res Function(_DashboardSummary) _then;

/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? totalReservas = null,Object? reservasPendientes = null,Object? recursosActivos = null,Object? usuarios = null,Object? espacioNombre = freezed,Object? reservasPorEstado = null,Object? reservasPorFecha = null,Object? reservasPorEspacio = null,Object? recursosMasReservados = null,Object? ocupacionPorDiaHora = null,Object? ocupacionGlobal = null,}) {
  return _then(_DashboardSummary(
totalReservas: null == totalReservas ? _self.totalReservas : totalReservas // ignore: cast_nullable_to_non_nullable
as int,reservasPendientes: null == reservasPendientes ? _self.reservasPendientes : reservasPendientes // ignore: cast_nullable_to_non_nullable
as int,recursosActivos: null == recursosActivos ? _self.recursosActivos : recursosActivos // ignore: cast_nullable_to_non_nullable
as int,usuarios: null == usuarios ? _self.usuarios : usuarios // ignore: cast_nullable_to_non_nullable
as int,espacioNombre: freezed == espacioNombre ? _self.espacioNombre : espacioNombre // ignore: cast_nullable_to_non_nullable
as String?,reservasPorEstado: null == reservasPorEstado ? _self.reservasPorEstado : reservasPorEstado // ignore: cast_nullable_to_non_nullable
as ReservasPorEstado,reservasPorFecha: null == reservasPorFecha ? _self._reservasPorFecha : reservasPorFecha // ignore: cast_nullable_to_non_nullable
as List<ReservasPorFecha>,reservasPorEspacio: null == reservasPorEspacio ? _self._reservasPorEspacio : reservasPorEspacio // ignore: cast_nullable_to_non_nullable
as List<ReservasPorEspacio>,recursosMasReservados: null == recursosMasReservados ? _self._recursosMasReservados : recursosMasReservados // ignore: cast_nullable_to_non_nullable
as List<RecursoMasReservado>,ocupacionPorDiaHora: null == ocupacionPorDiaHora ? _self._ocupacionPorDiaHora : ocupacionPorDiaHora // ignore: cast_nullable_to_non_nullable
as List<OcupacionDiaHora>,ocupacionGlobal: null == ocupacionGlobal ? _self.ocupacionGlobal : ocupacionGlobal // ignore: cast_nullable_to_non_nullable
as OcupacionGlobal,
  ));
}

/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReservasPorEstadoCopyWith<$Res> get reservasPorEstado {
  
  return $ReservasPorEstadoCopyWith<$Res>(_self.reservasPorEstado, (value) {
    return _then(_self.copyWith(reservasPorEstado: value));
  });
}/// Create a copy of DashboardSummary
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$OcupacionGlobalCopyWith<$Res> get ocupacionGlobal {
  
  return $OcupacionGlobalCopyWith<$Res>(_self.ocupacionGlobal, (value) {
    return _then(_self.copyWith(ocupacionGlobal: value));
  });
}
}

// dart format on
